from sqlmodel import Field, SQLModel
from pydantic import EmailStr, field_validator
from typing import Optional
from datetime import datetime

# What the user sends in (no id, no timestamp)
class SignupBase(SQLModel):
    first_name: str
    last_name: str
    email: EmailStr
    is_test: bool = Field(default=False)

    @field_validator('first_name')
    @classmethod
    def first_name_must_not_be_empty(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError('First name cannot be empty')
        return v

# What actually gets stored in the database
class Signup(SignupBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)


# ── INCIDENT MODELS ──────────────────────────────────────────────────────────

class IncidentBase(SQLModel):
    lake: str
    incident_date: Optional[datetime] = None
    location_description: str
    location_lat: Optional[float] = None
    location_lng: Optional[float] = None
    description: str
    photo_url: Optional[str] = None
    reporter_name: Optional[str] = None
    reporter_email: Optional[str] = None
    status: str = Field(default="pending")

class IncidentLitter(IncidentBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)

class IncidentLitterCreate(IncidentBase):
    pass

class IncidentWildlife(IncidentBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    species: Optional[str] = None
    condition: str  # entangled, injured, dead, distress

class IncidentWildlifeCreate(IncidentBase):
    species: Optional[str] = None
    condition: str

class IncidentWaterQuality(IncidentBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    observation_type: str  # algae, discoloration, odor, pollution, other

class IncidentWaterQualityCreate(IncidentBase):
    observation_type: str