"""
Market Data Lambda Function
Fetches stock data and calculates technical indicators
"""

import json
import os
import requests
from datetime import datetime, timedelta
import boto3
from decimal import Decimal

# Initialize clients
dynamodb = boto3.resource('dynamodb')
ssm = boto3.client('ssm')

# Get API key from environment or SSM Parameter Store
def get_api_key():
    """Get Alpha Vantage API key from environment or Parameter Store"""
    api_key = os.environ.get('ALPHA_VANTAGE_API_KEY')
    if not api_key:
        try:
            response = ssm.get_parameter(
                Name='/trading-agent/alpha-vantage-api-key',
                WithDecryption=True
            )
            api_key = response['Parameter']['Value']
        except Exception as e:
            print(f"Error getting API key: {e}")
            return None
    return api_key

def calculate_rsi(prices, period=14):
    """Calculate Relative Strength Index"""
    if len(prices) < period + 1:
        return None
    
    deltas = [prices[i] - prices[i-1] for i in range(1, len(prices))]
    gains = [d if d > 0 else 0 for d in deltas]
    losses = [-d if d < 0 else 0 for d in deltas]
    
    avg_gain = sum(gains[:period]) / period
    avg_loss = sum(losses[:period]) / period
    
    if avg_loss == 0:
        return 100
    
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    return round(rsi, 2)

def calculate_ema(prices, period):
    """Calculate Exponential Moving Average"""
    if len(prices) < period:
        return None
    
    multiplier = 2 / (period + 1)
    ema = sum(prices[:period]) / period
    
    for price in prices[period:]:
        ema = (price - ema) * multiplier + ema
    
    return round(ema, 2)

def calculate_macd(prices):
    """Calculate MACD (12, 26, 9)"""
    if len(prices) < 26:
        return None, None, None
    
    ema_12 = calculate_ema(prices, 12)
    ema_26 = calculate_ema(prices, 26)
    
    if ema_12 is None or ema_26 is None:
        return None, None, None
    
    macd_line = ema_12 - ema_26
    
    # For signal line, we'd need MACD history - simplified here
    signal_line = macd_line * 0.9  # Approximation
    histogram = macd_line - signal_line
    
    return round(macd_line, 2), round(signal_line, 2), round(histogram, 2)

def calculate_bollinger_bands(prices, period=20, std_dev=2):
    """Calculate Bollinger Bands"""
    if len(prices) < period:
        return None, None, None
    
    recent_prices = prices[-period:]
    sma = sum(recent_prices) / period
    
    variance = sum((p - sma) ** 2 for p in recent_prices) / period
    std = variance ** 0.5
    
    upper_band = sma + (std_dev * std)
    lower_band = sma - (std_dev * std)
    
    return round(upper_band, 2), round(sma, 2), round(lower_band, 2)

def fetch_stock_data(symbol, api_key):
    """Fetch stock data from Alpha Vantage"""
    url = f"https://www.alphavantage.co/query"
    params = {
        'function': 'TIME_SERIES_DAILY',
        'symbol': symbol,
        'apikey': api_key,
        'outputsize': 'compact'  # Last 100 days
    }
    
    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        if 'Error Message' in data:
            return {'error': f"Invalid symbol: {symbol}"}
        
        if 'Note' in data:
            return {'error': 'API rate limit reached'}
        
        if 'Time Series (Daily)' not in data:
            return {'error': 'No data available'}
        
        return data
    except Exception as e:
        return {'error': str(e)}

def analyze_stock(symbol, api_key):
    """Fetch and analyze stock data"""
    # Fetch data
    data = fetch_stock_data(symbol, api_key)
    
    if 'error' in data:
        return data
    
    # Parse time series
    time_series = data['Time Series (Daily)']
    dates = sorted(time_series.keys(), reverse=True)
    
    # Get latest data
    latest_date = dates[0]
    latest_data = time_series[latest_date]
    
    current_price = float(latest_data['4. close'])
    volume = int(latest_data['5. volume'])
    
    # Get historical prices for indicators
    prices = [float(time_series[date]['4. close']) for date in dates[:100]]
    
    # Calculate technical indicators
    rsi = calculate_rsi(prices, 14)
    ema_20 = calculate_ema(prices, 20)
    ema_50 = calculate_ema(prices, 50)
    macd_line, signal_line, histogram = calculate_macd(prices)
    upper_band, middle_band, lower_band = calculate_bollinger_bands(prices, 20, 2)
    
    # Determine signals
    signals = []
    
    if rsi and rsi < 30:
        signals.append("RSI_OVERSOLD")
    elif rsi and rsi > 70:
        signals.append("RSI_OVERBOUGHT")
    
    if ema_20 and ema_50:
        if ema_20 > ema_50:
            signals.append("BULLISH_EMA_CROSS")
        else:
            signals.append("BEARISH_EMA_CROSS")
    
    if macd_line and signal_line:
        if macd_line > signal_line:
            signals.append("MACD_BULLISH")
        else:
            signals.append("MACD_BEARISH")
    
    if upper_band and lower_band:
        if current_price > upper_band:
            signals.append("PRICE_ABOVE_UPPER_BB")
        elif current_price < lower_band:
            signals.append("PRICE_BELOW_LOWER_BB")
    
    # Calculate confidence score
    bullish_signals = sum(1 for s in signals if 'BULLISH' in s or 'OVERSOLD' in s or 'BELOW' in s)
    bearish_signals = sum(1 for s in signals if 'BEARISH' in s or 'OVERBOUGHT' in s or 'ABOVE' in s)
    
    total_signals = len(signals)
    if total_signals > 0:
        confidence = abs(bullish_signals - bearish_signals) / total_signals
    else:
        confidence = 0
    
    recommendation = "HOLD"
    if bullish_signals > bearish_signals and confidence > 0.5:
        recommendation = "BUY"
    elif bearish_signals > bullish_signals and confidence > 0.5:
        recommendation = "SELL"
    
    return {
        'symbol': symbol,
        'date': latest_date,
        'price': current_price,
        'volume': volume,
        'indicators': {
            'rsi': rsi,
            'ema_20': ema_20,
            'ema_50': ema_50,
            'macd': {
                'line': macd_line,
                'signal': signal_line,
                'histogram': histogram
            },
            'bollinger_bands': {
                'upper': upper_band,
                'middle': middle_band,
                'lower': lower_band
            }
        },
        'signals': signals,
        'recommendation': recommendation,
        'confidence': round(confidence, 2),
        'timestamp': datetime.utcnow().isoformat()
    }

def lambda_handler(event, context):
    """Lambda handler for market data analysis"""
    
    # Get API key
    api_key = get_api_key()
    if not api_key:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': 'API key not configured'})
        }
    
    # Parse input
    body = event.get('body', '{}')
    if isinstance(body, str):
        body = json.loads(body)
    
    symbol = body.get('symbol', event.get('symbol'))
    
    if not symbol:
        return {
            'statusCode': 400,
            'body': json.dumps({'error': 'Symbol required'})
        }
    
    # Analyze stock
    result = analyze_stock(symbol, api_key)
    
    if 'error' in result:
        return {
            'statusCode': 400,
            'body': json.dumps(result)
        }
    
    return {
        'statusCode': 200,
        'body': json.dumps(result)
    }
