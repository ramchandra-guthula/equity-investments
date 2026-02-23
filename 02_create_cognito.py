#!/usr/bin/env python3
"""
Script to create Cognito User Pool for agent authentication.
"""

import json
import boto3
import secrets
import string

cognito = boto3.client('cognito-idp', region_name='us-west-2')

REGION = 'us-west-2'
POOL_NAME = 'trading-agent-pool'
DOMAIN_PREFIX = f'trading-agent-{secrets.token_hex(4)}'

print("=" * 80)
print("CREATING COGNITO USER POOL")
print("=" * 80)

# Step 1: Create User Pool
print("\nStep 1: Creating Cognito User Pool...")
try:
    pool_response = cognito.create_user_pool(
        PoolName=POOL_NAME,
        Policies={
            'PasswordPolicy': {
                'MinimumLength': 8,
                'RequireUppercase': False,
                'RequireLowercase': False,
                'RequireNumbers': False,
                'RequireSymbols': False
            }
        },
        AutoVerifiedAttributes=['email']
    )
    
    user_pool_id = pool_response['UserPool']['Id']
    print(f"✓ User Pool created: {user_pool_id}")
    
except Exception as e:
    print(f"❌ Error creating user pool: {e}")
    exit(1)

# Step 2: Create User Pool Domain
print("\nStep 2: Creating User Pool Domain...")
try:
    domain_response = cognito.create_user_pool_domain(
        Domain=DOMAIN_PREFIX,
        UserPoolId=user_pool_id
    )
    print(f"✓ Domain created: {DOMAIN_PREFIX}.auth.{REGION}.amazoncognito.com")
    
except Exception as e:
    print(f"❌ Error creating domain: {e}")
    cognito.delete_user_pool(UserPoolId=user_pool_id)
    exit(1)

# Step 3: Create Resource Server
print("\nStep 3: Creating Resource Server...")
try:
    resource_server_response = cognito.create_resource_server(
        UserPoolId=user_pool_id,
        Identifier='trading-api',
        Name='TradingAPI',
        Scopes=[
            {
                'ScopeName': 'read',
                'ScopeDescription': 'Read access to trading agent'
            },
            {
                'ScopeName': 'write',
                'ScopeDescription': 'Write access to trading agent'
            }
        ]
    )
    print("✓ Resource server created with read/write scopes")
    
except Exception as e:
    print(f"❌ Error creating resource server: {e}")
    cognito.delete_user_pool_domain(Domain=DOMAIN_PREFIX, UserPoolId=user_pool_id)
    cognito.delete_user_pool(UserPoolId=user_pool_id)
    exit(1)

# Step 4: Create App Client
print("\nStep 4: Creating App Client...")
try:
    app_client_response = cognito.create_user_pool_client(
        UserPoolId=user_pool_id,
        ClientName='trading-agent-client',
        GenerateSecret=True,
        ExplicitAuthFlows=[],
        AllowedOAuthFlows=['client_credentials'],
        AllowedOAuthScopes=[
            'trading-api/read',
            'trading-api/write'
        ],
        AllowedOAuthFlowsUserPoolClient=True,
        SupportedIdentityProviders=['COGNITO']
    )
    
    client_id = app_client_response['UserPoolClient']['ClientId']
    client_secret = app_client_response['UserPoolClient']['ClientSecret']
    
    print(f"✓ App client created: {client_id}")
    
except Exception as e:
    print(f"❌ Error creating app client: {e}")
    cognito.delete_user_pool_domain(Domain=DOMAIN_PREFIX, UserPoolId=user_pool_id)
    cognito.delete_user_pool(UserPoolId=user_pool_id)
    exit(1)

# Step 5: Save configuration
print("\nStep 5: Saving configuration...")

cognito_config = {
    "user_pool_id": user_pool_id,
    "domain_prefix": DOMAIN_PREFIX,
    "client_id": client_id,
    "client_secret": client_secret,
    "token_endpoint": f"https://{DOMAIN_PREFIX}.auth.{REGION}.amazoncognito.com/oauth2/token",
    "discovery_url": f"https://cognito-idp.{REGION}.amazonaws.com/{user_pool_id}/.well-known/openid-configuration",
    "region": REGION
}

with open('cognito_config.json', 'w') as f:
    json.dump(cognito_config, f, indent=2)

print("✓ Configuration saved to cognito_config.json")

print("\n" + "=" * 80)
print("✓ COGNITO USER POOL CREATED SUCCESSFULLY")
print("=" * 80)
print(f"\nUser Pool ID: {user_pool_id}")
print(f"Client ID: {client_id}")
print(f"\nNext step: Run python3 03_create_gateway.py")
