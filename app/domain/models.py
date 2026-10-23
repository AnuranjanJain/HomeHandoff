from __future__ import annotations

from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, Field


class ArrivalEvent(BaseModel):
    event_id: str
    event_type: Literal["delivery", "visitor"]
    actor: str
    status: str
    eta: str
    instruction: str
    source: str
    recorded_at: datetime


class HouseholdPolicy(BaseModel):
    safe_dropoff_location: str
    trusted_contacts: list[str]
    automatic_unlock_allowed: bool = False
    confirmation_required_for_notifications: bool = True


class Availability(BaseModel):
    resident_status: str
    resident_available: bool
    trusted_contact_available: bool


class ToolCall(BaseModel):
    name: str
    input: dict[str, Any] = Field(default_factory=dict)
    output: dict[str, Any] = Field(default_factory=dict)
    status: Literal["completed", "blocked"] = "completed"


class ProposedAction(BaseModel):
    action_id: str
    status: Literal["proposed", "refused", "needs_clarification", "confirmed"]
    title: str
    description: str
    reason: str
    risk_level: Literal["low", "medium", "high"]
    requires_confirmation: bool
    allowed: bool


class Notification(BaseModel):
    recipient: str
    message: str
    status: Literal["simulated"] = "simulated"


class AuditEntry(BaseModel):
    timestamp: datetime
    event_id: str
    request: str
    decision: str
    reason: str
    data_boundary: str


class Message(BaseModel):
    role: Literal["user", "assistant"]
    content: str


class SessionState(BaseModel):
    session_id: str
    event: ArrivalEvent
    policy: HouseholdPolicy
    availability: Availability
    messages: list[Message] = Field(default_factory=list)
    tool_calls: list[ToolCall] = Field(default_factory=list)
    recommendation: ProposedAction | None = None
    notification: Notification | None = None
    audit_log: list[AuditEntry] = Field(default_factory=list)
    status: Literal["ready", "review", "confirmed", "blocked"] = "ready"


class AskRequest(BaseModel):
    message: str = Field(min_length=1, max_length=500)


class ConfirmRequest(BaseModel):
    action_id: str = Field(min_length=1, max_length=100)
