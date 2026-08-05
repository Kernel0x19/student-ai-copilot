"""
LangGraph-based Chatbot Agent with Ollama integration for Student AI Copilot.

This agent provides conversational AI capabilities using local Ollama models
with support for RAG (Retrieval-Augmented Generation) using the existing
vector search infrastructure.
"""

import re
from typing import AsyncGenerator, TypedDict, Annotated, List, Optional, Dict, Any
from datetime import datetime

from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, SystemMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_ollama import ChatOllama
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from sqlalchemy.orm import Session

from app.config import get_settings
from app.db.models import ChatMessageRecord, ChatThread, UserMemory, StudentProfile
from app.knowledge.hybrid_rag import HybridRAG

settings = get_settings()


class ChatState(TypedDict):
    """State for the chatbot conversation."""
    messages: Annotated[List[BaseMessage], add_messages]
    user_id: str
    user_profile: Optional[Dict[str, Any]]
    context: Optional[str]
    retrieved_docs: Optional[List[Dict[str, Any]]]
    long_term_memory: str
    db: Any
    student_profile: Optional[StudentProfile]


class ChatbotAgent:
    """
    LangGraph-based chatbot agent with Ollama integration.

    Features:
    - Local LLM inference via Ollama
    - RAG using existing vector search
    - Conversation memory with checkpointer
    - Student profile-aware responses
    """

    def __init__(
        self,
        model_name: Optional[str] = None,
        temperature: Optional[float] = None,
        base_url: Optional[str] = None
    ):
        # Use config settings with optional overrides
        self.model_name = model_name or settings.ollama_model
        self.temperature = temperature if temperature is not None else settings.ollama_temperature
        self.base_url = base_url or settings.ollama_base_url

        # Initialize Ollama LLM
        self.llm = ChatOllama(
            model=self.model_name,
            temperature=self.temperature,
            base_url=self.base_url,
            streaming=True
        )

        # Initialize vector search for RAG
        self.vector_search_available = False
        try:
            self.rag = HybridRAG()
            self.vector_search_available = True
        except Exception:
            self.vector_search_available = False

        # Build the graph
        self.graph = self._build_graph()
        self.app = self.graph.compile()

    def _build_graph(self) -> StateGraph:
        """Build the LangGraph state graph."""
        graph = StateGraph(ChatState)

        # Add nodes
        graph.add_node("retrieve_context", self._retrieve_context)
        graph.add_node("generate_response", self._generate_response)

        # Add edges
        graph.add_edge(START, "retrieve_context")
        graph.add_edge("retrieve_context", "generate_response")
        graph.add_edge("generate_response", END)

        return graph

    async def _retrieve_context(self, state: ChatState) -> ChatState:
        """Retrieve relevant context from vector store using RAG."""
        user_id = state.get("user_id", "")
        messages = state.get("messages", [])

        # Get the latest human message
        latest_human_msg = None
        for msg in reversed(messages):
            if isinstance(msg, HumanMessage):
                latest_human_msg = msg
                break

        if not latest_human_msg:
            return state

        query = latest_human_msg.content

        # Do not attach old scholarship matches to acknowledgements or greetings.
        # With no retrieval context, the model can simply respond courteously.
        if self._is_social_message(query):
            state["context"] = ""
            state["retrieved_docs"] = []
            return state

        # Keep retrieval scoped to education opportunities. General questions are
        # answered by the LLM normally, without irrelevant scholarship cards.
        if not self._needs_opportunity_retrieval(query):
            state["context"] = ""
            state["retrieved_docs"] = []
            return state

        # Retrieve relevant documents if vector search is available
        if self.vector_search_available and query:
            try:
                context_docs = self.rag.retrieve_for_profile(
                    state["db"], query, state.get("student_profile"), limit=5
                )
                state["context"] = self._format_context(context_docs)
                state["retrieved_docs"] = context_docs
            except Exception as e:
                # Log error but continue without context
                print(f"RAG retrieval error: {e}")
                state["context"] = ""
                state["retrieved_docs"] = []

        return state

    @staticmethod
    def _is_social_message(message: str) -> bool:
        """Detect short acknowledgements that do not need scholarship retrieval."""
        normalized = re.sub(r"[^\w\s\u0900-\u097f]", "", message.lower()).strip()
        social_messages = {
            "thanks", "thank you", "thankyou", "thx", "ty", "hello", "hi",
            "धन्यवाद", "धन्यवाद तुम्हाला", "आभार", "धन्यवाद आहे",
        }
        return normalized in social_messages

    @staticmethod
    def _needs_opportunity_retrieval(message: str) -> bool:
        """Return True only for requests that need the opportunities knowledge base."""
        normalized = message.lower()
        opportunity_terms = (
            "scholarship", "scholarships", "scheme", "schemes", "grant", "stipend",
            "fellowship", "internship", "placement", "student aid", "nsp",
            "eligibility", "eligible", "income certificate", "caste certificate",
            "scholarship application", "scholarship form", "शिष्यवृत्ती", "स्कॉलरशिप",
            "छात्रवृत्ति", "वजीफा", "इंटर्नशिप",
        )
        return any(term in normalized for term in opportunity_terms)

    def _format_context(self, docs: List[Dict[str, Any]]) -> str:
        """Format retrieved documents as context for the LLM."""
        if not docs:
            return ""

        context_parts = ["Relevant scholarship/internship opportunities:"]
        for i, doc in enumerate(docs, 1):
            context_parts.append(f"""
{i}. {doc['title']}
   Category: {doc['category']}
   Description: {doc['description'][:200]}...
   Relevance: {doc['relevance_score']:.2f}; Eligibility match: {doc.get('eligibility_score', 0):.2f}
   Deadline: {doc['deadline'] or 'Not specified'}
   Amount: ${doc['amount'] or 'Not specified'}""")

        return "\n".join(context_parts)

    async def _generate_response(self, state: ChatState) -> ChatState:
        """Generate AI response using the LLM with context."""
        messages = state.get("messages", [])
        user_id = state.get("user_id", "")
        user_profile = state.get("user_profile", {})
        context = state.get("context", "")
        long_term_memory = state.get("long_term_memory", "")

        # Build system prompt with student context
        system_prompt = self._build_system_prompt(user_profile, context, long_term_memory)

        # Prepare messages for LLM
        llm_messages = [SystemMessage(content=system_prompt)]

        # Add conversation history (last 10 messages to avoid token limits)
        recent_messages = messages[-10:] if len(messages) > 10 else messages
        llm_messages.extend(recent_messages)

        # Generate response
        try:
            response = await self.llm.ainvoke(llm_messages)

            # Add AI response to messages
            state["messages"] = messages + [response]
        except Exception as e:
            error_msg = AIMessage(content=f"I apologize, but I encountered an error: {str(e)}. Please try again.")
            state["messages"] = messages + [error_msg]

        return state

    def _build_system_prompt(self, user_profile: Dict[str, Any], context: str, long_term_memory: str = "") -> str:
        """Build system prompt with student profile and context."""
        current_date = datetime.now().strftime("%B %d, %Y")

        # Build profile summary
        profile_parts = []
        if user_profile:
            if user_profile.get("full_name"):
                profile_parts.append(f"Name: {user_profile['full_name']}")
            if user_profile.get("college"):
                profile_parts.append(f"College: {user_profile['college']}")
            if user_profile.get("stream"):
                profile_parts.append(f"Stream: {user_profile['stream']}")
            if user_profile.get("year_of_study"):
                profile_parts.append(f"Year: {user_profile['year_of_study']}")
            if user_profile.get("cgpa"):
                profile_parts.append(f"CGPA: {user_profile['cgpa']}")
            if user_profile.get("state"):
                profile_parts.append(f"State: {user_profile['state']}")
            if user_profile.get("category"):
                profile_parts.append(f"Category: {user_profile['category']}")
            if user_profile.get("income_annual"):
                profile_parts.append(f"Annual Income: ₹{user_profile['income_annual']:,}")
            if user_profile.get("skills"):
                profile_parts.append(f"Skills: {', '.join(user_profile['skills'])}")

        profile_str = "\n".join(profile_parts) if profile_parts else "No profile information available"

        system_prompt = f"""You are an AI assistant for the Student Success Copilot platform, helping Indian students find scholarships, internships, and career opportunities.

Current Date: {current_date}

STUDENT PROFILE:
{profile_str}

RELEVANT OPPORTUNITIES (from vector search):
{context if context else "No specific opportunities found for the current query."}

LONG-TERM MEMORY (facts learned in earlier conversations):
{long_term_memory or "No saved chat memories yet."}

YOUR ROLE:
- Be a helpful, general-purpose assistant, similar to a normal chat assistant.
- Answer general questions directly and naturally, not just scholarship questions.
- For scholarship, internship, eligibility, and application questions, use the retrieved opportunities
  to give personalized, actionable guidance.
- Use the retrieved opportunities to give specific, actionable recommendations
- Be encouraging and supportive - many students are first-generation applicants
- If you don't know something, admit it and suggest where to find the information
- Keep responses concise but informative
- Always consider the student's profile when making recommendations
- Understand questions written in English, Hindi, or Marathi (including speech-to-text transcripts).
  Reply in the same language as the student's latest question unless they ask for another language.
- Only call an opportunity "eligible" when it appears in RELEVANT OPPORTUNITIES.
- When opportunities are present, begin with "Based on your profile, you're eligible for"
  and name only those opportunities. Do not invent eligibility.
- For a greeting, thanks, or other short acknowledgement, reply warmly and briefly in the
  student's language. Do not provide scholarship recommendations, application steps, or sources.

GUIDELINES:
1. When recommending opportunities, mention specific names, deadlines, and eligibility criteria
2. Explain WHY an opportunity matches the student's profile
3. Provide step-by-step application guidance when asked
4. For eligibility questions, be specific about requirements
5. Encourage students to apply to multiple opportunities
6. Remind about document preparation (income certificates, caste certificates, transcripts, etc.)
7. Do not redirect general questions back to scholarships. Answer them normally; only use sources
   and application guidance when the student asks about an opportunity-related topic.

Remember: You are a guide, not a decision-maker. Always encourage students to verify details on official websites."""

        return system_prompt

    async def chat(
        self,
        db: Session,
        user_id: str,
        message: str,
        user_profile: Optional[Dict[str, Any]] = None,
        thread_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Process a chat message and return the AI response.

        Args:
            user_id: Unique identifier for the user
            message: User's message
            user_profile: Optional student profile for personalization
            thread_id: Optional thread ID for conversation continuity

        Returns:
            Dict containing response, retrieved docs, and thread info
        """
        thread = self._get_or_create_thread(db, user_id, thread_id, message)
        messages = self._recent_messages(db, thread.id)
        messages.append(HumanMessage(content=message))
        memory = self._long_term_memory(db, user_id)

        # Initial state
        initial_state: ChatState = {
            "messages": messages,
            "user_id": user_id,
            "user_profile": user_profile or {},
            "context": None,
            "retrieved_docs": None,
            "long_term_memory": memory,
            "db": db,
            "student_profile": db.query(StudentProfile).filter_by(user_id=user_id).first(),
        }

        # Run the graph
        result = await self.app.ainvoke(initial_state)

        # Get the AI response (last message)
        final_messages = result.get("messages", [])
        ai_response = None
        for msg in reversed(final_messages):
            if isinstance(msg, AIMessage):
                ai_response = msg.content
                break

        self._save_message_pair(db, thread, message, ai_response or "")
        self._remember(db, user_id, message)
        db.commit()

        return {
            "response": ai_response or "I apologize, but I couldn't generate a response. Please try again.",
            "retrieved_docs": result.get("retrieved_docs", []),
            "thread_id": thread.id,
            "message_count": db.query(ChatMessageRecord).filter_by(thread_id=thread.id).count(),
        }

    async def stream_chat(
        self,
        db: Session,
        user_id: str,
        message: str,
        user_profile: Optional[Dict[str, Any]] = None,
        thread_id: Optional[str] = None,
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """Stream model tokens while persisting the completed turn and thread state."""
        thread = self._get_or_create_thread(db, user_id, thread_id, message)
        messages = self._recent_messages(db, thread.id)
        messages.append(HumanMessage(content=message))
        state: ChatState = {
            "messages": messages,
            "user_id": user_id,
            "user_profile": user_profile or {},
            "context": None,
            "retrieved_docs": None,
            "long_term_memory": self._long_term_memory(db, user_id),
            "db": db,
            "student_profile": db.query(StudentProfile).filter_by(user_id=user_id).first(),
        }
        state = await self._retrieve_context(state)
        prompt = self._build_system_prompt(state["user_profile"], state.get("context") or "", state["long_term_memory"])
        response_text = ""
        try:
            async for chunk in self.llm.astream([SystemMessage(content=prompt), *messages]):
                token = chunk.content if isinstance(chunk.content, str) else ""
                if token:
                    response_text += token
                    yield {"type": "token", "content": token}
            self._save_message_pair(db, thread, message, response_text)
            self._remember(db, user_id, message)
            db.commit()
            yield {
                "type": "done",
                "thread_id": thread.id,
                "retrieved_docs": state.get("retrieved_docs") or [],
                "message_count": db.query(ChatMessageRecord).filter_by(thread_id=thread.id).count(),
            }
        except Exception as exc:
            db.rollback()
            yield {"type": "error", "detail": str(exc)}

    def _get_or_create_thread(self, db: Session, user_id: str, thread_id: Optional[str], first_message: str) -> ChatThread:
        thread = db.query(ChatThread).filter_by(id=thread_id, user_id=user_id).first() if thread_id else None
        if thread:
            return thread
        title = " ".join(first_message.split())[:80] or "New conversation"
        thread = ChatThread(user_id=user_id, title=title)
        db.add(thread)
        db.flush()
        return thread

    def _recent_messages(self, db: Session, thread_id: str, limit: int = 12) -> List[BaseMessage]:
        records = db.query(ChatMessageRecord).filter_by(thread_id=thread_id).order_by(ChatMessageRecord.created_at.desc()).limit(limit).all()
        messages: List[BaseMessage] = []
        for record in reversed(records):
            messages.append(HumanMessage(content=record.content) if record.role == "user" else AIMessage(content=record.content))
        return messages

    def _long_term_memory(self, db: Session, user_id: str) -> str:
        memories = db.query(UserMemory).filter_by(user_id=user_id).order_by(UserMemory.updated_at.desc()).limit(8).all()
        return "\n".join(f"- {memory.content}" for memory in reversed(memories))

    def _remember(self, db: Session, user_id: str, message: str) -> None:
        """Persist explicit preferences/facts without storing every chat message as memory."""
        match = re.search(r"(?:remember that|remember|i prefer|my goal is)\s+(.+)", message, re.IGNORECASE)
        if not match:
            return
        content = match.group(1).strip().rstrip(".")[:500]
        if content and not db.query(UserMemory).filter_by(user_id=user_id, content=content).first():
            db.add(UserMemory(user_id=user_id, content=content, source="chat"))

    def _save_message_pair(self, db: Session, thread: ChatThread, user_message: str, assistant_message: str) -> None:
        db.add_all([
            ChatMessageRecord(thread_id=thread.id, role="user", content=user_message),
            ChatMessageRecord(thread_id=thread.id, role="assistant", content=assistant_message),
        ])
        thread.updated_at = datetime.utcnow()

    async def get_conversation_history(self, db: Session, user_id: str, thread_id: str) -> List[Dict[str, Any]]:
        thread = db.query(ChatThread).filter_by(id=thread_id, user_id=user_id).first()
        if not thread:
            return []
        records = db.query(ChatMessageRecord).filter_by(thread_id=thread.id).order_by(ChatMessageRecord.created_at).all()
        return [{"role": record.role, "content": record.content} for record in records]

    async def clear_conversation(self, db: Session, user_id: str, thread_id: str) -> bool:
        thread = db.query(ChatThread).filter_by(id=thread_id, user_id=user_id).first()
        if not thread:
            return False
        db.query(ChatMessageRecord).filter_by(thread_id=thread.id).delete()
        db.commit()
        return True

    def list_threads(self, db: Session, user_id: str) -> List[Dict[str, Any]]:
        threads = db.query(ChatThread).filter_by(user_id=user_id).order_by(ChatThread.updated_at.desc()).all()
        return [{"id": thread.id, "title": thread.title, "updated_at": thread.updated_at.isoformat()} for thread in threads]


# Singleton instance
_chatbot_agent: Optional[ChatbotAgent] = None


def get_chatbot_agent() -> ChatbotAgent:
    """Get or create the singleton chatbot agent instance."""
    global _chatbot_agent
    if _chatbot_agent is None:
        _chatbot_agent = ChatbotAgent()
    return _chatbot_agent


# Convenience function for direct use
async def chat_with_bot(
    db: Session,
    user_id: str,
    message: str,
    user_profile: Optional[Dict[str, Any]] = None,
    thread_id: Optional[str] = None
) -> Dict[str, Any]:
    """Convenience function to chat with the bot."""
    agent = get_chatbot_agent()
    return await agent.chat(db, user_id, message, user_profile, thread_id)


# ---------------------------------------------------------------------------
# Eval-only function — NOT used by any production endpoint.
# Returns both the answer and the raw retrieved context chunks so that
# offline evaluation frameworks (Ragas, DeepEval) can score them.
# The production chat API shape is left completely unchanged.
# ---------------------------------------------------------------------------

async def query_scholarship_with_context(question: str) -> Dict[str, Any]:
    """
    Stateless eval entry-point for the Scholarship RAG pipeline.

    Runs a single question through retrieval + generation and returns:
        {
            "answer":   str,          # generated response
            "contexts": list[str],    # raw text of each retrieved chunk
        }

    Uses its own short-lived DB session (same pattern as run_ingestion) so
    it can be called from eval scripts without an active HTTP request context.
    Does NOT persist any chat history or memory.
    """
    from app.db.session import SessionLocal  # imported here to avoid circular imports at module load
    from app.db.models import Opportunity as Opp

    db = SessionLocal()
    try:
        agent = ChatbotAgent()

        # --- Retrieval (bypass eligibility filter for eval) ---
        # retrieve_for_profile filters out docs when profile=None because
        # evaluate_eligibility returns eligible=False for anonymous users.
        # For eval we always want real context, so we use semantic_search directly.
        candidates = agent.rag.semantic_search(question, limit=5, category="scholarship")
        ids = [item["opportunity_id"] for item in candidates if item.get("opportunity_id")]
        opportunities: Dict[str, Any] = {
            opp.id: opp for opp in db.query(Opp).filter(
                Opp.id.in_(ids), Opp.is_active.is_(True)
            ).all()
        } if ids else {}

        retrieved_docs: List[Dict[str, Any]] = []
        for candidate in candidates:
            opp = opportunities.get(candidate.get("opportunity_id"))
            if not opp:
                continue
            retrieved_docs.append({
                "opportunity_id": opp.id,
                "title": opp.title,
                "description": opp.description or "",
                "category": opp.category.value if opp.category else "scholarship",
                "relevance_score": candidate["score"],
                "deadline": opp.deadline.isoformat() if opp.deadline else None,
                "amount": opp.amount_max or opp.amount_min,
            })

        # Build raw context strings for Ragas
        contexts: List[str] = []
        for doc in retrieved_docs:
            parts = [doc.get("title", "")]
            if doc.get("description"):
                parts.append(doc["description"])
            if doc.get("deadline"):
                parts.append(f"Deadline: {doc['deadline']}")
            if doc.get("amount"):
                parts.append(f"Amount: {doc['amount']}")
            contexts.append(" | ".join(p for p in parts if p))

        if not contexts:
            contexts = ["No context retrieved."]

        # --- Context string for generation ---
        context_parts = ["Relevant scholarship opportunities:"]
        for i, doc in enumerate(retrieved_docs, 1):
            context_parts.append(
                f"{i}. {doc['title']}\n"
                f"   Description: {doc['description'][:300]}\n"
                f"   Deadline: {doc['deadline'] or 'Not specified'}\n"
                f"   Amount: {doc['amount'] or 'Not specified'}"
            )
        context_str = "\n".join(context_parts) if retrieved_docs else ""

        # --- Generation ---
        system_prompt = agent._build_system_prompt({}, context_str, "")
        llm_messages = [SystemMessage(content=system_prompt), HumanMessage(content=question)]
        try:
            response = await agent.llm.ainvoke(llm_messages)
            answer: str = response.content if isinstance(response.content, str) else str(response.content)
        except Exception as exc:
            answer = f"[eval error: {exc}]"

        return {"answer": answer, "contexts": contexts}
    finally:
        db.close()


