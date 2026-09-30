"""Enable Amazon Bedrock model invocation logging to CloudWatch.

Module 5 of the workshop. Once enabled, every model invocation in the
region is recorded, including the full request, the response, and the
guardrail assessment when a guardrail intervened.

Usage:
    python enable_model_invocation_logging.py <log_group_name> <logging_role_arn>
"""

import sys

import boto3

REGION = "us-east-1"


def main() -> None:
    if len(sys.argv) != 3:
        sys.exit(
            "Usage: python enable_model_invocation_logging.py "
            "<log_group_name> <logging_role_arn>"
        )
    log_group, role_arn = sys.argv[1], sys.argv[2]

    bedrock = boto3.client("bedrock", region_name=REGION)
    bedrock.put_model_invocation_logging_configuration(
        loggingConfig={
            "cloudWatchConfig": {
                "logGroupName": log_group,
                "roleArn": role_arn,
            },
            "textDataDeliveryEnabled": True,
            "imageDataDeliveryEnabled": False,
            "embeddingDataDeliveryEnabled": False,
        }
    )
    print(f"Model invocation logging enabled -> CloudWatch log group {log_group}")


if __name__ == "__main__":
    main()
