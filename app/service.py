from __future__ import annotations

from datetime import datetime, timezone
from uuid import uuid4

from app.adapters.simulated_data import load_arrival_event, load_availability, load_household_policy
from app.adapters.bedrock import BedrockIntentInterpreter
from app.domain.models import AuditEntry, Message, Notification, ProposedAction, SessionState, ToolCall
from app.domain.policy import evaluate_request, parse_intent


class HomeHandoffService:
    def __init__(self) -> None:
        self.interpreter = BedrockIntentInterpreter()
        self.pending_request: str | None = None
        self.state = self._new_state()

    def _new_state(self) -> SessionState:
        return SessionState(
            session_id=str(uuid4()),
            event=load_arrival_event(),
            policy=load_household_policy(),
            availability=load_availability(),
        )

    def reset(self) -> SessionState:
        self.pending_request = None
        self.state = self._new_state()
        return self.state

    def _tool(self, name: str, tool_input: dict, output: dict, status: str = "completed") -> None:
        self.state.tool_calls.append(ToolCall(name=name, input=tool_input, output=output, status=status))

    def handle_request(self, message: str) -> SessionState:
        self.pending_request = message
        self.state.messages.append(Message(role="user", content=message))
        self.state.tool_calls = []
        self.state.recommendation = None
        self.state.notification = None
        self.state.status = "review"

        self._tool(
            "get_arrival_event",
            {},
            {"event_id": self.state.event.event_id, "status": self.state.event.status, "source": self.state.event.source},
        )
        self._tool(
            "get_household_policy",
            {},
            {
                "safe_dropoff_location": self.state.policy.safe_dropoff_location,
                "automatic_unlock_allowed": self.state.policy.automatic_unlock_allowed,
            },
        )
        self._tool(
            "check_presence_and_schedule",
            {},
            {
                "resident_status": self.state.availability.resident_status,
                "resident_available": self.state.availability.resident_available,
            },
        )

        rule_intent = parse_intent(message)
        interpretation = self.interpreter.interpret(message) if rule_intent != "unsafe_access" else None
        intent = (
            "unsafe_access"
            if rule_intent == "unsafe_access"
            else (interpretation.intent if interpretation and interpretation.intent else rule_intent)
        )
        provider = interpretation.provider if interpretation else "local safety rule"
        interpretation_output = {"intent": intent, "provider": provider}
        if interpretation and interpretation.error:
            interpretation_output["fallback_reason"] = interpretation.error
        self._tool("interpret_request", {"message": message}, interpretation_output)
        recommendation = evaluate_request(intent, self.state.event, self.state.policy, self.state.availability)
        self._tool(
            "propose_safe_action",
            {"intent": intent},
            recommendation.model_dump(mode="json"),
            status="completed" if recommendation.allowed else "blocked",
        )
        self.state.recommendation = recommendation
        self.state.status = "blocked" if recommendation.status in ("refused", "needs_clarification") else "review"
        self.state.messages.append(Message(role="assistant", content=self._response_for(recommendation)))
        return self.state

    def confirm(self, action_id: str) -> SessionState:
        recommendation = self.state.recommendation
        if recommendation is None:
            raise ValueError("There is no pending action to confirm.")
        if recommendation.action_id != action_id:
            raise ValueError("That action is no longer the active recommendation.")
        if not recommendation.allowed or not recommendation.requires_confirmation:
            raise ValueError("This recommendation cannot be confirmed.")

        recommendation.status = "confirmed"
        recipient = self.state.policy.trusted_contacts[0]
        self.state.notification = Notification(
            recipient=recipient,
            message=f"HomeHandoff confirmed: {recommendation.title}.",
        )
        self._tool(
            "simulate_household_notification",
            {"recipient": recipient},
            {"status": "simulated", "message": self.state.notification.message},
        )
        self._tool(
            "write_audit_record",
            {"event_id": self.state.event.event_id},
            {"status": "recorded", "decision": recommendation.title},
        )
        self.state.audit_log.append(
            AuditEntry(
                timestamp=datetime.now(timezone.utc),
                event_id=self.state.event.event_id,
                request=self.pending_request or "",
                decision=recommendation.title,
                reason=recommendation.reason,
                data_boundary="Simulated event and household records; no live device action occurred.",
            )
        )
        self.state.status = "confirmed"
        self.state.messages.append(
            Message(
                role="assistant",
                content=f"Confirmed. A simulated notification was recorded for {recipient}; no message was sent outside this demo.",
            )
        )
        return self.state

    @staticmethod
    def _response_for(recommendation: ProposedAction) -> str:
        if recommendation.status == "refused":
            return f"I cannot do that. {recommendation.reason}"
        if recommendation.status == "needs_clarification":
            return recommendation.description
        return f"I recommend: {recommendation.title}. {recommendation.reason} Please confirm to notify the household."
