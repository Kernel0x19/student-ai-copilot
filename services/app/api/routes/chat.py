"""Chat API routes for the AI Chatbot."""

import json
import uuid
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db
from app.db.models import StudentProfile, User, Document
from app.agents import get_chatbot_agent, chat_with_bot
from app.agents.document_identifier import DOCUMENT_TYPES, DocumentIdentifier
from app.config import get_settings
from app.security.document_store import DocumentStore
from app.security.tee import create_tee_service
from app.verification.ocr_service import OCRService, OCRProvider

router = APIRouter(prefix="/chat", tags=["chat"])


class ChatMessage(BaseModel):
    """Single chat message."""
    role: str = Field(..., description="Role: 'user' or 'assistant'")
    content: str = Field(..., description="Message content")


class ChatRequest(BaseModel):
    """Request to send a message to the chatbot."""
    message: str = Field(..., description="User message")
    thread_id: Optional[str] = Field(None, description="Conversation thread ID (optional)")
    user_profile: Optional[Dict[str, Any]] = Field(None, description="Optional user profile context")


class ChatResponse(BaseModel):
    """Response from the chatbot."""
    response: str = Field(..., description="Assistant response")
    thread_id: str = Field(..., description="Conversation thread ID")
    retrieved_docs: List[Dict[str, Any]] = Field(default_factory=list, description="Retrieved documents")
    message_count: int = Field(..., description="Total messages in conversation")


class ConversationHistoryResponse(BaseModel):
    """Response with conversation history."""
    thread_id: str
    history: List[ChatMessage]


def _profile_context(profile: StudentProfile | None) -> Optional[Dict[str, Any]]:
    if not profile:
        return None
    return {
        "full_name": profile.full_name, "state": profile.state,
        "category": profile.category, "income_annual": profile.income_annual,
        "college": profile.college, "stream": profile.stream, "degree": profile.degree,
        "year_of_study": profile.year_of_study, "cgpa": profile.cgpa,
        "percentage_12th": profile.percentage_12th, "skills": profile.skills,
    }


