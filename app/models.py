from datetime import datetime

from sqlmodel import Field, SQLModel


class Ticket(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    customer_name: str = Field(index=True, max_length=120)
    customer_email: str | None = Field(default=None, index=True, max_length=255)
    subject: str = Field(index=True, max_length=200)
    message: str
    source: str = Field(default="form", index=True, max_length=30)
    customer_tier: str = Field(default="standard", index=True, max_length=30)

    category: str = Field(index=True, max_length=40)
    priority: str = Field(index=True, max_length=20)
    priority_score: int = Field(index=True)
    sentiment: str = Field(index=True, max_length=20)
    assigned_team: str = Field(index=True, max_length=60)
    suggested_reply: str
    next_action: str
    status: str = Field(default="open", index=True, max_length=30)

    created_at: datetime = Field(default_factory=datetime.utcnow, index=True)
    updated_at: datetime = Field(default_factory=datetime.utcnow, index=True)
