from datetime import datetime

from app.domain.models import ArrivalEvent, Availability, HouseholdPolicy


def load_arrival_event() -> ArrivalEvent:
    return ArrivalEvent(
        event_id="arrival-001",
        event_type="delivery",
        actor="Northstar Couriers",
        status="Arriving now",
        eta="Now",
        instruction="Leave at the covered porch. Do not enter the home.",
        source="Simulated household event",
        recorded_at=datetime.fromisoformat("2026-10-23T09:15:00+05:30"),
    )


def load_household_policy() -> HouseholdPolicy:
    return HouseholdPolicy(
        safe_dropoff_location="covered porch",
        trusted_contacts=["Maya", "Rohan"],
        automatic_unlock_allowed=False,
        confirmation_required_for_notifications=True,
    )


def load_availability() -> Availability:
    return Availability(
        resident_status="On a work call",
        resident_available=False,
        trusted_contact_available=True,
    )
