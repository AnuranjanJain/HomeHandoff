# Devpost Submission Copy

Use this as a draft for the submission. Fill personal eligibility and residence fields yourself. The demo uses simulated household data; do not describe it as connected to a live Alexa+, Ring device, or messaging service.

## Public project page

### Project name

HomeHandoff

### Elevator pitch

A simulated Alexa+ assistant that turns arrivals into safe, consent-based household handoffs.

### About the project

## Inspiration

When someone is busy at home, an assistant may need to help with an arrival without being given open-ended control over the home. HomeHandoff explores a safer interaction: check the household rules, recommend a limited action, and ask the resident to confirm before recording it.

## What it does

HomeHandoff presents a simulated arrival scenario. A resident can ask for help while on a call. The app checks the event, household policy, and availability, then recommends a safe response. The resident can confirm a simulated household notification. A request for automatic access is refused, and each decision is shown in an audit trail.

## How it works

The FastAPI app passes the request through an intent interpreter and a deterministic policy engine. The optional Amazon Bedrock adapter can classify request intent, but it cannot choose the policy outcome or perform an action. Local policy rules decide whether a recommendation is allowed. Confirmation is required before the demo records its simulated notification. The app also exposes these policy operations through a local Streamable HTTP MCP server using protocol version `2025-11-25`.

## How we built it

We built the experience in Python with FastAPI and Pydantic, keeping the policy rules separate from the web interface and simulated data. The MCP Python SDK exposes the same policy checks as tools. A verification script connects with the MCP client, negotiates the protocol, lists the tools, and calls the safe-action tool.

## What we learned

Language interpretation and safety decisions should have different responsibilities. A model can help identify what a person means, while deterministic policy and explicit confirmation constrain what the application can do. We also learned that signing in to the AWS console does not authenticate a local Python process; local AWS credentials and model access must be configured separately.

## Challenges and limits

The household, availability, and arrival records are simulated. The notification and audit record stay inside the demo. No door is unlocked, no real message is sent, and this project has not been connected to a live Alexa+ preview client or Ring device. The MCP server is local-only. The optional Bedrock adapter is included, but Bedrock access was not configured or invoked for this submission.

### Built with

Python, FastAPI, Pydantic, Model Context Protocol (MCP), MCP Python SDK

### Try it out / source

<https://github.com/AnuranjanJain/HomeHandoff>

## Additional information for judges

### Submitter and eligibility

- Submitter type: choose the truthful individual/team option.
- Organization: `N/A` if this is a personal submission.
- Country/province and eligibility confirmations: enter your own truthful information.
- Project status: new (the implementation was created during the hackathon period).

### Track selection

- Primary track: Alexa+ (simulated experience route).
- AWS Builder mini challenge: No. The source contains an optional Bedrock adapter, but an actual AWS service call has not been verified.
- Open Source mini challenge: Yes.

### Code repository

<https://github.com/AnuranjanJain/HomeHandoff>

The repository is public and includes an MIT license.

### Open Source mini challenge

- Contribution URL: <https://github.com/AnuranjanJain/handoff-policy-kit/commit/5cb38f1c72972ce9144b0713faae441b39d0caec>
- Project repository URL: <https://github.com/AnuranjanJain/handoff-policy-kit>
- GitHub username: `AnuranjanJain`
- Description: Created `handoff-policy-kit`, a dependency-free, MIT-licensed Python package for deterministic, consent-based household handoff decisions. It evaluates an event, request, availability, and safe drop-off location to return a recommendation. It cannot send notifications, unlock devices, call a model, or perform network actions. This gives application developers a small policy boundary to run before confirmation or external side effects.

### Project testing instructions

Clone the HomeHandoff repository, then run from its root:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m uvicorn app.main:app --reload
```

Open `http://127.0.0.1:8000`. Choose **Handle the delivery**, review the policy and tool trace, then confirm the simulated notification. Choose **Request access** to see the refusal. All household and device records are fixtures; no external action is performed.

To verify the MCP path, start `python -m app.mcp_server` in a second terminal and run `python scripts/verify_mcp.py` from the repository root.

### Product feedback

**1. Which developer tools, APIs, and SDKs did you use and for what?**

Python, FastAPI, and Pydantic power the simulated web experience, request handling, and typed data contracts. The MCP Python SDK provides the Streamable HTTP server and client verification flow. The repository includes an optional Amazon Bedrock adapter, but no Bedrock request was made, so this submission does not claim an AWS service integration.

**2. For each tool, API, or SDK used, what worked well?**

FastAPI and Pydantic made it practical to create a runnable local experience with explicit data contracts. The MCP Python SDK supported a local Streamable HTTP server; our verifier negotiated protocol version `2025-11-25`, listed the tools, and called `propose_safe_action` successfully.

**3. For each tool, API, or SDK used, what needs work?**

This build did not connect to a remote Alexa+ preview client, so the preview connection and its onboarding remain untested. The local MCP server needs an HTTPS-reachable deployment and any required preview access before that end-to-end path can be evaluated. The Bedrock adapter also needs a locally authenticated AWS profile and enabled model access before its service behavior can be evaluated.

**4. How was your onboarding experience?**

The local Python and FastAPI setup was direct. The MCP client/server flow was verifiable locally with the included script. Signing in to the AWS web console did not authenticate the local app; AWS CLI and a configured local profile were not available on this machine, so Bedrock onboarding could not be completed.

**5. Would you build with these devices and services again?**

Yes. The simulated Alexa+ route and MCP tools were useful for prototyping the interaction and safety boundary. We would continue with the real Alexa+ preview path after obtaining the required access and would keep explicit policy and confirmation checks around any device action.

### Friction log

- Task: determine whether the AWS console sign-in was enough to run the optional local Bedrock path.
- Steps: signed in to the AWS web console, then checked whether AWS CLI was available for local authentication.
- Expected: the local app could use the signed-in AWS account for a Bedrock request.
- Actual: AWS CLI is not installed, so no local profile or Bedrock invocation could be verified. The app remains usable through its deterministic fallback.
- Severity: Medium; this blocks the optional AWS Builder entry but not the Alexa+ simulated demo.
- Workaround: install AWS CLI v2, configure a least-privilege local profile (prefer IAM Identity Center where available), verify identity, enable an on-demand Bedrock model in the selected region, then make and record one real request before changing the track selection.
- Suggestion: provide a short end-to-end guide for local developer authentication, model access, and a first Bedrock request from a Python app.

### AI tools, learning, and career value

List the AI tools you actually used. Suggested learning response to personalize: “I learned to keep model-based intent interpretation separate from deterministic safety policy and to require an explicit confirmation before a simulated side effect.” Answer the career-value question based on your own experience.

### Demo video

Required: publish an English demo video under three minutes and paste its public YouTube or Vimeo URL. The local app URL is not a judge-accessible testing link.
