#!/usr/bin/env python3
"""
Script to add Email Notification Lambda target to AgentCore Gateway.
"""

import json
import boto3

# Load gateway configuration
with open('gateway_config.json') as f:
    gateway_config = json.load(f)

# Initialize AgentCore control plane client
gateway_client = boto3.client("bedrock-agentcore-control", region_name='us-west-2')

# Lambda ARN and tool schema
lambda_arn = "arn:aws:lambda:us-west-2:235206763254:function:TradingAgent-EmailNotification"
tool_schema = [
    {
        "name": "send_email_notification",
        "description": "Send email notification for trading alerts and daily summaries",
        "inputSchema": {
            "type": "object",
            "properties": {
                "alert_type": {
                    "type": "string",
                    "description": "Type of alert: high_confidence_opportunity, stop_loss_triggered, take_profit_reached, or daily_summary"
                },
                "data": {
                    "type": "object",
                    "description": "Alert data to include in email (recommendations, prices, etc.)"
                }
            },
            "required": ["alert_type", "data"]
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
print("Adding Email Notification Lambda target to gateway...")
print(f"  Gateway ID: {gateway_config['gateway_id']}")
print(f"  Target Name: EmailNotifier")
print(f"  Lambda ARN: {lambda_arn}")

create_response = gateway_client.create_gateway_target(
    gatewayIdentifier=gateway_config["gateway_id"],
    name="EmailNotifier",
    description="Sends email notifications for trading alerts",
    targetConfiguration=lambda_target_config,
    credentialProviderConfigurations=credential_config
)

target_id = create_response["targetId"]

print(f"\n✓ Lambda target added successfully!")
print(f"  Target ID: {target_id}")
print(f"  Target Name: EmailNotifier")

# Update gateway config
gateway_config["notification_target_id"] = target_id
with open('gateway_config.json', 'w') as f:
    json.dump(gateway_config, f, indent=2)

print(f"✓ Configuration updated")
