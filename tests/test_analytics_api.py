from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.pool import StaticPool
from sqlmodel import Session, SQLModel, create_engine

from app.database import get_session
from app.main import app


@pytest.fixture()
def client() -> Generator[TestClient, None, None]:
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)

    def get_test_session() -> Generator[Session, None, None]:
        with Session(engine) as session:
            yield session

    app.dependency_overrides[get_session] = get_test_session
    test_client = TestClient(app)
    yield test_client
    test_client.close()
    app.dependency_overrides.clear()


def test_analytics_summary_counts_tickets(client: TestClient) -> None:
    client.post(
        "/tickets",
        json={
            "customer_name": "Maya Patel",
            "customer_email": "maya@example.com",
            "subject": "Invoice charge",
            "message": "I need a refund for a duplicate payment charge.",
            "source": "email",
            "customer_tier": "standard",
        },
    )
    client.post(
        "/tickets",
        json={
            "customer_name": "Liam Carter",
            "customer_email": "liam@example.com",
            "subject": "Cannot login",
            "message": "Urgent, the system is down and we are blocked today.",
            "source": "chat",
            "customer_tier": "vip",
        },
    )

    response = client.get("/analytics/summary")

    assert response.status_code == 200
    data = response.json()
    assert data["total_tickets"] == 2
    assert data["open_tickets"] == 2
    assert data["urgent_tickets"] == 1
    assert data["tickets_by_category"]["billing"] == 1
    assert data["tickets_by_category"]["technical"] == 1
    assert data["tickets_by_priority"]["urgent"] == 1
    assert data["tickets_by_team"]["finance"] == 1
    assert data["average_priority_score"] > 0
