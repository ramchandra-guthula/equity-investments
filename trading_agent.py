"""
AgentCore Runtime Agent: trading_agent
Trading agent with memory and gateway integration
"""

import os
import json
from bedrock_agentcore.runtime import BedrockAgentCoreApp
from strands import Agent, tool
from strands.models import BedrockModel
from strands.tools.mcp import MCPClient
from mcp.client.streamable_http import streamablehttp_client
import requests
from bedrock_agentcore.memory.integrations.strands.config import AgentCoreMemoryConfig, RetrievalConfig
from bedrock_agentcore.memory.integrations.strands.session_manager import AgentCoreMemorySessionManager

# Constants
MODEL_ID = "us.anthropic.claude-sonnet-4-5-20250929-v1:0"
REGION = "us-west-2"
SESSION_ID = "default-session"
ACTOR_ID = "default-actor"

# Initialize app
app = BedrockAgentCoreApp()

def get_cognito_token_with_scope(client_id, client_secret, discovery_url, scope):
    """Get Cognito bearer token with a specific OAuth scope"""
    # Extract token endpoint from discovery URL
    discovery_response = requests.get(discovery_url)
    token_endpoint = discovery_response.json()['token_endpoint']
    
    # Get token using client credentials flow
    response = requests.post(
        token_endpoint,
        data={
            'grant_type': 'client_credentials',
            'client_id': client_id,
            'client_secret': client_secret,
            'scope': scope
        },
        headers={'Content-Type': 'application/x-www-form-urlencoded'}
    )
    
    response.raise_for_status()
    return response.json()["access_token"]

def create_mcp_client():
    """Create MCP client for gateway access"""
    gateway_url = os.environ.get("GATEWAY_URL")
    cognito_client_id = os.environ.get("COGNITO_CLIENT_ID")
    cognito_client_secret = os.environ.get("COGNITO_CLIENT_SECRET")
    cognito_discovery_url = os.environ.get("COGNITO_DISCOVERY_URL")
    oauth_scopes = os.environ.get("OAUTH_SCOPES", "trading-api/read trading-api/write")
    
    if not all([gateway_url, cognito_client_id, cognito_client_secret, cognito_discovery_url]):
        return None
    
    try:
        token = get_cognito_token_with_scope(
            cognito_client_id,
            cognito_client_secret,
            cognito_discovery_url,
            oauth_scopes
        )
        return MCPClient(
            lambda: streamablehttp_client(
                gateway_url,
                headers={"Authorization": f"Bearer {token}"},
            )
        )
    except Exception as e:
        print(f"Warning: Failed to create MCP client: {e}")
        return None

system_prompt = """You are an AI-powered swing trading analyst. Your role is to analyze stock market data, identify trading opportunities, and provide actionable recommendations.

You have access to:
1. Market data analysis tool - fetches real-time stock data and calculates technical indicators (RSI, MACD, EMA, Bollinger Bands)
2. Email notification tool - sends trading alerts and daily summaries
3. Memory - remembers user preferences and trading history

Your analysis should:
- Focus on swing trading opportunities (2-10 day holds)
- Use technical indicators to identify entry/exit points
- Provide clear BUY/SELL/HOLD recommendations with confidence scores
- Include risk management parameters (stop loss, take profit)
- Send email notifications for high-confidence opportunities (>70%)

Risk Management Rules:
- Max loss per trade: 2% of capital
- Stop loss: 3% trailing
- Take profit target: 5-8%
- Only recommend trades with confidence >70%

Always be conservative, prioritize capital preservation, and provide clear reasoning for your recommendations."""

@app.entrypoint
def invoke(payload, context=None):
    """AgentCore Runtime entrypoint"""
    try:
        # Initialize model
        bedrock_model = BedrockModel(model_id=MODEL_ID, temperature=0.3)
        
        # Get environment variables
        memory_id = os.environ.get("MEMORY_ID")
        if not memory_id:
            return "Error: MEMORY_ID environment variable is required"
        
        session_id = context.session_id if context else SESSION_ID
        actor_id = payload.get("actor_id", ACTOR_ID)
        
        # Configure memory
        agentcore_memory_config = AgentCoreMemoryConfig(
            memory_id=memory_id,
            session_id=session_id,
            actor_id=actor_id,
            retrieval_config={
                f"trading/{actor_id}/semantic": RetrievalConfig(top_k=3),
                f"trading/{actor_id}/preferences": RetrievalConfig(top_k=3),
                f"trading/{actor_id}/{session_id}/summary": RetrievalConfig(top_k=2),
            }
        )
        
        session_manager = AgentCoreMemorySessionManager(
            agentcore_memory_config=agentcore_memory_config,
            region_name=REGION
        )
        
        # Custom tools
        custom_tools = []
        
        # Try to create MCP client for gateway tools
        mcp_client = create_mcp_client()
        
        if mcp_client:
            try:
                with mcp_client:
                    gateway_tools = list(mcp_client.list_tools_sync())
                    
                    agent = Agent(
                        model=bedrock_model,
                        tools=custom_tools + gateway_tools,
                        system_prompt=system_prompt,
                        session_manager=session_manager
                    )
                    
                    user_input = payload.get("prompt", "")
                    response = agent(user_input)
                    return response.message["content"][0]["text"]
            except Exception as e:
                print(f"Warning: Failed to use gateway tools: {e}")
        
        # Fallback without gateway tools
        agent = Agent(
            model=bedrock_model,
            tools=custom_tools,
            system_prompt=system_prompt,
            session_manager=session_manager
        )
        
        user_input = payload.get("prompt", "")
        response = agent(user_input)
        return response.message["content"][0]["text"]
    
    except Exception as e:
        error_msg = f"Agent invocation failed: {str(e)}"
        print(error_msg)
        import traceback
        traceback.print_exc()
        return error_msg

if __name__ == "__main__":
    app.run()
