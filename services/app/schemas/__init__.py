from datetime import date, datetime
from enum import Enum

from pydantic import BaseModel, Field


class UserRole(str, Enum):
    STUDENT = "student"
    REVIEWER = "reviewer"
    ADMIN = "admin"


class OpportunityCategory(str, Enum):
    SCHOLARSHIP = "scholarship"
    INTERNSHIP = "internship"
    PLACEMENT = "placement"
    HACKATHON = "hackathon"


class ApplicationState(str, Enum):
    DISCOVERED = "discovered"
    ELIGIBILITY_CHECK = "eligibility_check"
    DOCUMENT_VALIDATION = "document_validation"
    HUMAN_REVIEW = "human_review"
    SUBMITTED = "submitted"
    TRACKING = "tracking"
    COMPLETED = "completed"
    REJECTED = "rejected"


class StudentProfileCreate(BaseModel):
    full_name: str | None = None
    date_of_birth: date | None = None
    gender: str | None = None
    phone: str | None = None
    state: str | None = None
    district: str | None = None
    category: str | None = None
    income_annual: float | None = None
    college: str | None = None
    university: str | None = None
    stream: str | None = None
    degree: str | None = None
    year_of_study: int | None = None
    cgpa: float | None = None
    percentage_12th: float | None = None
    backlogs: int | None = None
    skills: list[str] = Field(default_factory=list)
    documents: list[dict] = Field(default_factory=list)
    # preferences stores: work_mode, pref_duration, availability,
    # pref_locations, interests, resume_url, portfolio_url, cover_letter_url
    preferences: dict = Field(default_factory=dict)


class StudentProfileResponse(StudentProfileCreate):
    id: str
    user_id: str
    readiness_score: float
    updated_at: datetime

    model_config = {"from_attributes": True}


class OpportunityResponse(BaseModel):
    id: str
    source: str
    category: OpportunityCategory
    title: str
    description: str | None
    amount_min: float | None
    amount_max: float | None
    deadline: date | None
    eligibility_rules: dict
    documents_required: list[str]
    application_url: str | None
    state_filter: list[str]
    tags: list[str]
    raw_data: dict | None = None

    model_config = {"from_attributes": True}


class MatchResult(BaseModel):
    opportunity: OpportunityResponse
    match_score: float
    eligibility: dict
    reasons: list[str]


class RecommendationResponse(BaseModel):
    matches: list[MatchResult]
    total: int
    readiness_score: float


class ConsentUpdate(BaseModel):
    purpose: str
    granted: bool


class ConsentResponse(BaseModel):
    purpose: str
    granted: bool
    granted_at: datetime | None

    model_config = {"from_attributes": True}


class ApplicationCreate(BaseModel):
    opportunity_id: str
    saved: bool = False


class ApplicationResponse(BaseModel):
    id: str
    opportunity_id: str
    state: ApplicationState
    match_score: float
    eligibility_result: dict | None
    checklist: list[dict]
    progress_pct: int
    saved: bool
    opportunity: OpportunityResponse | None = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class WorkflowTransitionRequest(BaseModel):
    to_state: ApplicationState
    notes: str | None = None


class NotificationResponse(BaseModel):
    id: str
    title: str
    body: str
    channel: str
    read: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class DashboardStats(BaseModel):
    scholarships_matched: int
    internships_available: int
    documents_uploaded: int
    applications_tracked: int
    readiness_score: float


class SearchRequest(BaseModel):
    query: str
    category: OpportunityCategory | None = OpportunityCategory.SCHOLARSHIP
    state: str | None = None
    limit: int = 20
