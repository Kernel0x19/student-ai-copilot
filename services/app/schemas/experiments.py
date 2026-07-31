"""Pydantic schemas for A/B testing experiments"""

from datetime import datetime
from typing import Dict, Any, List, Optional

from pydantic import BaseModel, Field


class VariantConfig(BaseModel):
    """Configuration for an experiment variant"""
    name: str = Field(..., description="Variant name (e.g., 'control', 'treatment_a')")
    config: Dict[str, Any] = Field(default_factory=dict, description="Variant-specific configuration")


class ExperimentCreate(BaseModel):
    """Schema for creating a new experiment"""
    experiment_name: str = Field(..., description="Unique experiment identifier")
    variants: List[VariantConfig] = Field(..., min_length=2, description="List of variants (must have at least 2)")


class ExperimentVariantResponse(BaseModel):
    """Response schema for experiment variant"""
    id: str
    experiment_name: str
    variant_name: str
    is_active: bool
    config: Dict[str, Any]
    created_at: datetime

    class Config:
        from_attributes = True


class UserAssignmentResponse(BaseModel):
    """Response schema for user variant assignment"""
    user_id: str
    experiment_name: str
    variant_name: str
    assigned_at: datetime


class VariantMetrics(BaseModel):
    """Metrics for a single variant"""
    users: int
    total_interactions: int
    conversion_rate: float
    engagement_rate: float
    application_rate: float
    relevance_score: float
    breakdown: Dict[str, int]


class ExperimentMetricsResponse(BaseModel):
    """Response schema for experiment metrics"""
    experiment_name: str
    period: Dict[str, str]
    variants: Dict[str, VariantMetrics]


class VariantComparison(BaseModel):
    """Comparison between control and treatment variant"""
    variant: str
    lifts: Dict[str, Dict[str, Any]]


class ExperimentComparisonResponse(BaseModel):
    """Response schema for variant comparison"""
    experiment_name: str
    control_variant: str
    period: Dict[str, str]
    comparisons: Dict[str, VariantComparison]


class ExperimentSummary(BaseModel):
    """High-level experiment summary"""
    experiment_name: str
    total_users: int
    total_feedback: int
    variant_distribution: Dict[str, int]


class PromoteVariantRequest(BaseModel):
    """Request to promote a winning variant to default"""
    winning_variant: str = Field(..., description="Name of the variant to promote")


class PromoteVariantResponse(BaseModel):
    """Response after promoting variant"""
    experiment_name: str
    winning_variant: str
    config: Dict[str, Any]
    message: str

