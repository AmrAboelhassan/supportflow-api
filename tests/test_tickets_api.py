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


def _ticket_payload(**overrides: str) -> dict:
    payload = {
        "customer_name": "Ava Stone",
        "customer_email": "ava@example.com",
        "subject": "Cannot login",
        "message": "This is urgent. I cannot login and my team is blocked today.",
        "source": "email",
        "customer_tier": "standard",
    }
    payload.update(overrides)
    return payload


def test_create_ticket_generates_triage_fields(client: TestClient) -> None:
    response = client.post("/tickets", json=_ticket_payload())

    assert response.status_code == 201
    data = response.json()
    assert data["id"] == 1
    assert data["category"] == "technical"
    assert data["priority"] == "urgent"
    assert data["sentiment"] == "neutral"
    assert data["assigned_team"] == "technical_support"
    assert data["status"] == "open"
    assert "suggested_reply" in data
    assert "next_action" in data


def test_list_tickets_filters_and_search(client: TestClient) -> None:
    client.post("/tickets", json=_ticket_payload(customer_name="Ava Stone"))
    client.post(
        "/tickets",
            json=_ticket_payload(
                customer_name="Ben Reed",
                customer_email="ben@example.com",
                subject="Invoice refund",
                message="I need a refund for a duplicate invoice charge.",
                source="chat",
            ),
    )

    billing_response = client.get("/tickets", params={"category": "billing"})
    assert billing_response.status_code == 200
    billing_data = billing_response.json()
    assert len(billing_data) == 1
    assert billing_data[0]["assigned_team"] == "finance"

    search_response = client.get("/tickets", params={"q": "Ava"})
    assert search_response.status_code == 200
    assert len(search_response.json()) == 1


def test_get_ticket_detail_and_missing_ticket(client: TestClient) -> None:
    create_response = client.post("/tickets", json=_ticket_payload())
    ticket_id = create_response.json()["id"]

    detail_response = client.get(f"/tickets/{ticket_id}")
    assert detail_response.status_code == 200
    assert detail_response.json()["id"] == ticket_id

    missing_response = client.get("/tickets/999")
    assert missing_response.status_code == 404


def test_update_ticket_status_and_reject_invalid_status(client: TestClient) -> None:
    create_response = client.post("/tickets", json=_ticket_payload())
    ticket_id = create_response.json()["id"]

    update_response = client.patch(
        f"/tickets/{ticket_id}/status",
        json={"status": "in_progress"},
    )
    assert update_response.status_code == 200
    assert update_response.json()["status"] == "in_progress"

    invalid_response = client.patch(
        f"/tickets/{ticket_id}/status",
        json={"status": "paused"},
    )
    assert invalid_response.status_code == 422


def test_seed_endpoint_is_available_for_demo_data(client: TestClient) -> None:
    response = client.post("/seed")

    assert response.status_code == 200
    assert response.json()["created"] == 5
