"""
Domain models for Represent App
"""

from datetime import datetime
from uuid import UUID, uuid4
from typing import Optional
from aws_lambda_powertools.utilities.parser import BaseModel, Field, validator


class Representative(BaseModel):
    """Model for a political representative"""

    id: str = Field(default_factory=lambda: str(uuid4()))
    name: str
    position: str  # e.g., "Senator", "Representative"
    district: Optional[str] = None
    state: str
    party: Optional[str] = None
    contact_info: Optional[dict] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    @validator("id")
    def validate_id(cls, v: str) -> str:
        """Validate UUID format"""
        try:
            UUID(v)
        except ValueError:
            v = str(uuid4())
        return v

    class Config:
        """Pydantic configuration"""

        json_encoders = {datetime: lambda v: v.isoformat()}