@router.post("/", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Send a message to the AI chatbot and get a response.

    The chatbot uses Ollama + LangChain + LangGraph for RAG-powered conversations
    about scholarships, eligibility, and student guidance.
    """
    try:
        # Get user profile for context if not provided
        user_profile = request.user_profile
        if user_profile is None:
            profile = db.query(StudentProfile).filter_by(user_id=current_user.id).first()
            user_profile = _profile_context(profile)

        result = await chat_with_bot(
            db=db,
            user_id=current_user.id,
            message=request.message,
            user_profile=user_profile,
            thread_id=request.thread_id
        )

        return ChatResponse(
            response=result["response"],
            thread_id=result["thread_id"],
            retrieved_docs=result.get("retrieved_docs") or [],
            message_count=result.get("message_count", 0)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Chat error: {str(e)}"
        )


@router.post("/upload", response_model=ChatResponse)
async def upload_in_chat(
    file: UploadFile = File(...),
    message: str = Form(""),
    thread_id: Optional[str] = Form(None),
    attach_to_profile: bool = Form(True),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Securely classify a document uploaded from chat and optionally attach it to the profile."""
    if file.size is not None and file.size > 10 * 1024 * 1024:
        raise HTTPException(status_code=413, detail="Documents must be 10 MB or smaller")
    content = await file.read()
    if not content:
        raise HTTPException(status_code=400, detail="Empty file contents")
    if len(content) > 10 * 1024 * 1024:
        raise HTTPException(status_code=413, detail="Documents must be 10 MB or smaller")

    try:
        # Pass encrypted upload bytes through the TEE before OCR. The mock mirrors
        # this flow locally; production implementations keep the operation enclave-bound.
        tee = create_tee_service(get_settings().tee_mode)
        tee.process_in_enclave("chat_document_intake", {"filename": file.filename or "upload", "size": len(content)})
        tee_encrypted = tee.encrypt_sensitive(content, "document")
        secure_content = await tee.process_secure(tee_encrypted, "decrypt")
        ocr_result = await OCRService(provider=OCRProvider.TESSERACT).extract_text(secure_content)
        identified = await DocumentIdentifier().identify(ocr_result.get("text", ""))
        doc_type = identified["document_type"]
        document_id = f"doc-{uuid.uuid4().hex[:12]}"
        encrypted_path = DocumentStore(db).store_encrypted_document(document_id, secure_content)

        document = Document(
            id=document_id, user_id=current_user.id, document_type=doc_type,
            file_path=encrypted_path, encryption_key_id=f"kdf-{document_id}",
            verification_status="pending", overall_confidence=identified["confidence"],
            extracted_fields={"classification_method": identified["method"], "filename": file.filename or "upload"},
            field_confidences={"document_type": identified["confidence"]},
            gov_verification_status="not_applicable",
        )
        db.add(document)
        profile = db.query(StudentProfile).filter_by(user_id=current_user.id).first()
        if attach_to_profile and not profile:
            profile = StudentProfile(user_id=current_user.id)
            db.add(profile)
        if attach_to_profile:
            documents = list(profile.documents or [])
            documents.append({"id": document_id, "type": doc_type, "filename": file.filename or "upload", "attached_at": datetime.utcnow().isoformat()})
            profile.documents = documents
        db.commit()
    except HTTPException:
        raise
    except Exception as exc:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Document processing error: {str(exc)}")

    label = DOCUMENT_TYPES[doc_type]
    acknowledgement = f"You uploaded your {label}."
    if attach_to_profile:
        acknowledgement += " It has been securely attached to your profile."
    if message.strip():
        result = await chat_with_bot(
            db=db, user_id=current_user.id, message=message.strip(),
            user_profile=_profile_context(profile), thread_id=thread_id,
        )
        response = f"{acknowledgement}\n\n{result['response']}"
        return ChatResponse(response=response, thread_id=result["thread_id"], retrieved_docs=result.get("retrieved_docs") or [], message_count=result.get("message_count", 0))
    return ChatResponse(response=acknowledgement, thread_id=thread_id or "", retrieved_docs=[], message_count=0)

@router.post("/stream")
async def stream_chat(
    request: ChatRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Server-sent event stream for incremental chat tokens."""
    agent = get_chatbot_agent()

    async def event_stream():
        async for event in agent.stream_chat(
            db=db,
            user_id=current_user.id,
            message=request.message,
            user_profile=request.user_profile or _profile_context(
                db.query(StudentProfile).filter_by(user_id=current_user.id).first()
            ),
            thread_id=request.thread_id,
        ):
            yield f"data: {json.dumps(event)}\n\n"

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "Connection": "keep-alive"},
    )


@router.get("/history/{thread_id}", response_model=ConversationHistoryResponse)
async def get_chat_history(
    thread_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get conversation history for a thread."""
    agent = get_chatbot_agent()
    history = await agent.get_conversation_history(db, current_user.id, thread_id)

    messages = [
        ChatMessage(role=msg["role"], content=msg["content"])
        for msg in history
    ]

    return ConversationHistoryResponse(
        thread_id=thread_id,
        history=messages
    )


@router.delete("/history/{thread_id}")
async def clear_chat_history(
    thread_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Clear conversation history for a thread."""
    agent = get_chatbot_agent()
    success = await agent.clear_conversation(db, current_user.id, thread_id)

    if success:
        return {"message": "Conversation history cleared", "thread_id": thread_id}
    else:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to clear conversation history"
        )


@router.get("/threads")
async def list_chat_threads(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """List the signed-in user's persistent conversation threads."""
    return {"threads": get_chatbot_agent().list_threads(db, current_user.id)}


@router.get("/health")
async def chat_health():
    """Health check for chat service."""
    return {
        "status": "ok",
        "service": "chatbot",
        "model": "ollama (llama3.1)",
        "framework": "langchain + langgraph"
    }
