#!/usr/bin/env python3
"""
Script to create Lambda functions for trading agent.
Creates:
1. Market Data Lambda - Fetches and analyzes stock data
2. Email Notification Lambda - Sends trading alerts
"""

import json
import os
import zipfile
import boto3
import time
from io import BytesIO

# Initialize clients
lambda_client = boto3.client('lambda', region_name='us-west-2')
iam_client = boto3.client('iam')
ssm_client = boto3.client('ssm')
sts_client = boto3.client('sts')

# Get account ID
account_id = sts_client.get_caller_identity()['Account']

print("=" * 80)
print("CREATING LAMBDA FUNCTIONS FOR TRADING AGENT")
print("=" * 80)

# Step 1: Store secrets in Parameter Store
print("\nStep 1: Storing secrets in AWS Systems Manager Parameter Store...")

# Get secrets from environment or prompt
alpha_vantage_key = os.environ.get('ALPHA_VANTAGE_API_KEY')
notification_email = os.environ.get('NOTIFICATION_EMAIL')

if not alpha_vantage_key:
    print("⚠️  ALPHA_VANTAGE_API_KEY not found in environment")
    print("   Please set it: export ALPHA_VANTAGE_API_KEY=your_key")
    exit(1)

if not notification_email:
    print("⚠️  NOTIFICATION_EMAIL not found in environment")
    print("   Please set it: export NOTIFICATION_EMAIL=your_email@example.com")
    exit(1)

try:
    # Store Alpha Vantage API key
    ssm_client.put_parameter(
        Name='/trading-agent/alpha-vantage-api-key',
        Value=alpha_vantage_key,
        Type='SecureString',
        Overwrite=True,
        Description='Alpha Vantage API key for market data'
    )
    print("✓ Stored Alpha Vantage API key in Parameter Store")
    
    # Store notification email
    ssm_client.put_parameter(
        Name='/trading-agent/notification-email',
        Value=notification_email,
        Type='String',
        Overwrite=True,
        Description='Email address for trading notifications'
    )
    print("✓ Stored notification email in Parameter Store")
    
except Exception as e:
    print(f"❌ Error storing parameters: {e}")
    exit(1)

# Step 2: Create IAM role for Lambda functions
print("\nStep 2: Creating IAM role for Lambda functions...")

lambda_role_name = 'TradingAgentLambdaRole'
trust_policy = {
    "Version": "2012-10-17",
    "Statement": [{
        "Effect": "Allow",
        "Principal": {"Service": "lambda.amazonaws.com"},
        "Action": "sts:AssumeRole"
    }]
}

try:
    # Try to create role
    role_response = iam_client.create_role(
        RoleName=lambda_role_name,
        AssumeRolePolicyDocument=json.dumps(trust_policy),
        Description='Role for Trading Agent Lambda functions'
    )
    role_arn = role_response['Role']['Arn']
    print(f"✓ Created IAM role: {role_arn}")
    
    # Wait for role to be available
    time.sleep(10)
    
except iam_client.exceptions.EntityAlreadyExistsException:
    role_response = iam_client.get_role(RoleName=lambda_role_name)
    role_arn = role_response['Role']['Arn']
    print(f"✓ Using existing IAM role: {role_arn}")

# Attach policies
policies_to_attach = [
    'arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole',
    'arn:aws:iam::aws:policy/AmazonSSMReadOnlyAccess',
    'arn:aws:iam::aws:policy/AmazonSESFullAccess'
]

for policy_arn in policies_to_attach:
    try:
        iam_client.attach_role_policy(
            RoleName=lambda_role_name,
            PolicyArn=policy_arn
        )
        print(f"✓ Attached policy: {policy_arn.split('/')[-1]}")
    except Exception as e:
        if 'already attached' not in str(e).lower():
            print(f"⚠️  Warning attaching policy: {e}")

# Step 3: Create Market Data Lambda
print("\nStep 3: Creating Market Data Lambda function...")

def create_lambda_zip(filename):
    """Create a zip file for Lambda deployment"""
    zip_buffer = BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        zip_file.write(filename, os.path.basename(filename))
    zip_buffer.seek(0)
    return zip_buffer.read()

market_data_function_name = 'TradingAgent-MarketData'

