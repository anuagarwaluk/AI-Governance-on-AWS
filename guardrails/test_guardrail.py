"""Test the guardrail with the workshop's attack and normal prompts.

Uses the ApplyGuardrail API, so the guardrail can be validated on its own
before it is attached to any agent or model.

Usage:
    python test_guardrail.py <guardrail_id> <guardrail_version>
"""

import json
import sys
from pathlib import Path

import boto3

REGION = "us-east-1"


def apply_guardrail(client, guardrail_id: str, version: str, text: str) -> dict:
    return client.apply_guardrail(
        guardrailIdentifier=guardrail_id,
        guardrailVersion=version,
        source="INPUT",
        content=[{"text": {"text": text}}],
    )


def main() -> None:
    if len(sys.argv) != 3:
        sys.exit("Usage: python test_guardrail.py <guardrail_id> <guardrail_version>")

    guardrail_id, version = sys.argv[1], sys.argv[2]
    runtime = boto3.client("bedrock-runtime", region_name=REGION)
    prompts = json.loads((Path(__file__).parent / "attack_prompts.json").read_text())

    for case in prompts["cases"]:
        result = apply_guardrail(runtime, guardrail_id, version, case["prompt"])
        action = result["action"]  # GUARDRAIL_INTERVENED or NONE
        expected = case["expected_action"]
        status = "PASS" if action == expected else "FAIL"
        print(f"[{status}] {case['name']}: action={action} (expected {expected})")
        if action == "GUARDRAIL_INTERVENED":
            for assessment in result.get("assessments", []):
                for topic in assessment.get("topicPolicy", {}).get("topics", []):
                    print(f"         topic hit: {topic['name']} -> {topic['action']}")


if __name__ == "__main__":
    main()
