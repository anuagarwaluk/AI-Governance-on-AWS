# CloudWatch Logs Insights queries for AI governance

Queries used in module 5 (Agent Observability). Together they answer the
question an auditor asks first: what did the agent do, and did the
controls fire?

## 1. Guardrail interventions in model invocation logs

Run against the Bedrock model invocation log group. Every intervention
is a control that worked, recorded with its timestamp and reason.

```
fields @timestamp, modelId, output.outputBodyJson.amazon-bedrock-guardrailAction as guardrailAction
| filter output.outputBodyJson.amazon-bedrock-guardrailAction = "INTERVENED"
| sort @timestamp desc
| limit 50
```

## 2. Guardrail intervention spans in AgentCore observability

Run against the AgentCore runtime's observability log group. AgentCore
emits OpenTelemetry spans for every reasoning step, model call and tool
invocation; guardrail interventions appear as `guardrail_intervened`
events tied to a session.

```
fields @timestamp, @message
| filter @message like /guardrail_intervened/
| sort @timestamp desc
| limit 50
```

## 3. Who invoked the model (CloudTrail)

Run against your CloudTrail log group. CloudTrail gives the API-level
record: identity, source IP, time. AgentCore observability gives the
reasoning-level record. Governance needs both, because "who called the
API" and "why the agent did what it did" are different questions.

```
fields @timestamp, userIdentity.arn, eventName, awsRegion
| filter eventSource = "bedrock.amazonaws.com" and eventName like /InvokeModel/
| sort @timestamp desc
| limit 50
```

## 4. Intervention rate over time

A rising intervention rate means either an attack in progress or a
guardrail that is too aggressive. Either way, someone should look.

```
fields @timestamp
| filter @message like /guardrail_intervened/
| stats count() as interventions by bin(1h)
```
