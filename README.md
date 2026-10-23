# HomeHandoff

HomeHandoff is a simulated Alexa+ household experience for consent-based arrival handoffs. It checks a simulated event against household policy, proposes a safe action, requires confirmation before recording a simulated notification, and saves the decision in the demo session.

## What is real and what is simulated

- The FastAPI application, policy engine, typed tool contracts, confirmation flow, refusal path, and audit trail are real and runnable.
- Arrival, household, and availability records are simulated fixtures for the hackathon demo.
- No door unlock, Ring event, or live Alexa+ action is performed.
- The optional Bedrock adapter interprets language only; the local policy engine remains authoritative.
- The optional MCP server exposes the same policy tools through Streamable HTTP.

## Run locally

Requires Python 3.11 or newer.

```powershell
cd outputs/homehandoff
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m uvicorn app.main:app --reload
```

Open <http://127.0.0.1:8000>.

## Optional AWS Builder path

An AWS console login does not automatically provide credentials to this local app. Install AWS CLI v2, configure a least-privilege IAM Identity Center profile if your AWS account supports it, and verify local access with `aws sts get-caller-identity --profile homehandoff`. Then check that Amazon Bedrock and an on-demand model are available in the selected region. Choose the exact model ID from the Bedrock console and set the three environment variables below. The app falls back to the deterministic parser when the model is not configured or the provider fails, and shows which path handled the request.

```powershell
$env:AWS_PROFILE="homehandoff"
$env:AWS_REGION="us-east-1"
$env:BEDROCK_MODEL_ID="<model-id-from-bedrock-console>"
python -m uvicorn app.main:app --reload
```

Do not use root access keys or put any access keys in `.env`, source code, or GitHub. Bedrock permissions must allow `bedrock:InvokeModel` for the selected model. The AWS Builder entry requires an actual AWS service integration, so include this track only after you have run one request and the UI trace says `Amazon Bedrock`. Record the service, model, region, and observed onboarding friction.

## Optional Alexa+ MCP path

The MCP server uses the official Python SDK and Streamable HTTP. It exposes the same consent-first tools used by the web simulation.

```powershell
python -m app.mcp_server
```

In a second terminal, run `python scripts/verify_mcp.py`. It connects using the official MCP client, reports the negotiated protocol, lists tools, and calls the safe-action tool. The endpoint is `http://127.0.0.1:8001/mcp`; it is local-only and uses MCP protocol version `2025-11-25` through `mcp>=1.30,<2`. The MCP server prepares recommendations and notification drafts; it does not connect to an Amazon household or send messages. To connect a remote Alexa+ preview client, the server would need an HTTPS-reachable host and any preview access required by Amazon.

## Demo path

1. Use **Handle the delivery** or enter: `I am on a call. Handle the delivery safely.`
2. Review the event, policy checks, tool trace, and recommendation.
3. Click **Confirm simulated notification**.
4. Use **Request access** to show that automatic unlocking is refused.
5. Use **Reset scenario** to replay the flow.

## Future adapters

The simulated data adapter is isolated from the policy rules. The included MCP server exposes the current simulated tools. Any future live device adapter must preserve explicit confirmation for high-risk actions.
