#!/usr/bin/env python3
"""
Complete infrastructure setup for Trading Agent
Run this script to set up all AWS resources
"""

import subprocess
import sys
import os

def run_script(script_name, description):
    """Run a setup script and handle errors"""
    print(f"\n{'='*80}")
    print(f"Running: {description}")
    print(f"{'='*80}\n")
    
    result = subprocess.run([sys.executable, script_name], capture_output=False)
    
    if result.returncode != 0:
        print(f"\n❌ Error running {script_name}")
        print("Please fix the error and run this script again")
        sys.exit(1)
    
    print(f"\n✓ {description} completed successfully")

def check_environment():
    """Check required environment variables"""
    required_vars = ['ALPHA_VANTAGE_API_KEY', 'NOTIFICATION_EMAIL']
    missing = []
    
    for var in required_vars:
        if not os.environ.get(var):
            missing.append(var)
    
    if missing:
        print("❌ Missing required environment variables:")
        for var in missing:
            print(f"   - {var}")
        print("\nPlease set them:")
        print("   export ALPHA_VANTAGE_API_KEY=your_key")
        print("   export NOTIFICATION_EMAIL=your_email@example.com")
        sys.exit(1)
    
    print("✓ Environment variables configured")

def main():
    print("=" * 80)
    print("TRADING AGENT - COMPLETE INFRASTRUCTURE SETUP")
    print("=" * 80)
    
    # Check environment
    print("\nStep 1: Checking environment...")
    check_environment()
    
    # Run setup scripts in order
    scripts = [
        ("01_create_lambdas.py", "Create Lambda Functions"),
        ("02_create_cognito.py", "Create Cognito User Pool"),
    ]
    
    for script, description in scripts:
        if os.path.exists(script):
            run_script(script, description)
        else:
            print(f"⚠️  Script not found: {script}")
    
    print("\n" + "=" * 80)
    print("✓ INFRASTRUCTURE SETUP COMPLETE")
    print("=" * 80)
    print("\nNext steps:")
    print("  1. Create Gateway (requires MCP tool or manual setup)")
    print("  2. Create Memory (requires MCP tool)")
    print("  3. Deploy Trading Agent")
    print("\nSee README.md for detailed instructions")

if __name__ == "__main__":
    main()
