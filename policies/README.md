# Organizations policies for AI governance

Service control policies from module 3 (Organizations Bedrock Policies).
Attach them at the organization root or OU level. They are preventative
controls: they cannot be bypassed by anyone inside the member accounts,
including administrators.

| Policy | What it enforces |
|---|---|
| `scp-enforce-guardrails.json` | Every Bedrock model invocation must carry a guardrail. Uses the `bedrock:GuardrailIdentifier` condition key, so an invocation without a guardrail is denied before the model runs. |
| `scp-restrict-bedrock-regions.json` | Bedrock can only be used in approved regions, which keeps data residency and monitoring scope predictable. |
| `scp-restrict-model-access.json` | Only the approved model list can be invoked. Edit the `NotResource` list to match your organization's approved models. |

Test SCPs in an innovation sandbox OU before attaching them to
production OUs. A guardrail-enforcement SCP applied to an account whose
agents do not yet pass a guardrail identifier will break those agents by
design.
