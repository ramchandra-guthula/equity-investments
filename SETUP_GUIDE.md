# Trading Agent - Complete Setup Guide

## Prerequisites

1. **AWS Account** with appropriate permissions
2. **Alpha Vantage API Key** (free tier: https://www.alphavantage.co/support/#api-key)
3. **Email address** for notifications
4. **Python 3.12+** installed locally
5. **AWS CLI** configured with credentials

## Quick Start (Local Setup)

### Step 1: Clone and Configure

```bash
# Navigate to project directory
cd equity-investments

# Copy environment template
cp .env.template .env

# Edit .env and add your values
nano .env
```

Add these values to `.env`:
```bash
ALPHA_VANTAGE_API_KEY=your_actual_api_key
NOTIFICATION_EMAIL=your_email@example.com
AWS_REGION=us-west-2
```

### Step 2: Install Dependencies

```bash
pip install boto3 requests pyyaml strands-agents bedrock-agentcore
```

### Step 3: Run Setup Scripts

```bash
# Set environment variables
export $(cat .env | xargs)

# Run complete setup
python3 setup_infrastructure.py
```

This will:
- Create Lambda functions (Market Data + Email Notification)
- Store secrets in AWS Parameter Store
- Create Cognito User Pool for authentication
- Verify your email in SES

### Step 4: Verify Email

Check your inbox for SES verification email and click the link.

### Step 5: Create Gateway and Memory (Manual)

Since these require MCP tools, run from Kiro IDE or use AWS CLI:

```bash
# Create gateway role
aws iam create-role --role-name TradingAgentGatewayRole \
  --assume-role-policy-document file://gateway-trust-policy.json

# Create gateway (use AgentCore console or CLI)
# Create memory (use AgentCore console or CLI)
```

## GitHub Setup

### Step 1: Create Repository

```bash
git init
git add .
git commit -m "Initial commit: Trading Agent"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/trading-agent.git
git push -u origin main
```

### Step 2: Add GitHub Secrets

Go to: Repository → Settings → Secrets and variables → Actions

Add these secrets:
- `AWS_ACCESS_KEY_ID` - Your AWS access key
- `AWS_SECRET_ACCESS_KEY` - Your AWS secret key
- `ALPHA_VANTAGE_API_KEY` - Your Alpha Vantage API key
- `NOTIFICATION_EMAIL` - your_email@example.com

### Step 3: Enable GitHub Actions

The workflow will automatically deploy on push to main branch.

## Email Notifications

### Schedule: 8 AM CST Daily

The agent will send daily market analysis emails at 8 AM Central Time.

### Email Types

1. **Daily Summary** (8 AM CST)
   - Market analysis for watchlist stocks
   - High-confidence trading opportunities
   - Technical indicator summary

2. **High Confidence Alerts** (Real-time)
   - Sent when confidence score > 70%
   - Includes entry/exit recommendations
   - Risk management parameters

3. **Stop Loss/Take Profit** (Phase 2)
   - Triggered when positions hit targets
   - Includes P&L summary

## Testing

### Test Market Data Lambda

```bash
aws lambda invoke \
  --function-name TradingAgent-MarketData \
  --payload '{"symbol":"AAPL"}' \
  response.json

cat response.json
```

### Test Email Notification

```bash
aws lambda invoke \
  --function-name TradingAgent-EmailNotification \
  --payload '{
    "alert_type": "daily_summary",
    "data": {
      "recommendations": []
    }
  }' \
  response.json
```

## Scheduling Daily Analysis

### Option 1: EventBridge (Recommended)

```bash
# Create EventBridge rule for 8 AM CST (14:00 UTC)
aws events put-rule \
  --name trading-agent-daily-analysis \
  --schedule-expression "cron(0 14 * * ? *)" \
  --description "Daily market analysis at 8 AM CST"

# Add Lambda target
aws events put-targets \
  --rule trading-agent-daily-analysis \
  --targets "Id"="1","Arn"="arn:aws:lambda:us-west-2:ACCOUNT_ID:function:TradingAgent-MarketData"
```

### Option 2: GitHub Actions (Alternative)

The workflow can be scheduled to run daily:

```yaml
on:
  schedule:
    - cron: '0 14 * * *'  # 8 AM CST = 14:00 UTC
```

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    EventBridge Schedule                      │
│                    (8 AM CST Daily)                          │
└──────────────┬──────────────────────────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────────────────────────┐
│              AgentCore Runtime (Trading Agent)               │
│                                                              │
│  - Analyzes watchlist stocks                                 │
│  - Calculates technical indicators                           │
│  - Generates recommendations                                 │
│  - Stores history in Memory                                  │
└──────────────┬──────────────────────────────────────────────┘
               │
               ├─── AgentCore Memory (Trading History)
               │
               ├─── AgentCore Gateway
               │    │
               │    ├─── Market Data Lambda
               │    │    └─── Alpha Vantage API
               │    │
               │    └─── Email Notification Lambda
               │         └─── Amazon SES
               │
               └─── Cognito (Authentication)
```

## Cost Estimates

### Monthly Costs (Phase 1)

- **Lambda**: ~$5-10 (daily executions)
- **AgentCore Runtime**: ~$50-100 (serverless agent)
- **AgentCore Memory**: ~$10 (storage)
- **AgentCore Gateway**: ~$5 (API calls)
- **SES**: Free tier (62,000 emails/month)
- **Parameter Store**: Free
- **EventBridge**: Free tier

**Total**: ~$70-125/month

### Cost Optimization

- Use Alpha Vantage free tier (500 calls/day)
- Analyze only watchlist stocks (10 stocks)
- Send emails only for high-confidence opportunities
- Use compact memory storage

## Troubleshooting

### Email Not Sending

1. Check SES verification status:
```bash
aws ses get-identity-verification-attributes \
  --identities your_email@example.com
```

2. Verify email in SES console
3. Check Lambda logs in CloudWatch

### Lambda Errors

```bash
# View logs
aws logs tail /aws/lambda/TradingAgent-MarketData --follow

# Check function configuration
aws lambda get-function --function-name TradingAgent-MarketData
```

### API Rate Limits

Alpha Vantage free tier: 5 calls/minute, 500/day
- Analyze max 10 stocks per day
- Cache results in DynamoDB (future enhancement)

## Security Best Practices

1. **Never commit secrets** to Git
   - Use `.gitignore` for config files
   - Store secrets in Parameter Store
   - Use GitHub Secrets for CI/CD

2. **Use least privilege IAM roles**
   - Lambda roles have minimal permissions
   - Gateway role only invokes Lambda

3. **Enable CloudWatch logging**
   - Monitor all Lambda executions
   - Set up alarms for errors

4. **Rotate credentials regularly**
   - Update API keys quarterly
   - Rotate Cognito secrets

## Next Steps

1. ✅ Infrastructure setup complete
2. ⏳ Create AgentCore Gateway
3. ⏳ Create AgentCore Memory
4. ⏳ Deploy Trading Agent
5. ⏳ Schedule daily analysis
6. ⏳ Test for 2 weeks
7. ⏳ Move to Phase 2 (autonomous trading)

## Support

For issues or questions:
- Check CloudWatch logs
- Review AWS documentation
- Test Lambda functions individually
- Verify all configurations

## Legal Disclaimer

This is an educational project. Not financial advice. Trading involves risk. Always:
- Consult financial advisors
- Understand your risk tolerance
- Never invest more than you can afford to lose
- Comply with all regulations
- Start with paper trading
