"""Custom AWS Config rule: every AgentCore runtime must carry a guardrail.

Lambda handler for a periodic custom Config rule. It lists Bedrock
AgentCore agent runtimes in the account and marks each runtime
NON_COMPLIANT unless its latest version defines a GUARDRAIL_ID
environment variable. This is the "guardrail compliance check" from the
workshop's AI governance dashboard: guardrails become something you can
prove, not something you assume.

Deploy as a Lambda function and register it as a custom Config rule with
a periodic trigger (for example every 24 hours).
"""

import json

import boto3

config = boto3.client("config")
agentcore = boto3.client("bedrock-agentcore-control")


def evaluate_runtime(runtime: dict) -> tuple[str, str]:
    """Return (compliance_type, annotation) for one agent runtime."""
    detail = agentcore.get_agent_runtime(agentRuntimeId=runtime["agentRuntimeId"])
    env = detail.get("environmentVariables", {}) or {}
    if env.get("GUARDRAIL_ID"):
        return "COMPLIANT", "Guardrail attached via GUARDRAIL_ID"
    return "NON_COMPLIANT", "No GUARDRAIL_ID environment variable on runtime"


def lambda_handler(event, context):
    result_token = event["resultToken"]
    ordering_ts = json.loads(event["invokingEvent"])["notificationCreationTime"]

    evaluations = []
    paginator = agentcore.get_paginator("list_agent_runtimes")
    for page in paginator.paginate():
        for runtime in page.get("agentRuntimes", []):
            compliance, annotation = evaluate_runtime(runtime)
            evaluations.append(
                {
                    "ComplianceResourceType": "AWS::::Account",
                    "ComplianceResourceId": runtime["agentRuntimeId"],
                    "ComplianceType": compliance,
                    "Annotation": annotation,
                    "OrderingTimestamp": ordering_ts,
                }
            )

    for i in range(0, len(evaluations), 100):
        config.put_evaluations(
            Evaluations=evaluations[i : i + 100], ResultToken=result_token
        )
    return {"evaluations": len(evaluations)}
