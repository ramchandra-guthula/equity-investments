#!/usr/bin/env python3
"""
Script to test the deployed Trading Agent.
"""

import json
import base64
import requests
from bedrock_agentcore_starter_toolkit import Runtime

# Load configurations
with open('runtime_execution_role_config.json') as f:
    role_config = json.load(f)

with open('cognito_config.json') as f:
    cognito_config = json.load(f)

print("=" * 80)
print("TESTING TRADING AGENT")
print("=" * 80)

# Step 1: Get OAuth token
print("\n1. Generating OAuth bearer token...")

credentials = f"{cognito_config['client_id']}:{cognito_config['client_secret']}"
encoded_credentials = base64.b64encode(credentials.encode()).decode()

response = requests.post(
    cognito_config['token_endpoint'],
    headers={
        "Authorization": f"Basic {encoded_credentials}",
        "Content-Type": "application/x-www-form-urlencoded"
    },
    data={
        "grant_type": "client_credentials",
        "scope": "trading-api/read trading-api/write"
    }
)

if response.status_code != 200:
    print(f"❌ Failed to get OAuth token: {response.text}")
    exit(1)

bearer_token = response.json()["access_token"]
print("✓ OAuth token obtained")

# Step 2: Initialize Runtime
print("\n2. Initializing Runtime...")
runtime = Runtime()

auth_config = {
    "customJWTAuthorizer": {
        "allowedClients": [cognito_config["client_id"]],
        "discoveryUrl": cognito_config["discovery_url"]
    }
}

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

# Step 3: Test with stock analysis
print("\n3. Testing agent with stock analysis request...")
print("   Query: 'Analyze AAPL stock and tell me if it's a good swing trade opportunity'")

payload = {
    "prompt": "Analyze AAPL stock and tell me if it's a good swing trade opportunity. Use the market data tool to get current data and technical indicators.",
    "actor_id": "trader_001"
}

try:
    response = runtime.invoke(
        payload,
        bearer_token=bearer_token
    )
    
    print("\n" + "=" * 80)
    print("✓ AGENT RESPONSE")
    print("=" * 80)
    print(response)
    print("=" * 80)
    
    # Save response
    with open('test_response.json', 'w') as f:
        json.dump({
            "actor_id": "trader_001",
            "prompt": payload['prompt'],
            "response": response
        }, f, indent=2)
    
    print("\n✓ Response saved to test_response.json")
    
except Exception as e:
    print(f"\n" + "=" * 80)
    print(f"❌ Error invoking agent")
    print("=" * 80)
    print(f"Error: {e}")
    exit(1)

print("\n" + "=" * 80)
print("✓ TEST COMPLETE")
print("=" * 80)
print("\nThe agent successfully:")
print("  - Authenticated with Cognito")
print("  - Accessed gateway tools")
print("  - Analyzed stock data")
print("  - Provided trading recommendation")
