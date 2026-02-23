#!/usr/bin/env python3
"""
Script to create AgentCore Gateway and register Lambda tools.
Uses MCP tool to generate the script.
"""

import json
import os

# Load configurations
with open('lambda_config.json') as f:
    lambda_config = json.load(f)

with open('cognito_config.json') as f:
    cognito_config = json.load(f)

print("=" * 80)
print("CREATING AGENTCORE GATEWAY")
print("=" * 80)

print("\n⚠️  This script requires MCP tool: mcp_aws_bedrock_agentcore_agentcore_gateway_create")
print("Please run this from Kiro IDE or use the AgentCore CLI")
print("\nManual steps:")
print("1. Create gateway role with Lambda invoke permissions")
print("2. Create gateway with Cognito authentication")
print("3. Add both Lambda functions as targets")
print("\nConfiguration ready:")
print(f"  - Market Data Lambda: {lambda_config['market_data']['function_arn']}")
print(f"  - Notification Lambda: {lambda_config['notification']['function_arn']}")
print(f"  - Cognito Client ID: {cognito_config['client_id']}")
print(f"  - Discovery URL: {cognito_config['discovery_url']}")
