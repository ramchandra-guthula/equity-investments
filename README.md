# 🎯 Equity Investment Agent

AI-powered swing trading agent built with AWS Bedrock AgentCore and Strands.

**Status**: ✅ Infrastructure Ready | ⏳ Gateway & Memory Pending | 🚀 Ready to Deploy

## 🚀 Quick Start

```bash
# 1. Set environment variables
export ALPHA_VANTAGE_API_KEY=your_api_key_here
export NOTIFICATION_EMAIL=your_email@example.com

# 2. Run quick start
cd equity-investments
./quickstart.sh

# 3. Verify email in SES (check inbox)

# 4. Continue with Gateway & Memory setup (see SETUP_GUIDE.md)
```

## Project Phases

### Phase 1: Market Analysis & Suggestions (Current)
- Daily market analysis and reporting
- Trading opportunity identification
- Risk-adjusted recommendations
- Email/SMS notifications for opportunities
- Memory of user preferences and past suggestions

### Phase 2: Autonomous Trading (Future)
- Automated trade execution within risk parameters
- Portfolio management and rebalancing
- Human-in-the-loop for high-value trades
- Performance tracking and strategy optimization

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    AgentCore Runtime                         │
│                  (Swing Trading Agent)                       │
│                                                              │
│  - Market Analysis                                           │
│  - Technical Indicators (RSI, MACD, Moving Averages)        │
│  - Risk Assessment                                           │
│  - Trade Recommendations                                     │
└──────────────┬──────────────────────────────────────────────┘
               │
               ├─── AgentCore Memory (Preferences, History)
               │
               ├─── AgentCore Gateway (MCP Tools)
               │    │
               │    ├─── Market Data Lambda (Alpha Vantage/Yahoo)
               │    ├─── Portfolio Tracker Lambda
               │    ├─── Trade Executor Lambda (Phase 2)
               │    └─── Notification Lambda (SNS/Email)
               │
               └─── EventBridge (Daily Schedule)
```

## Risk Management Strategy

### Swing Trading Parameters
- **Holding Period**: 2-10 days
- **Max Loss Per Trade**: 2% of capital
- **Max Portfolio Risk**: 10% total exposure
- **Position Sizing**: Kelly Criterion with 0.5 multiplier
- **Stop Loss**: Trailing stop at 3%
- **Take Profit**: 5-8% target

### Technical Indicators
- RSI (14-period) - Overbought/Oversold
- MACD - Trend confirmation
- 20/50 EMA - Support/Resistance
- Volume analysis - Confirmation
- Bollinger Bands - Volatility

## Tech Stack

- **Agent Framework**: Strands Agents SDK
- **Deployment**: AWS Bedrock AgentCore Runtime
- **Memory**: AgentCore Memory (preferences, history)
- **Tools**: AgentCore Gateway + Lambda functions
- **Auth**: Amazon Cognito
- **Scheduling**: Amazon EventBridge
- **Notifications**: Amazon SNS
- **Model**: Claude Sonnet 4.5

## Setup Instructions

See individual scripts in numbered order:
1. `01_create_market_data_lambda.py` - Market data fetcher
2. `02_create_portfolio_lambda.py` - Portfolio tracker
3. `03_create_notification_lambda.py` - Alert system
4. `04_create_cognito.py` - Authentication
5. `05_create_gateway.py` - MCP Gateway
6. `06_create_memory.py` - Agent memory
7. `07_trading_agent.py` - Main agent code
8. `08_deploy_agent.py` - Deploy to runtime
9. `09_schedule_daily_analysis.py` - EventBridge schedule

## Configuration Files

- `config.json` - Trading parameters and risk limits
- `watchlist.json` - Stocks to monitor
- `portfolio.json` - Current holdings (Phase 2)

## Safety Features

- Human approval required for all trades (Phase 1)
- Configurable risk limits
- Daily loss limits
- Position size limits
- Emergency stop mechanism
- Audit trail in Memory

## Legal Disclaimer

This is an educational project. Trading involves risk. Always:
- Consult with financial advisors
- Understand your risk tolerance
- Never invest more than you can afford to lose
- Comply with all applicable regulations
- Use paper trading first

## Next Steps

1. Set up market data API (Alpha Vantage free tier)
2. Define your watchlist and risk parameters
3. Create Lambda functions for data fetching
4. Build Phase 1 agent (suggestions only)
5. Test with paper trading
6. Gradually move to Phase 2 with minimal capital
