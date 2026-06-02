from collections import Counter
from datetime import datetime

from sqlmodel import Session, col, select

from app.models import Ticket
from app.schemas import TicketCreate
from app.triage import triage_ticket


def create_ticket(session: Session, ticket_in: TicketCreate) -> Ticket:
    triage = triage_ticket(
        subject=ticket_in.subject,
        message=ticket_in.message,
        customer_tier=ticket_in.customer_tier,
    )
    ticket = Ticket(
        **ticket_in.model_dump(),
        category=triage.category,
        priority=triage.priority,
        priority_score=triage.priority_score,
        sentiment=triage.sentiment,
        assigned_team=triage.assigned_team,
        suggested_reply=triage.suggested_reply,
        next_action=triage.next_action,
    )
    session.add(ticket)
    session.commit()
    session.refresh(ticket)
    return ticket


def list_tickets(
    session: Session,
    status: str | None = None,
    category: str | None = None,
    priority: str | None = None,
    assigned_team: str | None = None,
    sentiment: str | None = None,
    q: str | None = None,
    limit: int = 50,
    offset: int = 0,
) -> list[Ticket]:
    statement = select(Ticket).order_by(col(Ticket.created_at).desc()).offset(offset).limit(limit)

    if status:
        statement = statement.where(Ticket.status == status)
    if category:
        statement = statement.where(Ticket.category == category)
    if priority:
        statement = statement.where(Ticket.priority == priority)
    if assigned_team:
        statement = statement.where(Ticket.assigned_team == assigned_team)
    if sentiment:
        statement = statement.where(Ticket.sentiment == sentiment)
    if q:
        query = f"%{q.lower()}%"
        statement = statement.where(
            col(Ticket.customer_name).ilike(query)
            | col(Ticket.customer_email).ilike(query)
            | col(Ticket.subject).ilike(query)
            | col(Ticket.message).ilike(query)
        )

    return list(session.exec(statement).all())


def get_ticket(session: Session, ticket_id: int) -> Ticket | None:
    return session.get(Ticket, ticket_id)


def update_ticket_status(session: Session, ticket: Ticket, status: str) -> Ticket:
    ticket.status = status
    ticket.updated_at = datetime.utcnow()
    session.add(ticket)
    session.commit()
    session.refresh(ticket)
    return ticket


def get_analytics_summary(session: Session) -> dict:
    tickets = list(session.exec(select(Ticket)).all())
    total_tickets = len(tickets)
    open_tickets = sum(1 for ticket in tickets if ticket.status == "open")
    urgent_tickets = sum(1 for ticket in tickets if ticket.priority == "urgent")
    average_priority_score = (
        round(sum(ticket.priority_score for ticket in tickets) / total_tickets, 2)
        if total_tickets
        else 0.0
    )

    return {
        "total_tickets": total_tickets,
        "open_tickets": open_tickets,
        "urgent_tickets": urgent_tickets,
        "tickets_by_category": dict(Counter(ticket.category for ticket in tickets)),
        "tickets_by_priority": dict(Counter(ticket.priority for ticket in tickets)),
        "tickets_by_team": dict(Counter(ticket.assigned_team for ticket in tickets)),
        "tickets_by_sentiment": dict(Counter(ticket.sentiment for ticket in tickets)),
        "average_priority_score": average_priority_score,
    }
