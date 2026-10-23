from __future__ import annotations

import re
from typing import Literal

from app.domain.models import ArrivalEvent, Availability, HouseholdPolicy, ProposedAction

Intent = Literal["safe_delivery", "visitor_check", "unsafe_access", "ambiguous"]


def parse_intent(message: str) -> Intent:
    normalized = message.casefold()
    access_request = re.search(
        r"\b(unlock|unlatch|open|buzz|let|allow|grant|disarm)\b.{0,40}\b(door|lock|entry|inside|in)\b",
        normalized,
    )
    reverse_access_request = re.search(
        r"\b(door|lock)\b.{0,30}\b(unlock|unlatch|open|buzz|disarm)\b",
        normalized,
    )
    if access_request or reverse_access_request:
        return "unsafe_access"
    if any(term in normalized for term in ("visitor", "caregiver", "guest")):
        return "visitor_check"
    if any(term in normalized for term in ("delivery", "package", "courier", "parcel")):
        return "safe_delivery"
    return "ambiguous"


def evaluate_request(
    intent: Intent,
    event: ArrivalEvent,
    policy: HouseholdPolicy,
    availability: Availability,
) -> ProposedAction:
    if intent == "unsafe_access":
        return ProposedAction(
            action_id="blocked-access",
            status="refused",
            title="No automatic access",
            description="The household policy does not allow an agent to unlock or open the door.",
            reason="Access control is a high-risk action and requires a separate trusted verification flow.",
            risk_level="high",
            requires_confirmation=False,
            allowed=False,
        )

    if intent == "safe_delivery" and event.event_type == "delivery":
        return ProposedAction(
            action_id="safe-dropoff",
            status="proposed",
            title=f"Ask {policy.trusted_contacts[0]} to watch for the porch drop-off",
            description=(
                f"The resident is {availability.resident_status.lower()}. "
                f"The event instruction says: {event.instruction}"
            ),
            reason="This shares the delivery update with a trusted contact without granting home access.",
            risk_level="low",
            requires_confirmation=policy.confirmation_required_for_notifications,
            allowed=True,
        )

    if intent == "visitor_check":
        return ProposedAction(
            action_id="verify-visitor",
            status="proposed",
            title="Ask a trusted contact to verify the visitor",
            description=(
                f"The resident is {availability.resident_status.lower()}. "
                "A trusted contact can be notified without opening the door."
            ),
            reason="Visitor identity is not established by the current simulated event.",
            risk_level="medium",
            requires_confirmation=True,
            allowed=True,
        )

    return ProposedAction(
        action_id="needs-context",
        status="needs_clarification",
        title="I need more context",
        description="Say whether you want to handle the delivery, check a visitor, or request a safe notification.",
        reason="The request does not identify a safe action for the current event.",
        risk_level="medium",
        requires_confirmation=False,
        allowed=False,
    )
