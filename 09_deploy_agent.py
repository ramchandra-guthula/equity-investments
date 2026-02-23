#!/usr/bin/env python3
"""
Script to deploy Trading Agent to AgentCore Runtime.
"""

import json
import os
from bedrock_agentcore_starter_toolkit import Runtime

# Load all configurations
with open('memory_config.json') as f:
    memory_config = json.load(f)

with open('gateway_config.json') as f:
    gateway_config = json.load(f)

with open('cognito_config.json') as f:
    cognito_config = json.load(f)

with open('runtime_execution_role_config.json') as f:
    role_config = json.load(f)

print("=" * 80)
print("DEPLOYING TRADING AGENT TO AGENTCORE RUNTIME")
print("=" * 80)

# Initialize Runtime
runtime = Runtime()

# Build authorizer configuration
auth_config = {
    "customJWTAuthorizer": {
        "allowedClients": [cognito_config["client_id"]],
        "discoveryUrl": cognito_config["discovery_url"]
    }
}

# Step 1: Configure runtime
print("\nStep 1: Configuring runtime...")
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
print("✓ Runtime configured")

# Step 2: Build environment variables
print("\nStep 2: Preparing environment variables...")
env_vars = {
    "MEMORY_ID": memory_config["memory_id"],
    "GATEWAY_URL": gateway_config["gateway_url"],
    "COGNITO_CLIENT_ID": cognito_config["client_id"],
    "COGNITO_CLIENT_SECRET": cognito_config["client_secret"],
    "COGNITO_DISCOVERY_URL": cognito_config["discovery_url"],
    "OAUTH_SCOPES": "trading-api/read trading-api/write"
}

print("Environment variables:")
for key in env_vars:
    if "SECRET" in key:
        print(f"  {key}: ***")
    else:
        print(f"  {key}: {env_vars[key]}")

# Step 3: Launch agent
print("\n" + "=" * 80)
print("LAUNCHING AGENT TO RUNTIME")
print("=" * 80)
print("\nThis will:")
print("  1. Create CodeBuild project")
print("  2. Build Docker container")
print("  3. Push to ECR")
print("  4. Deploy to AgentCore Runtime")
print("\n⏱️  Expected time: 5-10 minutes")
print("=" * 80)

launch_result = runtime.launch(
    env_vars=env_vars,
    auto_update_on_conflict=True
)

agent_arn = launch_result.agent_arn

# Save runtime config
runtime_output_config = {
    "agent_arn": agent_arn,
    "agent_name": "trading_agent",
    "region": "us-west-2",
    "memory_id": memory_config["memory_id"],
    "gateway_url": gateway_config["gateway_url"]
}

with open('runtime_config.json', 'w') as f:
    json.dump(runtime_output_config, f, indent=2)

print(f"\n✓ Agent deployment initiated!")
print(f"  Agent ARN: {agent_arn}")
print(f"✓ Configuration saved to runtime_config.json")

print("\n" + "=" * 80)
print("NEXT STEPS")
print("=" * 80)
print("\n1. Monitor deployment status:")
print("   python3 10_check_status.py")
print("\n2. Wait for status to show 'READY'")
print("\n3. Test your agent:")
print("   python3 11_test_agent.py")
print("\n" + "=" * 80)
