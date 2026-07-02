from datetime import datetime
from typing import Literal

from pydantic import field_validator
from sqlmodel import Field, SQLModel


TicketSource = Literal["email", "chat", "form", "whatsapp"]
CustomerTier = Literal["standard", "premium", "vip"]
TicketStatus = Literal["open", "in_progress", "waiting_customer", "resolved", "closed"]
TicketCategory = Literal["billing", "technical", "sales", "account", "general"]
TicketPriority = Literal["low", "medium", "high", "urgent"]
TicketSentiment = Literal["negative", "neutral", "positive"]


class TicketCreate(SQLModel):
    customer_name: str = Field(min_length=1, max_length=120)
    customer_email: str | None = Field(default=None, max_length=255)
    subject: str = Field(min_length=1, max_length=200)
    message: str = Field(min_length=1)
    source: TicketSource = "form"
    customer_tier: CustomerTier = "standard"

    @field_validator("customer_name", "subject", "message")
    @classmethod
    def text_fields_must_not_be_blank(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("must not be blank")
        return value


class TicketRead(SQLModel):
    id: int
    customer_name: str
    customer_email: str | None
    subject: str
    message: str
    source: str
    customer_tier: str
    category: str
    priority: str
    priority_score: int
    sentiment: str
    assigned_team: str
    suggested_reply: str
    next_action: str
    status: str
    created_at: datetime
    updated_at: datetime


class TicketStatusUpdate(SQLModel):
    status: TicketStatus


class AnalyticsSummary(SQLModel):
    total_tickets: int
    open_tickets: int
    urgent_tickets: int
    tickets_by_category: dict[str, int]
    tickets_by_priority: dict[str, int]
    tickets_by_team: dict[str, int]
    tickets_by_sentiment: dict[str, int]
    average_priority_score: float
