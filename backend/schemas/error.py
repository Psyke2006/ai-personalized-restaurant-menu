from datetime import datetime, timezone
from pydantic import BaseModel, Field

class ErrorDetail(BaseModel):
    code: str
    message: str
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

class ErrorResponse(BaseModel):
    error: ErrorDetail