try:
    # Create zip file
    zip_content = create_lambda_zip('lambda_market_data.py')
    
    # Create or update function
    try:
        lambda_client.create_function(
            FunctionName=market_data_function_name,
            Runtime='python3.12',
            Role=role_arn,
            Handler='lambda_market_data.lambda_handler',
            Code={'ZipFile': zip_content},
            Description='Fetches and analyzes stock market data',
            Timeout=30,
            MemorySize=256
        )
        print(f"✓ Created Lambda function: {market_data_function_name}")
    except lambda_client.exceptions.ResourceConflictException:
        lambda_client.update_function_code(
            FunctionName=market_data_function_name,
            ZipFile=zip_content
        )
        print(f"✓ Updated Lambda function: {market_data_function_name}")
    
    # Get function ARN
    market_data_response = lambda_client.get_function(FunctionName=market_data_function_name)
    market_data_arn = market_data_response['Configuration']['FunctionArn']
    
except Exception as e:
    print(f"❌ Error creating market data Lambda: {e}")
    exit(1)

# Step 4: Create Email Notification Lambda
print("\nStep 4: Creating Email Notification Lambda function...")

notification_function_name = 'TradingAgent-EmailNotification'

try:
    # Create zip file
    zip_content = create_lambda_zip('lambda_notification.py')
    
    # Create or update function
    try:
        lambda_client.create_function(
            FunctionName=notification_function_name,
            Runtime='python3.12',
            Role=role_arn,
            Handler='lambda_notification.lambda_handler',
            Code={'ZipFile': zip_content},
            Description='Sends email notifications for trading alerts',
            Timeout=30,
            MemorySize=256
        )
        print(f"✓ Created Lambda function: {notification_function_name}")
    except lambda_client.exceptions.ResourceConflictException:
        lambda_client.update_function_code(
            FunctionName=notification_function_name,
            ZipFile=zip_content
        )
        print(f"✓ Updated Lambda function: {notification_function_name}")
    
    # Get function ARN
    notification_response = lambda_client.get_function(FunctionName=notification_function_name)
    notification_arn = notification_response['Configuration']['FunctionArn']
    
except Exception as e:
    print(f"❌ Error creating notification Lambda: {e}")
    exit(1)

# Step 5: Verify SES email
print("\nStep 5: Verifying email address in Amazon SES...")
print(f"   Email: {notification_email}")

ses_client = boto3.client('ses', region_name='us-west-2')

try:
    # Check if email is already verified
    response = ses_client.get_identity_verification_attributes(
        Identities=[notification_email]
    )
    
    status = response['VerificationAttributes'].get(notification_email, {}).get('VerificationStatus')
    
    if status == 'Success':
        print("✓ Email already verified in SES")
    else:
        # Send verification email
        ses_client.verify_email_identity(EmailAddress=notification_email)
        print("📧 Verification email sent!")
        print(f"   Please check {notification_email} and click the verification link")
        print("   You must verify before emails can be sent")
        
except Exception as e:
    print(f"⚠️  Warning: {e}")
    print("   You may need to verify your email manually in SES console")

# Step 6: Save configuration
print("\nStep 6: Saving Lambda configuration...")

lambda_config = {
    "market_data": {
        "function_name": market_data_function_name,
        "function_arn": market_data_arn,
        "tool_schema": [{
            "name": "analyze_stock",
            "description": "Fetch and analyze stock market data with technical indicators",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "symbol": {
                        "type": "string",
                        "description": "Stock ticker symbol (e.g., AAPL, MSFT)"
                    }
                },
                "required": ["symbol"]
            }
        }]
    },
    "notification": {
        "function_name": notification_function_name,
        "function_arn": notification_arn,
        "tool_schema": [{
            "name": "send_email_notification",
            "description": "Send email notification for trading alerts",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "alert_type": {
                        "type": "string",
                        "enum": ["high_confidence_opportunity", "stop_loss_triggered", "take_profit_reached", "daily_summary"],
                        "description": "Type of alert to send"
                    },
                    "data": {
                        "type": "object",
                        "description": "Alert data to include in email"
                    }
                },
                "required": ["alert_type", "data"]
            }
        }]
    },
    "role_arn": role_arn,
    "region": "us-west-2"
}

with open('lambda_config.json', 'w') as f:
    json.dump(lambda_config, f, indent=2)

print("✓ Configuration saved to lambda_config.json")

print("\n" + "=" * 80)
print("✓ LAMBDA FUNCTIONS CREATED SUCCESSFULLY")
print("=" * 80)
print(f"\nMarket Data Lambda: {market_data_arn}")
print(f"Notification Lambda: {notification_arn}")
print(f"\nNext steps:")
print("  1. Verify your email in SES (check inbox)")
print("  2. Run: python3 02_create_cognito.py")
