# Responsibility: Pydantic schemas for session request/response validation

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


class SessionCreate(BaseModel):
    """Payload sent by the frontend when starting a new session."""

    mode: Literal["interview", "social"] = Field(
        ...,
        description="Training mode — interview or social",
    )
    job_title: str | None = Field(
        default=None,
        max_length=150,
        description="Target job title — required for interview mode",
    )
    scenario: str | None = Field(
        default=None,
        max_length=150,
        description="Social scenario — required for social mode",
    )
    duration_s: int | None = Field(
        default=None,
        ge=10,
        le=300,
        description="Intended session duration in seconds",
    )


class SessionResponse(BaseModel):
    """Response returned after creating a session."""

    session_id: str
    job_id: str
    status: str = "processing"


class JobStatusResponse(BaseModel):
    """Response returned when polling job status."""

    job_id: str
    status: Literal["processing", "complete", "error"]
    session_id: str | None = None
    error: str | None = None