#!/usr/bin/env python3
"""
Script to create IAM execution role for AgentCore Runtime.
"""

import json
import boto3
import time

iam_client = boto3.client('iam')
sts_client = boto3.client('sts')

ROLE_NAME = f'TradingAgentRuntimeRole-{int(time.time())}'
POLICY_NAME = f'TradingAgentRuntimePolicy-{int(time.time())}'
account_id = sts_client.get_caller_identity()['Account']
REGION = 'us-west-2'

print("=" * 80)
print("CREATING RUNTIME EXECUTION ROLE")
print("=" * 80)

# Step 1: Create role
print("\nStep 1: Creating IAM role...")

trust_policy = {
    "Version": "2012-10-17",
    "Statement": [{
        "Effect": "Allow",
        "Principal": {"Service": "bedrock-agentcore.amazonaws.com"},
        "Action": "sts:AssumeRole"
    }]
}

try:
    role_response = iam_client.create_role(
        RoleName=ROLE_NAME,
        AssumeRolePolicyDocument=json.dumps(trust_policy),
        Description='Execution role for Trading Agent Runtime'
    )
    role_arn = role_response['Role']['Arn']
    print(f"✓ Role created: {role_arn}")
    time.sleep(10)
except Exception as e:
    print(f"❌ Error: {e}")
    exit(1)

# Step 2: Create comprehensive policy
print("\nStep 2: Creating permissions policy...")

permissions_policy = {
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "BedrockModelAccess",
            "Effect": "Allow",
            "Action": [
                "bedrock:InvokeModel",
                "bedrock:InvokeModelWithResponseStream"
            ],
            "Resource": [
                "arn:aws:bedrock:*::foundation-model/*",
                f"arn:aws:bedrock:{REGION}:{account_id}:*"
            ]
        },
        {
            "Sid": "AgentCoreMemoryAccess",
            "Effect": "Allow",
            "Action": [
                "bedrock-agentcore:CreateEvent",
                "bedrock-agentcore:ListEvents",
                "bedrock-agentcore:GetMemoryRecord",
                "bedrock-agentcore:GetMemory",
                "bedrock-agentcore:RetrieveMemoryRecords",
                "bedrock-agentcore:ListMemoryRecords"
            ],
            "Resource": f"arn:aws:bedrock-agentcore:{REGION}:{account_id}:*"
        },
        {
            "Sid": "CloudWatchLogsAccess",
            "Effect": "Allow",
            "Action": [
                "logs:CreateLogGroup",
                "logs:CreateLogStream",
                "logs:PutLogEvents"
            ],
            "Resource": f"arn:aws:logs:{REGION}:{account_id}:log-group:/aws/bedrock-agentcore/*"
        },
        {
            "Sid": "XRayAccess",
            "Effect": "Allow",
            "Action": [
                "xray:PutTraceSegments",
                "xray:PutTelemetryRecords"
            ],
            "Resource": "*"
        },
        {
            "Sid": "ECRAccess",
            "Effect": "Allow",
            "Action": [
                "ecr:GetAuthorizationToken",
                "ecr:BatchCheckLayerAvailability",
                "ecr:GetDownloadUrlForLayer",
                "ecr:BatchGetImage"
            ],
            "Resource": "*"
        },
        {
            "Sid": "SSMParameterAccess",
            "Effect": "Allow",
            "Action": "ssm:GetParameter",
            "Resource": f"arn:aws:ssm:{REGION}:{account_id}:parameter/trading-agent/*"
        }
    ]
}

try:
    policy_response = iam_client.create_policy(
        PolicyName=POLICY_NAME,
        PolicyDocument=json.dumps(permissions_policy),
        Description='Permissions for Trading Agent Runtime'
    )
    policy_arn = policy_response['Policy']['Arn']
    print(f"✓ Policy created: {policy_arn}")
except Exception as e:
    print(f"❌ Error: {e}")
    iam_client.delete_role(RoleName=ROLE_NAME)
    exit(1)

# Step 3: Attach policy
print("\nStep 3: Attaching policy to role...")

try:
    iam_client.attach_role_policy(
        RoleName=ROLE_NAME,
        PolicyArn=policy_arn
    )
    print("✓ Policy attached")
except Exception as e:
    print(f"❌ Error: {e}")
    exit(1)

# Save configuration
config = {
    "role_name": ROLE_NAME,
    "role_arn": role_arn,
    "policy_arn": policy_arn,
    "region": REGION
}

with open('runtime_execution_role_config.json', 'w') as f:
    json.dump(config, f, indent=2)

print("\n✓ Configuration saved to runtime_execution_role_config.json")

print("\n" + "=" * 80)
print("✓ RUNTIME EXECUTION ROLE CREATED SUCCESSFULLY")
print("=" * 80)
print(f"\nRole ARN: {role_arn}")
print("\nNext step: Deploy agent to runtime")
