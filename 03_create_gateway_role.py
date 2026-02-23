#!/usr/bin/env python3
"""
Script to create IAM role for AgentCore Gateway.
"""

import json
import boto3
import time

iam_client = boto3.client('iam')
sts_client = boto3.client('sts')

ROLE_NAME = f'TradingAgentGatewayRole-{int(time.time())}'
account_id = sts_client.get_caller_identity()['Account']

print("=" * 80)
print("CREATING GATEWAY IAM ROLE")
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
        Description='Role for Trading Agent Gateway to invoke Lambda functions'
    )
    role_arn = role_response['Role']['Arn']
    print(f"✓ Role created: {role_arn}")
    time.sleep(10)
except Exception as e:
    print(f"❌ Error: {e}")
    exit(1)

# Step 2: Create policy
print("\nStep 2: Creating Lambda invoke policy...")

policy_document = {
    "Version": "2012-10-17",
    "Statement": [{
        "Effect": "Allow",
        "Action": "lambda:InvokeFunction",
        "Resource": [
            f"arn:aws:lambda:us-west-2:{account_id}:function:TradingAgent-*"
        ]
    }]
}

policy_name = f'TradingAgentGatewayPolicy-{int(time.time())}'

try:
    policy_response = iam_client.create_policy(
        PolicyName=policy_name,
        PolicyDocument=json.dumps(policy_document),
        Description='Allows gateway to invoke trading agent Lambda functions'
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
    "region": "us-west-2"
}

with open('gateway_role_config.json', 'w') as f:
    json.dump(config, f, indent=2)

print("\n✓ Configuration saved to gateway_role_config.json")

print("\n" + "=" * 80)
print("✓ GATEWAY ROLE CREATED SUCCESSFULLY")
print("=" * 80)
print(f"\nRole ARN: {role_arn}")
print("\nNext step: Create gateway")
