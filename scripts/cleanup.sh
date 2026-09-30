#!/usr/bin/env bash
# Remove all billable workshop resources. Run when you finish.
set -uo pipefail

REGION="${AWS_DEFAULT_REGION:-us-east-1}"

echo "== Deleting AgentCore runtime =="
RUNTIME_ID=$(aws bedrock-agentcore-control list-agent-runtimes --region "$REGION" \
  --query "agentRuntimes[?agentRuntimeName=='rewards_assistant'].agentRuntimeId" --output text)
if [ -n "$RUNTIME_ID" ] && [ "$RUNTIME_ID" != "None" ]; then
  aws bedrock-agentcore-control delete-agent-runtime \
    --agent-runtime-id "$RUNTIME_ID" --region "$REGION"
  echo "Deleted runtime $RUNTIME_ID"
fi

echo "== Deleting guardrail =="
GUARDRAIL_ID=$(aws bedrock list-guardrails --region "$REGION" \
  --query "guardrails[?name=='rewards-assistant-guardrail'].id" --output text)
if [ -n "$GUARDRAIL_ID" ] && [ "$GUARDRAIL_ID" != "None" ]; then
  aws bedrock delete-guardrail --guardrail-identifier "$GUARDRAIL_ID" --region "$REGION"
  echo "Deleted guardrail $GUARDRAIL_ID"
fi

echo "== Deleting conformance packs =="
for PACK in aiml-infra-best-practices bedrock-security-governance \
            sagemaker-security-governance self-hosted-aiml-best-practices; do
  aws configservice delete-conformance-pack \
    --conformance-pack-name "$PACK" --region "$REGION" 2>/dev/null \
    && echo "Deleted conformance pack $PACK"
done

echo "== Disabling model invocation logging =="
aws bedrock delete-model-invocation-logging-configuration --region "$REGION" 2>/dev/null

echo "Cleanup complete. Verify in the console: AgentCore, Bedrock Guardrails, AWS Config."
