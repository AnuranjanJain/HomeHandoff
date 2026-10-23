# Demo Script (under 3 minutes)

## 0:00-0:20 - The problem

Show the arrival context and say:

> When a resident is busy, the useful action is not to give an unverified assistant control of the door. HomeHandoff checks the household policy, proposes a safe handoff, and asks for consent.

## 0:20-1:05 - Safe delivery

Click **Handle the delivery** or enter:

> I am on a call. Handle the delivery safely.

Pause on the tool trace. Point out the arrival event, household policy, availability check, and recommendation.

## 1:05-1:35 - Consent and audit

Click **Confirm simulated notification**. Show the simulated notification record and audit trail. Say:

> After confirmation, the demo records a simulated notification. It does not contact a household messaging service or unlock a device.

## 1:35-2:05 - Safe refusal

Click **Request access**. Show the blocked decision and explain:

> The policy refuses automatic unlocking because access is high risk and the current event does not establish identity.

## 2:05-2:40 - Implementation

Show the repository briefly. Mention FastAPI, Pydantic tool contracts, the policy engine, then switch to the MCP verification terminal and show the protocol version and `propose_safe_action` result. If Bedrock has been configured and verified, show a request whose trace identifies Amazon Bedrock. Otherwise state that model access was unavailable and the deterministic path handled the request.

## 2:40-2:55 - Close

> HomeHandoff turns a vague household request into a visible, consent-based decision that can be inspected and replayed. Event data is simulated; the MCP interface is real and ready for a verified Alexa+ preview connection.
