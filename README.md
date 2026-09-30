# AI Governance on AWS: Attack, Govern, Prove

I attacked my own AI agent, then governed it. This repository is the full build from the AWS **AI Governance on AWS** workshop, completed hands on as part of BeSA Cohort 10 (week 6). It covers the complete governance lifecycle: an ungoverned agent falling for a prompt injection, the guardrails that stop the same attack, the Organizations policies that make guardrails mandatory, the AWS Config rules that prove the controls are working, and the observability that shows every intervention.

![Architecture](diagrams/ai-governance-architecture.png)

## The story in three screenshots

**1. The attack succeeds.** The ungoverned rewards assistant receives a prompt claiming to be from a system administrator, confirming a fraudulent 500,000-point "Founders Legacy" reward. The agent complies and echoes the customer's card details back. All data in this demo is synthetic.

![Prompt injection succeeds](screenshots/05-prompt-injection-succeeds.png)

**2. A guardrail is applied.** An Amazon Bedrock guardrail with a denied topic for admin-override attempts, a prompt attack filter, and PII masking is attached to the same agent through a single environment variable. No agent code changes.

![Denied topic configuration](screenshots/06-guardrail-denied-topic-admin-override.png)

**3. The same attack fails.** The identical injection prompt now returns one line: "Sorry, the model cannot answer this question." The request is blocked before the model runs, and the intervention is recorded as a `guardrail_intervened` event in observability.

![Guardrail blocks the injection](screenshots/11-guardrail-blocks-injection.png)

## What is in this repository

```
ai-governance-on-aws/
├── agent/
│   ├── rewards_assistant.py            # The agent on AgentCore Runtime (guardrail via env var)
│   └── requirements.txt
├── guardrails/
│   ├── create_guardrail.py             # Denied topic + prompt attack filter + PII masking
│   ├── test_guardrail.py               # ApplyGuardrail tests: injection blocked, normal traffic passes
│   └── attack_prompts.json             # The workshop's attack and normal prompts
├── policies/
│   ├── scp-enforce-guardrails.json     # Deny Bedrock invocation without a guardrail
│   ├── scp-restrict-bedrock-regions.json
│   ├── scp-restrict-model-access.json  # Approved-model allow list
│   └── README.md
├── governance/
│   ├── deploy_conformance_packs.sh     # AWS Config conformance packs
│   ├── conformance-pack-aiml-infra.yaml
│   └── config_rule_guardrail_compliance.py  # Custom rule: every runtime must carry a guardrail
├── observability/
│   ├── enable_model_invocation_logging.py
│   └── logs_insights_queries.md        # guardrail_intervened, CloudTrail and intervention-rate queries
├── diagrams/
│   └── ai-governance-architecture.png
├── screenshots/                        # 15 redacted console captures of the full build
├── scripts/
│   └── cleanup.sh                      # Remove every billable resource
└── docs/
    └── walkthrough.md                  # Module-by-module notes and gotchas
```

## The five layers

| Layer | Service | What it does here |
|---|---|---|
| Govern | AWS Organizations | Multi-account strategy, an innovation sandbox OU, and service control policies that make guardrails, approved models and approved regions non-negotiable |
| Protect | Amazon Bedrock Guardrails | Denied topic for admin-override attempts, prompt attack detection on input, PII anonymisation on output |
| Run | Amazon Bedrock AgentCore Runtime | The rewards assistant, one microVM per session, guardrail attached through `GUARDRAIL_ID` |
| Prove | AWS Config + Security Hub | Custom rules and conformance packs score compliance continuously; Security Hub AI inventory discovers every AI resource in the account |
| Observe | AgentCore Observability + CloudWatch + CloudTrail | OpenTelemetry traces of every reasoning step, `guardrail_intervened` events, full model invocation logs, API-level audit trail |

## Why defence in depth

Guardrails are probabilistic. They catch the attacks they were trained and configured to catch, which is why they are one layer rather than the whole answer. The deterministic layers around them do the rest: SCPs that no workload can bypass, Config rules that flag drift, and logging that proves what happened. The workshop's compliance scores make the point honestly. The first conformance pack evaluation came back at 30 to 38 percent compliant, which is not a failure. It is a baseline, and a baseline is where governance starts.

## Running it yourself

Prerequisites: an AWS account with Amazon Bedrock model access enabled in your region, Python 3.10+, and the AWS CLI configured.

```bash
pip install -r agent/requirements.txt

# 1. Create the guardrail and note the returned ID and version
python guardrails/create_guardrail.py

# 2. Prove it works before touching any agent
python guardrails/test_guardrail.py <guardrail_id> <version>

# 3. Deploy the agent to AgentCore Runtime (agentcore CLI), first without
#    GUARDRAIL_ID to see the ungoverned behaviour, then update the runtime
#    with GUARDRAIL_ID and GUARDRAIL_VERSION set

# 4. Deploy the compliance layer
cd governance && ./deploy_conformance_packs.sh

# 5. Turn on model invocation logging
python observability/enable_model_invocation_logging.py <log_group> <role_arn>
```

When you finish:

```bash
./scripts/cleanup.sh
```

The workshop runs comfortably in an afternoon and cost me only a few dollars of consumption-based usage. Cleanup matters because conformance pack evaluations and stored logs continue to bill.

*Built and measured by Anu Agarwal — [linkedin.com/in/agarwalanu](https://www.linkedin.com/in/agarwalanu)*

<img width="732" height="56" alt="image" src="https://github.com/user-attachments/assets/6d6d2775-4fcf-45af-a872-aa3b19b7db72" />
