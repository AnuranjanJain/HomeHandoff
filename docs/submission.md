# Submission Notes

## Project name

HomeHandoff

## Elevator pitch

A simulated Alexa+ agent that turns arrivals into safe, consent-based handoffs.

## Track boundary

This project uses the Alexa+ simulated-experience route and includes an optional self-hosted MCP server using Streamable HTTP. The household event and device state are clearly labelled simulated. The local workflow, policy checks, confirmation boundary, refusal path, and audit trail are executable source code.

## AWS Builder boundary

When configured, Amazon Bedrock interprets the user's request. It cannot decide policy or execute external actions. The local policy engine validates the intent and the confirmation boundary controls notifications. **Select AWS Builder only after a real Bedrock invocation appears in the UI trace.** Record the exact model, AWS region, and onboarding result in the final product feedback.

## Open Source mini challenge

The additional project is `handoff-policy-kit`, a dependency-free MIT-licensed policy package created during this hackathon and published as its own public repository.

- Project repository: <https://github.com/AnuranjanJain/handoff-policy-kit>
- Contribution URL: <https://github.com/AnuranjanJain/handoff-policy-kit/commit/5cb38f1c72972ce9144b0713faae441b39d0caec>
- GitHub username: `AnuranjanJain`
- License: MIT

## Devpost fields

- Submitter type: select the truthful individual/team option.
- Organization: `N/A` if this is a personal submission.
- Primary track: Alexa+.
- Primary repository: <https://github.com/AnuranjanJain/HomeHandoff> (public; MIT license at repository root).
- Project status: new, because this implementation began during the hackathon submission period.
- AWS Builder: do not select yet. The optional Bedrock adapter is implemented, but no Bedrock call has been verified. The local machine does not have AWS CLI installed, and console sign-in alone does not provide local SDK credentials.
- Open Source mini challenge: select; include the contribution and repository URLs above, GitHub username `AnuranjanJain`, and the description in `docs/devpost-copy.md`.
- Product testing: provide the local run command and describe that all household/device records are simulated.
- AI tools, learning, and career-value questions: answer based on the tools actually used and what you personally learned; do not submit a prefilled claim on the participant's behalf.

## Product feedback checklist

For every Amazon, AWS, model, or framework tool used in the final project, record:

- What task it supported.
- What worked well.
- What was difficult or unclear.
- Whether onboarding was sufficient.
- Whether the project would use it again.

## Friction log checklist

For each meaningful issue, record the attempted task, expected behavior, actual behavior, severity, workaround, and actionable suggestion. Do not invent entries; use observed behavior only.
