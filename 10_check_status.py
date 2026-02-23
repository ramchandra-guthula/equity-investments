#!/usr/bin/env python3
"""
Script to check Trading Agent deployment status.
"""

import json
from bedrock_agentcore_starter_toolkit import Runtime

# Load configurations
with open('runtime_execution_role_config.json') as f:
    role_config = json.load(f)

with open('cognito_config.json') as f:
    cognito_config = json.load(f)

# Initialize Runtime
runtime = Runtime()

# Build authorizer configuration
auth_config = {
    "customJWTAuthorizer": {
        "allowedClients": [cognito_config["client_id"]],
        "discoveryUrl": cognito_config["discovery_url"]
    }
}

# Configure runtime
print("Loading runtime configuration...")
runtime.configure(
    entrypoint="trading_agent.py",
    agent_name="trading_agent",
    execution_role=role_config["role_arn"],
    auto_create_ecr=True,
    memory_mode="NO_MEMORY",
    requirements_file="requirements.txt",
    region="us-west-2",
    authorizer_configuration=auth_config
)

# Check status
print("Checking runtime deployment status...")
status_response = runtime.status()

status = status_response.endpoint["status"]

print(f"\nAgent Status: {status}")
print(f"Endpoint Details: {json.dumps(status_response.endpoint, indent=2, default=str)}")

if status == "READY":
    print("\n" + "=" * 80)
    print("✓ Agent is READY to receive requests!")
    print("=" * 80)
    print("\nYou can now test your agent with:")
    print("  python3 11_test_agent.py")
elif status in ["CREATING", "UPDATING"]:
    print("\n" + "=" * 80)
    print("⏳ Agent deployment in progress...")
    print("=" * 80)
    print("\nRun this script again in 1-2 minutes to check status.")
elif status in ["CREATE_FAILED", "UPDATE_FAILED"]:
    print("\n" + "=" * 80)
    print("✗ Agent deployment failed!")
    print("=" * 80)
    print("\nCheck CloudWatch logs for details")
else:
    print(f"\n⚠ Unknown status: {status}")
