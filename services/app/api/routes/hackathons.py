"""Hackathon Finder API routes.

Plain browse/filter feature — no eligibility or matching logic.
Mirrors the structure of internships.py but much simpler (no applications,
no match scores, no workflow).

Endpoints:
  GET /api/v1/hackathons          — paginated + filtered listing
  GET /api/v1/hackathons/{id}     — single hackathon detail
"""

from __future__ import annotations

from datetime import date
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.agents.hackathon import HackathonAgent
from app.api.deps import get_current_user
from app.db.models import Hackathon, User
from app.db.session import get_db

router = APIRouter(prefix="/hackathons", tags=["hackathons"])
_agent = HackathonAgent()


# ── Pydantic response schema ──────────────────────────────────────────────────

class HackathonResponse(BaseModel):
    id: str
    source: str
    title: str
    organizer: Optional[str]
    mode: str
    location: Optional[str]
    team_size: Optional[str]
    prize_pool: int
    registration_deadline: Optional[date]
    start_date: Optional[date]
    end_date: Optional[date]
    themes: list[str]
    apply_link: Optional[str]
    posted_date: Optional[date]

    model_config = {"from_attributes": True}

    # Ensure themes is always a list even when stored as None
    @classmethod
    def from_orm_safe(cls, h: Hackathon) -> "HackathonResponse":
        return cls(
            id=h.id,
            source=h.source,
            title=h.title,
            organizer=h.organizer or "",
            mode=h.mode or "online",
            location=h.location or "",
            team_size=h.team_size or "",
            prize_pool=h.prize_pool or 0,
            registration_deadline=h.registration_deadline,
            start_date=h.start_date,
            end_date=h.end_date,
            themes=h.themes or [],
            apply_link=h.apply_link or "",
            posted_date=h.posted_date,
        )


class HackathonListResponse(BaseModel):
    items: list[HackathonResponse]
    total: int


# ── Routes ────────────────────────────────────────────────────────────────────

@router.get("", response_model=HackathonListResponse)
def list_hackathons(
    query:         Optional[str] = Query(None, description="Search title, organizer, themes"),
    mode:          Optional[str] = Query(None, description="online | offline | hybrid"),
    source:        Optional[str] = Query(None, description="Platform slug (devfolio, mlh, …)"),
    theme:         Optional[str] = Query(None, description="Theme substring filter"),
    prize_min:     Optional[int] = Query(None, description="Minimum prize pool in ₹"),
    location:      Optional[str] = Query(None, description="Location substring filter"),
    deadline_days: Optional[int] = Query(None, description="Show only hackathons with deadline within N days"),
    limit:         int           = Query(60,  ge=1, le=200),
    offset:        int           = Query(0,   ge=0),
    user: User    = Depends(get_current_user),
    db:   Session = Depends(get_db),
):
    result = _agent.list(
        db,
        query=query,
        mode=mode,
        source=source,
        theme=theme,
        prize_min=prize_min,
        location=location,
        deadline_days=deadline_days,
        limit=limit,
        offset=offset,
    )
    return HackathonListResponse(
        items=[HackathonResponse.from_orm_safe(h) for h in result["items"]],
        total=result["total"],
    )


@router.get("/{hackathon_id}", response_model=HackathonResponse)
def get_hackathon(
    hackathon_id: str,
    user: User    = Depends(get_current_user),
    db:   Session = Depends(get_db),
):
    h = db.query(Hackathon).filter_by(id=hackathon_id, is_active=True).first()
    if not h:
        raise HTTPException(status_code=404, detail="Hackathon not found")
    return HackathonResponse.from_orm_safe(h)
