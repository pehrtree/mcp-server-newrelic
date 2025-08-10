#!/usr/bin/env python3
"""Test script for New Relic API integration."""

import asyncio
import logging
import os
import sys
from pathlib import Path

# Load .env file if it exists
env_file = Path(__file__).parent / ".env"
if env_file.exists():
    with open(env_file) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                os.environ[key] = value

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from newrelic_mcp.client import NewRelicClient
from newrelic_mcp.models import LogQueryRequest

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def test_api_connectivity():
    """Test basic API connectivity."""
    logger.info("🧪 Testing New Relic API integration...")
    
    api_key = os.getenv("NEW_RELIC_API_KEY")
    if not api_key:
        logger.error("❌ NEW_RELIC_API_KEY environment variable not set")
        return False
    
    logger.info(f"✓ API Key found (length: {len(api_key)})")
    
    try:
        client = NewRelicClient(api_key)
        logger.info("✓ Client initialized")
        
        # Test 1: Get accounts
        logger.info("\n📋 Testing account listing...")
        accounts_query = """
        {
          actor {
            accounts {
              id
              name
            }
          }
        }
        """
        
        import httpx
        async with httpx.AsyncClient(timeout=30.0) as http_client:
            response = await http_client.post(
                client.endpoint,
                headers=client.headers,
                json={"query": accounts_query}
            )
            
            if response.status_code != 200:
                logger.error(f"❌ HTTP {response.status_code}: {response.text}")
                return False
            
            data = response.json()
            if "errors" in data:
                logger.error(f"❌ GraphQL errors: {data['errors']}")
                return False
            
            accounts = data.get("data", {}).get("actor", {}).get("accounts", [])
            logger.info(f"✓ Found {len(accounts)} accounts:")
            for account in accounts[:3]:  # Show first 3
                logger.info(f"  - {account.get('name', 'Unknown')} (ID: {account.get('id')})")
            
            if not accounts:
                logger.warning("⚠ No accounts found - this may indicate permission issues")
                return False
        
        # Test 2: Try a simple log query on the first account
        if accounts:
            test_account_id = str(accounts[0]["id"])
            logger.info(f"\n🔍 Testing log query on account {test_account_id}...")
            
            request = LogQueryRequest(
                account_id=test_account_id,
                message_search="",  # Empty search to get any logs
                since="1 day ago",
                limit=5
            )
            
            try:
                response = await client.query_logs(request)
                logger.info(f"✓ Query successful! Found {len(response.logs)} logs (total: {response.total_results})")
                logger.info(f"✓ Query executed: {response.query_executed}")
                
                if response.logs:
                    logger.info("📄 Sample log entries:")
                    for i, log in enumerate(response.logs[:2]):  # Show first 2
                        logger.info(f"  {i+1}. [{log.level}] {log.timestamp_str}: {log.message[:100]}...")
                else:
                    logger.info("ℹ No logs found in the time range")
                
                return True
                
            except Exception as e:
                logger.error(f"❌ Log query failed: {e}")
                return False
    
    except Exception as e:
        logger.error(f"❌ API test failed: {e}")
        return False


async def main():
    """Run API tests."""
    logger.info("🚀 Starting New Relic API integration tests...")
    
    success = await test_api_connectivity()
    
    if success:
        logger.info("\n✅ All tests passed! New Relic API integration is working.")
    else:
        logger.error("\n❌ Some tests failed. Check your API key and permissions.")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())