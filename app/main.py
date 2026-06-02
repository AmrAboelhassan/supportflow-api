from collections.abc import Generator
from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, HTTPException, Query, status
from sqlmodel import Session

from app import crud
from app.database import get_session, init_db
from app.models import Ticket
from app.schemas import (
    AnalyticsSummary,
    TicketCategory,
    TicketCreate,
    TicketPriority,
    TicketRead,
    TicketSentiment,
    TicketStatus,
    TicketStatusUpdate,
)
from app.seed import seed_sample_tickets


@asynccontextmanager
async def lifespan(app: FastAPI) -> Generator[None, None, None]:
    init_db()
    yield


app = FastAPI(
    title="SupportFlow Triage API",
    description=(
        "FastAPI-based support ticket triage system with rule-based classification, "
        "priority scoring, suggested replies, status tracking, and analytics."
    ),
    version="0.1.0",
    lifespan=lifespan,
)


@app.get("/")
def root() -> dict[str, str]:
    return {
        "name": "SupportFlow Triage API",
        "description": (
            "FastAPI-based support ticket triage system with rule-based classification, "
            "priority scoring, suggested replies, status tracking, and analytics."
        ),
        "docs": "/docs",
    }


@app.post("/tickets", response_model=TicketRead, status_code=status.HTTP_201_CREATED)
def create_ticket(ticket_in: TicketCreate, session: Session = Depends(get_session)) -> Ticket:
    return crud.create_ticket(session=session, ticket_in=ticket_in)


@app.get("/tickets", response_model=list[TicketRead])
def list_tickets(
    status: TicketStatus | None = None,
    category: TicketCategory | None = None,
    priority: TicketPriority | None = None,
    assigned_team: str | None = None,
    sentiment: TicketSentiment | None = None,
    q: str | None = Query(default=None, description="Search customer, subject, email, or message text."),
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    session: Session = Depends(get_session),
) -> list[Ticket]:
    return crud.list_tickets(
        session=session,
        status=status,
        category=category,
        priority=priority,
        assigned_team=assigned_team,
        sentiment=sentiment,
        q=q,
        limit=limit,
        offset=offset,
    )


@app.get("/tickets/{ticket_id}", response_model=TicketRead)
def get_ticket(ticket_id: int, session: Session = Depends(get_session)) -> Ticket:
    ticket = crud.get_ticket(session=session, ticket_id=ticket_id)
    if ticket is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ticket not found")
    return ticket


@app.patch("/tickets/{ticket_id}/status", response_model=TicketRead)
def update_ticket_status(
    ticket_id: int,
    status_update: TicketStatusUpdate,
    session: Session = Depends(get_session),
) -> Ticket:
    ticket = crud.get_ticket(session=session, ticket_id=ticket_id)
    if ticket is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ticket not found")
    return crud.update_ticket_status(session=session, ticket=ticket, status=status_update.status)


@app.get("/analytics/summary", response_model=AnalyticsSummary)
def analytics_summary(session: Session = Depends(get_session)) -> dict:
    return crud.get_analytics_summary(session=session)


@app.post("/seed", tags=["Development"])
def seed_demo_data(session: Session = Depends(get_session)) -> dict:
    """Create sample tickets for local development and portfolio demos only."""
    tickets = seed_sample_tickets(session=session)
    return {
        "message": "Development/demo sample tickets created.",
        "created": len(tickets),
        "ticket_ids": [ticket.id for ticket in tickets],
    }
