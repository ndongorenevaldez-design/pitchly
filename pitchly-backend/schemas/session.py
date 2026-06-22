from pydantic import BaseModel, Field


class SessionCreate(BaseModel):
    # Responsibility: Validate session analysis requests.
    mode: str = Field(pattern="^(interview|social)$")
    job_title: str | None = Field(default=None, max_length=120)
    scenario: str | None = Field(default=None, max_length=120)
    duration_s: int = Field(default=120, ge=30, le=300)


class SessionStatus(BaseModel):
    # Responsibility: Shape polling status responses.
    job_id: str
    status: str
    session_id: str | None = None
    error: str | None = None
