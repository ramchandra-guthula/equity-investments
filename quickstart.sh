#!/bin/bash

# Trading Agent - Quick Start Script
# This script sets up the complete infrastructure

set -e  # Exit on error

echo "================================================================================"
echo "TRADING AGENT - QUICK START"
echo "================================================================================"

# Check if running from correct directory
if [ ! -f "lambda_market_data.py" ]; then
    echo "❌ Error: Please run this script from the equity-investments directory"
    exit 1
fi

# Check for required environment variables
if [ -z "$ALPHA_VANTAGE_API_KEY" ]; then
    echo "❌ Error: ALPHA_VANTAGE_API_KEY not set"
    echo "   Please run: export ALPHA_VANTAGE_API_KEY=your_key"
    exit 1
fi

if [ -z "$NOTIFICATION_EMAIL" ]; then
    echo "❌ Error: NOTIFICATION_EMAIL not set"
    echo "   Please run: export NOTIFICATION_EMAIL=your_email@example.com"
    exit 1
fi

echo "✓ Environment variables configured"
echo "  API Key: ${ALPHA_VANTAGE_API_KEY:0:10}..."
echo "  Email: $NOTIFICATION_EMAIL"
echo ""

# Check Python version
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "✓ Python version: $python_version"

# Check AWS CLI
if ! command -v aws &> /dev/null; then
    echo "❌ Error: AWS CLI not found"
    echo "   Please install: https://aws.amazon.com/cli/"
    exit 1
fi

echo "✓ AWS CLI installed"

# Check AWS credentials
if ! aws sts get-caller-identity &> /dev/null; then
    echo "❌ Error: AWS credentials not configured"
    echo "   Please run: aws configure"
    exit 1
fi

account_id=$(aws sts get-caller-identity --query Account --output text)
echo "✓ AWS credentials configured (Account: $account_id)"
echo ""

# Install Python dependencies
echo "Installing Python dependencies..."
pip3 install -q boto3 requests pyyaml 2>/dev/null || true
echo "✓ Dependencies installed"
echo ""

# Run setup scripts
echo "================================================================================"
echo "STEP 1: Creating Lambda Functions"
echo "================================================================================"
python3 01_create_lambdas.py

echo ""
echo "================================================================================"
echo "STEP 2: Creating Cognito User Pool"
echo "================================================================================"
python3 02_create_cognito.py

echo ""
echo "================================================================================"
echo "✓ INFRASTRUCTURE SETUP COMPLETE"
echo "================================================================================"
echo ""
echo "Next steps:"
echo "  1. Check your email ($NOTIFICATION_EMAIL) and verify SES"
echo "  2. Create AgentCore Gateway (requires MCP tool or manual setup)"
echo "  3. Create AgentCore Memory (requires MCP tool)"
echo "  4. Deploy Trading Agent"
echo ""
echo "See SETUP_GUIDE.md for detailed instructions"
echo ""
echo "Configuration files created:"
echo "  - lambda_config.json"
echo "  - cognito_config.json"
echo ""
echo "Secrets stored in AWS Parameter Store:"
echo "  - /trading-agent/alpha-vantage-api-key"
echo "  - /trading-agent/notification-email"
echo ""
