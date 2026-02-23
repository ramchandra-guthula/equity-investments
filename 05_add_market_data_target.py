#!/usr/bin/env python3
"""
Script to add Market Data Lambda target to AgentCore Gateway.
"""

import json
import boto3

# Load gateway configuration
with open('gateway_config.json') as f:
    gateway_config = json.load(f)

# Initialize AgentCore control plane client
gateway_client = boto3.client("bedrock-agentcore-control", region_name='us-west-2')

# Lambda ARN and tool schema
lambda_arn = "arn:aws:lambda:us-west-2:235206763254:function:TradingAgent-MarketData"
tool_schema = [
    {
        "name": "analyze_stock",
        "description": "Fetch and analyze stock market data with technical indicators (RSI, MACD, EMA, Bollinger Bands)",
        "inputSchema": {
            "type": "object",
            "properties": {
                "symbol": {
                    "type": "string",
                    "description": "Stock ticker symbol (e.g., AAPL, MSFT, GOOGL)"
                }
            },
            "required": ["symbol"]
        }
    }
]

# Build Lambda target configuration with MCP protocol
lambda_target_config = {
    "mcp": {
        "lambda": {
            "lambdaArn": lambda_arn,
            "toolSchema": {
                "inlinePayload": tool_schema
            }
        }
    }
}

# Use gateway's IAM role for Lambda invocation
credential_config = [{"credentialProviderType": "GATEWAY_IAM_ROLE"}]

# Create target
print("Adding Market Data Lambda target to gateway...")
print(f"  Gateway ID: {gateway_config['gateway_id']}")
print(f"  Target Name: MarketDataAnalyzer")
print(f"  Lambda ARN: {lambda_arn}")

create_response = gateway_client.create_gateway_target(
    gatewayIdentifier=gateway_config["gateway_id"],
    name="MarketDataAnalyzer",
    description="Fetches and analyzes stock market data with technical indicators",
    targetConfiguration=lambda_target_config,
    credentialProviderConfigurations=credential_config
)

target_id = create_response["targetId"]

print(f"\n✓ Lambda target added successfully!")
print(f"  Target ID: {target_id}")
print(f"  Target Name: MarketDataAnalyzer")

# Update gateway config
gateway_config["market_data_target_id"] = target_id
with open('gateway_config.json', 'w') as f:
    json.dump(gateway_config, f, indent=2)

print(f"✓ Configuration updated")
