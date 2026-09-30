#!/usr/bin/env bash
# Deploy the AI/ML conformance packs used in module 4 of the workshop.
# Each pack is a bundle of AWS Config rules deployed and scored as one unit.
set -euo pipefail

REGION="${AWS_DEFAULT_REGION:-us-east-1}"

deploy () {
  local name="$1" template="$2"
  echo "Deploying conformance pack: ${name}"
  aws configservice put-conformance-pack \
    --conformance-pack-name "${name}" \
    --template-body "file://${template}" \
    --region "${REGION}"
}

deploy "aiml-infra-best-practices" "conformance-pack-aiml-infra.yaml"

echo "Deployment started. Compliance scores appear in the AWS Config console"
echo "under Conformance packs once the initial evaluation completes."
