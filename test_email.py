#!/usr/bin/env python3
"""
Script to send a sample trading email.
"""

import json
import boto3

# Initialize Lambda client
lambda_client = boto3.client('lambda', region_name='us-west-2')

print("=" * 80)
print("SENDING SAMPLE TRADING EMAIL")
print("=" * 80)

# Create sample trading recommendations
sample_data = {
    "recommendations": [
        {
            "symbol": "AAPL",
            "recommendation": "BUY",
            "price": 175.50,
            "confidence": 0.85,
            "indicators": {
                "rsi": 42.5,
                "ema_20": 178.20,
                "ema_50": 172.80,
                "macd": {
                    "line": 2.5,
                    "signal": 1.8,
                    "histogram": 0.7
                },
                "bollinger_bands": {
                    "upper": 182.50,
                    "middle": 175.00,
                    "lower": 167.50
                }
            },
            "signals": [
                "RSI_OVERSOLD",
                "BULLISH_EMA_CROSS",
                "MACD_BULLISH",
                "PRICE_BELOW_LOWER_BB"
            ]
        },
        {
            "symbol": "MSFT",
            "recommendation": "HOLD",
            "price": 420.30,
            "confidence": 0.55,
            "indicators": {
                "rsi": 52.0,
                "ema_20": 418.50,
                "ema_50": 415.20,
                "macd": {
                    "line": 1.2,
                    "signal": 1.5,
                    "histogram": -0.3
                },
                "bollinger_bands": {
                    "upper": 425.00,
                    "middle": 420.00,
                    "lower": 415.00
                }
            },
            "signals": [
                "BULLISH_EMA_CROSS"
            ]
        },
        {
            "symbol": "NVDA",
            "recommendation": "SELL",
            "price": 875.20,
            "confidence": 0.78,
            "indicators": {
                "rsi": 72.5,
                "ema_20": 865.00,
                "ema_50": 850.00,
                "macd": {
                    "line": -2.5,
                    "signal": -1.2,
                    "histogram": -1.3
                },
                "bollinger_bands": {
                    "upper": 880.00,
                    "middle": 870.00,
                    "lower": 860.00
                }
            },
            "signals": [
                "RSI_OVERBOUGHT",
                "MACD_BEARISH",
                "PRICE_ABOVE_UPPER_BB"
            ]
        }
    ]
}

# Prepare Lambda payload
payload = {
    "alert_type": "daily_summary",
    "data": sample_data
}

print("\nSending daily summary email with 3 stock analyses...")
print("  - AAPL: BUY (85% confidence)")
print("  - MSFT: HOLD (55% confidence)")
print("  - NVDA: SELL (78% confidence)")

try:
    # Invoke Lambda
    response = lambda_client.invoke(
        FunctionName='TradingAgent-EmailNotification',
        InvocationType='RequestResponse',
        Payload=json.dumps(payload)
    )
    
    # Parse response
    response_payload = json.loads(response['Payload'].read())
    
    print(f"\nLambda Response: {json.dumps(response_payload, indent=2)}")
    
    if response['StatusCode'] == 200:
        if 'body' in response_payload:
            result = json.loads(response_payload['body'])
        else:
            result = response_payload
        
        if 'message_id' in result:
            print("\n" + "=" * 80)
            print("✓ EMAIL SENT SUCCESSFULLY!")
            print("=" * 80)
            print(f"\nMessage ID: {result['message_id']}")
            print(f"To: your_email@example.com")
            print("\n📧 Check your inbox for the trading analysis email!")
            print("\nThe email includes:")
            print("  - Beautiful HTML formatting")
            print("  - Technical indicator analysis")
            print("  - BUY/SELL/HOLD recommendations")
            print("  - Risk management parameters")
            print("  - Confidence scores")
        else:
            print("\n❌ Email sending failed")
            print(f"Error: {result.get('error', 'Unknown error')}")
            print(f"Details: {result.get('details', 'No details')}")
    else:
        print(f"\n❌ Lambda invocation failed with status: {response['StatusCode']}")
        print(f"Response: {response_payload}")
        
except Exception as e:
    print(f"\n❌ Error: {e}")
    print("\nPossible issues:")
    print("  1. Email not verified in SES")
    print("  2. Lambda function error")
    print("  3. Permissions issue")
    
print("\n" + "=" * 80)
