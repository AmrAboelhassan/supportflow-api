from dataclasses import dataclass


@dataclass(frozen=True)
class TriageResult:
    category: str
    priority: str
    priority_score: int
    sentiment: str
    assigned_team: str
    suggested_reply: str
    next_action: str


CATEGORY_KEYWORDS = {
    "billing": ("invoice", "payment", "refund", "subscription", "charge"),
    "technical": ("error", "bug", "crash", "login", "not working", "down"),
    "sales": ("pricing", "demo", "quote", "plan"),
    "account": ("password", "profile", "access", "email"),
}

TEAM_BY_CATEGORY = {
    "billing": "finance",
    "technical": "technical_support",
    "sales": "sales",
    "account": "customer_success",
    "general": "support",
}

URGENT_KEYWORDS = (
    "urgent",
    "asap",
    "today",
    "losing money",
    "blocked",
    "down",
    "cannot login",
    "can't login",
)
HIGH_KEYWORDS = (
    "angry",
    "frustrated",
    "complaint",
    "failed payment",
    "production issue",
)
LOW_KEYWORDS = ("simple question", "thanks", "thank you", "appreciate")
NEGATIVE_KEYWORDS = (
    "angry",
    "frustrated",
    "upset",
    "complaint",
    "terrible",
    "disappointed",
)
POSITIVE_KEYWORDS = ("thanks", "thank you", "great", "appreciate", "helpful")

PRIORITY_SCORES = {
    "low": 20,
    "medium": 50,
    "high": 75,
    "urgent": 95,
}
PRIORITY_ORDER = ("low", "medium", "high", "urgent")


def triage_ticket(subject: str, message: str, customer_tier: str = "standard") -> TriageResult:
    text = _normalize(f"{subject} {message}")
    category = _classify_category(text)
    sentiment = _detect_sentiment(text)
    priority = _calculate_priority(text, sentiment, customer_tier)
    assigned_team = TEAM_BY_CATEGORY[category]

    return TriageResult(
        category=category,
        priority=priority,
        priority_score=PRIORITY_SCORES[priority],
        sentiment=sentiment,
        assigned_team=assigned_team,
        suggested_reply=_suggest_reply(category, priority, sentiment),
        next_action=_next_action(category, priority),
    )


def _normalize(text: str) -> str:
    return " ".join(text.lower().split())


def _contains_any(text: str, keywords: tuple[str, ...]) -> bool:
    return any(keyword in text for keyword in keywords)


def _classify_category(text: str) -> str:
    for category, keywords in CATEGORY_KEYWORDS.items():
        if _contains_any(text, keywords):
            return category
    return "general"


def _detect_sentiment(text: str) -> str:
    if _contains_any(text, NEGATIVE_KEYWORDS):
        return "negative"
    if _contains_any(text, POSITIVE_KEYWORDS):
        return "positive"
    return "neutral"


def _calculate_priority(text: str, sentiment: str, customer_tier: str) -> str:
    if _contains_any(text, URGENT_KEYWORDS):
        return "urgent"
    if _contains_any(text, HIGH_KEYWORDS) or sentiment == "negative":
        priority = "high"
    elif _contains_any(text, LOW_KEYWORDS):
        priority = "low"
    elif customer_tier == "premium":
        priority = "high"
    else:
        priority = "medium"

    if customer_tier == "vip":
        return _escalate_priority(priority)
    return priority


def _escalate_priority(priority: str) -> str:
    index = PRIORITY_ORDER.index(priority)
    return PRIORITY_ORDER[min(index + 1, len(PRIORITY_ORDER) - 1)]


def _suggest_reply(category: str, priority: str, sentiment: str) -> str:
    opener = "Thanks for contacting us."
    if priority in {"high", "urgent"} or sentiment == "negative":
        opener = "Thanks for contacting us. We understand this is important and will prioritize it."

    templates = {
        "billing": "Our finance team will review the billing details and follow up with an update.",
        "technical": "Our technical support team will investigate the issue and share next steps.",
        "sales": "Our sales team will review your request and contact you with the right information.",
        "account": "Our customer success team will review your account details and help restore access or update information.",
        "general": "Our support team will review your message and respond with the best next step.",
    }
    return f"{opener} {templates[category]}"


def _next_action(category: str, priority: str) -> str:
    if priority == "urgent" and category in {"technical", "account"}:
        return "Investigate immediately and provide a status update."

    actions = {
        "billing": "Review billing records and confirm the account transaction history.",
        "technical": "Reproduce or inspect the technical issue and prepare troubleshooting steps.",
        "sales": "Schedule a sales follow-up and prepare plan or pricing details.",
        "account": "Verify account details and confirm the requested account change or access issue.",
        "general": "Review the ticket and route it to the correct owner if needed.",
    }
    return actions[category]
