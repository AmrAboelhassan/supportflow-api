# SupportFlow Triage API

Repository name: `supportflow-api`

FastAPI-based support ticket triage system with rule-based classification, priority scoring, suggested replies, status tracking, and analytics.

SupportFlow Triage API is a local-first backend project for support operations. The MVP uses a deterministic, rule-based triage engine. It does not use an AI model, does not call external AI services, does not require OpenAI API keys, and does not use paid APIs.

The project is designed as a GitHub portfolio backend: it demonstrates API design, SQLite persistence, SQLModel models, business logic, filtering, status tracking, analytics, and a clean triage interface that could later support optional LLM-assisted triage with rule-based fallback.

## Features

- Create support tickets from customer messages.
- Automatically estimate category, priority, sentiment, assigned team, suggested reply, next action, and status.
- List and filter tickets by status, category, priority, assigned team, sentiment, and search query.
- Retrieve ticket details.
- Update ticket status.
- View analytics summary.
- Seed sample demo tickets for local testing.
- Run focused pytest coverage for triage rules, API behavior, and analytics.

## Tech Stack

- Python
- FastAPI
- SQLite
- SQLModel
- Pydantic validation through FastAPI and SQLModel
- Uvicorn
- Pytest

## Architecture

```text
app/
  main.py       FastAPI application and route definitions
  database.py   SQLite engine, session dependency, and table initialization
  models.py     SQLModel database table models
  schemas.py    API request and response schemas
  crud.py       Database operations, filtering, status updates, analytics
  triage.py     Rule-based triage engine
  seed.py       Development/demo sample ticket seeding
tests/
  test_triage.py
  test_tickets_api.py
  test_analytics_api.py
```

The MVP keeps the triage engine isolated in `app/triage.py`. That keeps the API and database layers separate from triage decisions and leaves a clear extension point for optional LLM-assisted triage later.

## API Endpoints

| Method | Path | Description |
| --- | --- | --- |
| `GET` | `/` | Basic project info |
| `POST` | `/tickets` | Create a ticket and run rule-based triage |
| `GET` | `/tickets` | List tickets with filters and search |
| `GET` | `/tickets/{ticket_id}` | Get one ticket |
| `PATCH` | `/tickets/{ticket_id}/status` | Update ticket status |
| `GET` | `/analytics/summary` | Get ticket analytics summary |
| `POST` | `/seed` | Create sample tickets for development/demo use only |

## Setup

Create and activate a virtual environment:

```bash
python -m venv .venv
.venv\Scripts\activate.bat
```

Install dependencies:

```bash
python -m pip install -r requirements.txt
```

Run the API:

```bash
uvicorn app.main:app --reload
```

Open:

```text
http://127.0.0.1:8000
http://127.0.0.1:8000/docs
```

## Usage Examples

Create a ticket:

```bash
curl -X POST http://127.0.0.1:8000/tickets ^
  -H "Content-Type: application/json" ^
  -d "{\"customer_name\":\"Ava Stone\",\"customer_email\":\"ava@example.com\",\"subject\":\"Cannot login\",\"message\":\"This is urgent. I cannot login and my team is blocked today.\",\"source\":\"email\",\"customer_tier\":\"standard\"}"
```

List tickets:

```bash
curl "http://127.0.0.1:8000/tickets"
```

Filter tickets:

```bash
curl "http://127.0.0.1:8000/tickets?category=technical&priority=urgent"
```

Search tickets:

```bash
curl "http://127.0.0.1:8000/tickets?q=invoice"
```

Get ticket detail:

```bash
curl "http://127.0.0.1:8000/tickets/1"
```

Update status:

```bash
curl -X PATCH http://127.0.0.1:8000/tickets/1/status ^
  -H "Content-Type: application/json" ^
  -d "{\"status\":\"in_progress\"}"
```

Get analytics:

```bash
curl "http://127.0.0.1:8000/analytics/summary"
```

Seed demo data:

```bash
curl -X POST "http://127.0.0.1:8000/seed"
```

## Sample Request

```json
{
  "customer_name": "Ava Stone",
  "customer_email": "ava@example.com",
  "subject": "Cannot login",
  "message": "This is urgent. I cannot login and my team is blocked today.",
  "source": "email",
  "customer_tier": "standard"
}
```

## Sample Response

```json
{
  "id": 1,
  "customer_name": "Ava Stone",
  "customer_email": "ava@example.com",
  "subject": "Cannot login",
  "message": "This is urgent. I cannot login and my team is blocked today.",
  "source": "email",
  "customer_tier": "standard",
  "category": "technical",
  "priority": "urgent",
  "priority_score": 95,
  "sentiment": "neutral",
  "assigned_team": "technical_support",
  "suggested_reply": "Thanks for contacting us. We understand this is important and will prioritize it. Our technical support team will investigate the issue and share next steps.",
  "next_action": "Investigate immediately and provide a status update.",
  "status": "open",
  "created_at": "2026-06-02T08:00:00",
  "updated_at": "2026-06-02T08:00:00"
}
```

## Triage Logic

The MVP triage engine is rule-based:

- Categories are matched by keywords such as `invoice`, `payment`, `refund`, `error`, `bug`, `login`, `pricing`, `demo`, `password`, and `access`.
- Priority is based on urgency keywords, customer tier, negative wording, and simple low-risk messages.
- Sentiment is detected from positive and negative keyword groups.
- Assigned team is mapped from category.
- Suggested replies and next actions are templated from category, priority, and sentiment.

Category-to-team mapping:

| Category | Team |
| --- | --- |
| `billing` | `finance` |
| `technical` | `technical_support` |
| `sales` | `sales` |
| `account` | `customer_success` |
| `general` | `support` |

Allowed statuses:

```text
open
in_progress
waiting_customer
resolved
closed
```

## Limitations

- This version does not use an AI model or LLM.
- Triage quality depends on simple keyword matching.
- No authentication or role-based access control.
- No frontend or admin dashboard.
- No SLA automation.
- No email, chat, webhook, or WhatsApp ingestion.
- SQLite is used for local development and portfolio demonstration.

## Future Improvements

- Optional LLM-assisted triage mode with rule-based fallback.
- Email and webhook ingestion.
- Admin dashboard.
- User authentication.
- Configurable team assignment rules.
- SLA tracking.
- PostgreSQL migration.
- Docker support.
- Deployment.

## QA Checklist

Run compile checks:

```bash
python -m py_compile app/main.py app/database.py app/models.py app/schemas.py app/crud.py app/triage.py app/seed.py
```

Run tests:

```bash
pytest
```

Manual checks:

- Start the API with `uvicorn app.main:app --reload`.
- Open Swagger docs at `/docs`.
- Test `POST /tickets`.
- Test `GET /tickets` filters.
- Test `GET /tickets/{ticket_id}`.
- Test `PATCH /tickets/{ticket_id}/status`.
- Test `GET /analytics/summary`.
- Optionally seed demo data with `POST /seed`.
