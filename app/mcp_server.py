from __future__ import annotations

from mcp.server.fastmcp import FastMCP

from app.adapters.simulated_data import load_arrival_event, load_availability, load_household_policy
from app.domain.policy import evaluate_request, parse_intent

mcp = FastMCP(
    "HomeHandoff",
    instructions=(
        "Consent-first household handoff tools. Event data is simulated. "
        "Never unlock a door or take a high-risk action automatically."
    ),
    host="127.0.0.1",
    port=8001,
    streamable_http_path="/mcp",
    stateless_http=True,
)


@mcp.tool()
def get_arrival_event() -> dict:
    """Return the current simulated household arrival event."""
    return load_arrival_event().model_dump(mode="json")


@mcp.tool()
def get_household_policy() -> dict:
    """Return household safety rules for the current scenario."""
    return load_household_policy().model_dump(mode="json")


@mcp.tool()
def check_presence_and_schedule() -> dict:
    """Return resident availability for the current scenario."""
    return load_availability().model_dump(mode="json")


@mcp.tool()
def propose_safe_action(request: str) -> dict:
    """Evaluate a request against the household policy without performing an action."""
    event = load_arrival_event()
    policy = load_household_policy()
    availability = load_availability()
    intent = parse_intent(request)
    recommendation = evaluate_request(intent, event, policy, availability)
    return {"intent": intent, "recommendation": recommendation.model_dump(mode="json")}


@mcp.tool()
def prepare_notification(recipient: str, message: str) -> dict:
    """Prepare a notification draft; an external client must obtain confirmation before sending."""
    return {
        "status": "awaiting_confirmation",
        "recipient": recipient,
        "message": message,
        "requires_confirmation": True,
        "data_boundary": "Draft only; no notification was sent and no live device action occurred.",
    }


if __name__ == "__main__":
    mcp.run(transport="streamable-http")
