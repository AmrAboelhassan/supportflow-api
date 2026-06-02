from app.triage import triage_ticket


def test_classifies_billing_ticket() -> None:
    result = triage_ticket(
        subject="Invoice question",
        message="I need a refund for a duplicate payment charge.",
    )

    assert result.category == "billing"
    assert result.assigned_team == "finance"


def test_classifies_urgent_technical_ticket() -> None:
    result = triage_ticket(
        subject="Cannot login",
        message="This is urgent, our portal is down and we are blocked today.",
    )

    assert result.category == "technical"
    assert result.priority == "urgent"
    assert result.priority_score == 95
    assert result.assigned_team == "technical_support"


def test_detects_negative_sentiment_and_high_priority() -> None:
    result = triage_ticket(
        subject="Support complaint",
        message="I am frustrated and disappointed with this terrible issue.",
    )

    assert result.sentiment == "negative"
    assert result.priority == "high"


def test_normal_positive_message_stays_low_priority() -> None:
    result = triage_ticket(
        subject="Thanks",
        message="Thank you, I appreciate the helpful support.",
    )

    assert result.category == "general"
    assert result.sentiment == "positive"
    assert result.priority == "low"


def test_vip_low_positive_message_becomes_medium_priority() -> None:
    result = triage_ticket(
        subject="Thanks",
        message="Thank you, I appreciate the helpful support.",
        customer_tier="vip",
    )

    assert result.sentiment == "positive"
    assert result.priority == "medium"


def test_vip_medium_message_becomes_high_priority() -> None:
    result = triage_ticket(
        subject="Question about my account",
        message="Can you help me update my email?",
        customer_tier="vip",
    )

    assert result.priority == "high"


def test_urgent_keyword_still_becomes_urgent_priority() -> None:
    result = triage_ticket(
        subject="Simple question",
        message="This is urgent, please help when possible.",
        customer_tier="standard",
    )

    assert result.priority == "urgent"
