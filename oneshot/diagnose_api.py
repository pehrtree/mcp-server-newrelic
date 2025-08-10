#!/usr/bin/env python3
"""Diagnose New Relic API key issues."""

import os
from pathlib import Path

# Load .env file if it exists
env_file = Path(__file__).parent / ".env"
if env_file.exists():
    print("✓ Found .env file")
    with open(env_file) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                os.environ[key] = value
else:
    print("⚠ No .env file found")

api_key = os.getenv("NEW_RELIC_API_KEY")

if not api_key:
    print("❌ NEW_RELIC_API_KEY not found in environment")
    print("\nTo fix this, you need to:")
    print("1. Create a .env file in the oneshot directory")
    print("2. Add your New Relic API key: NEW_RELIC_API_KEY=your_key_here")
    print("\nAPI key requirements:")
    print("- Must be a User API Key (starts with 'NRAK')")
    print("- Get it from: New Relic UI > API keys > Create key > User key")
    exit(1)

print(f"✓ API Key found")
print(f"  Length: {len(api_key)}")
print(f"  Starts with: {api_key[:4]}...")
print(f"  Ends with: ...{api_key[-4:]}")

# Check key type
if api_key.startswith("NRAK"):
    print("✓ Appears to be a User API Key (correct type)")
elif api_key.startswith("NRAI"):
    print("⚠ This appears to be an Ingest API Key (wrong type)")
    print("  You need a User API Key that starts with 'NRAK'")
elif api_key.startswith("NRRA"):
    print("⚠ This appears to be a REST API Key (legacy, may not work)")
    print("  You should use a User API Key that starts with 'NRAK'")
else:
    print("⚠ Unknown API key format")
    print("  Expected User API Key starting with 'NRAK'")

print(f"\nEndpoint: {os.getenv('NEW_RELIC_API_ENDPOINT', 'https://api.newrelic.com/graphql')}")
print("\nIf you're still getting 401 errors after confirming the key type:")
print("1. Verify the key hasn't expired")
print("2. Check that your New Relic account has the necessary permissions")
print("3. Try creating a fresh User API Key")