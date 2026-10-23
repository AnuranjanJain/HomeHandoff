from __future__ import annotations

import json
import os
from dataclasses import dataclass
from typing import Any

from dotenv import load_dotenv

from app.domain.policy import Intent

try:
    import boto3
except ImportError:  # Optional until AWS access is configured.
    boto3 = None

load_dotenv()


@dataclass(frozen=True)
class InterpretationResult:
    intent: Intent | None
    provider: str
    error: str | None = None


class BedrockIntentInterpreter:
    """Uses Bedrock only for intent extraction; policy decisions stay local."""

    def __init__(self, model_id: str | None = None, region: str | None = None, profile: str | None = None) -> None:
        self.model_id = model_id or os.getenv("BEDROCK_MODEL_ID", "").strip()
        self.region = region or os.getenv("AWS_REGION", "us-east-1").strip()
        self.profile = profile or os.getenv("AWS_PROFILE", "").strip() or None

    @property
    def configured(self) -> bool:
        return bool(self.model_id and boto3 is not None)

    def interpret(self, message: str) -> InterpretationResult:
        if not self.configured:
            return InterpretationResult(intent=None, provider="deterministic fallback")

        try:
            session = boto3.Session(profile_name=self.profile, region_name=self.region)
            client = session.client("bedrock-runtime", region_name=self.region)
            response = client.converse(
                modelId=self.model_id,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "text": (
                                    "Classify this household request as exactly one JSON object with an intent "
                                    "of safe_delivery, visitor_check, unsafe_access, or ambiguous. "
                                    f"Request: {message}"
                                )
                            }
                        ],
                    }
                ],
                inferenceConfig={"maxTokens": 60, "temperature": 0},
            )
            text = response["output"]["message"]["content"][0]["text"]
            payload = self._parse_json(text)
            intent = payload.get("intent")
            if intent not in {"safe_delivery", "visitor_check", "unsafe_access", "ambiguous"}:
                raise ValueError("Bedrock returned an unsupported intent.")
            return InterpretationResult(intent=intent, provider="Amazon Bedrock")  # type: ignore[arg-type]
        except Exception as exc:  # Provider failures must fall back without exposing credentials.
            return InterpretationResult(intent=None, provider="deterministic fallback", error=type(exc).__name__)

    @staticmethod
    def _parse_json(text: str) -> dict[str, Any]:
        cleaned = text.strip()
        if cleaned.startswith("```"):
            cleaned = cleaned.strip("`").removeprefix("json").strip()
        payload = json.loads(cleaned)
        if not isinstance(payload, dict):
            raise ValueError("Bedrock returned a non-object response.")
        return payload
