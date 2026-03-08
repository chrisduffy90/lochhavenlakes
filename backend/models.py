from sqlmodel import Field, SQLModel
from typing import Optional
from datetime import datetime

# What the user sends in (no id, no timestamp)
class SignupBase(SQLModel):
    name: str
    email: str

# What actually gets stored in the database
class Signup(SignupBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)