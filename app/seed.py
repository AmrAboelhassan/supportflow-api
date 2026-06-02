from sqlmodel import Session

from app.crud import create_ticket
from app.models import Ticket
from app.schemas import TicketCreate


SAMPLE_TICKETS = [
    {
        "customer_name": "Maya Patel",
        "customer_email": "maya@example.com",
        "subject": "Invoice charge looks wrong",
        "message": "I was charged twice for my subscription invoice this month.",
        "source": "email",
        "customer_tier": "premium",
    },
    {
        "customer_name": "Liam Carter",
        "customer_email": "liam@example.com",
        "subject": "Cannot login and our team is blocked",
        "message": "This is urgent. We cannot login today and the portal is down for our staff.",
        "source": "chat",
        "customer_tier": "vip",
    },
    {
        "customer_name": "Noor Hassan",
        "customer_email": "noor@example.com",
        "subject": "Need pricing for a larger plan",
        "message": "Can someone share a quote and schedule a demo for the enterprise plan?",
        "source": "form",
        "customer_tier": "standard",
    },
    {
        "customer_name": "Elena Garcia",
        "customer_email": "elena@example.com",
        "subject": "Password reset help",
        "message": "I need help with password access for my profile email.",
        "source": "whatsapp",
        "customer_tier": "standard",
    },
    {
        "customer_name": "Sam Wilson",
        "customer_email": "sam@example.com",
        "subject": "Thanks for the quick support",
        "message": "Thank you, the last answer was helpful and everything looks great.",
        "source": "email",
        "customer_tier": "standard",
    },
]


def seed_sample_tickets(session: Session) -> list[Ticket]:
    tickets: list[Ticket] = []
    for ticket_data in SAMPLE_TICKETS:
        tickets.append(create_ticket(session=session, ticket_in=TicketCreate(**ticket_data)))
    return tickets
