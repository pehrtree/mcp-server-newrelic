"""New Relic API client for querying logs."""

import json
import logging
from typing import Any, Dict, List, Optional
import httpx

from .models import LogQueryRequest, LogQueryResponse, LogEntry

logger = logging.getLogger(__name__)


class NewRelicClient:
    """Client for interacting with New Relic GraphQL API."""
    
    def __init__(self, api_key: str, endpoint: str = "https://api.newrelic.com/graphql"):
        """Initialize New Relic client.
        
        Args:
            api_key: New Relic User API Key (should start with NRAK)
            endpoint: GraphQL API endpoint
        """
        if not api_key.startswith("NRAK"):
            logger.warning("API key does not start with 'NRAK'. It may not be a valid User API Key.")
        
        self.api_key = api_key
        self.endpoint = endpoint
        self.headers = {
            "Content-Type": "application/json",
            "API-Key": api_key
        }
    
    def _build_nrql_query(self, request: LogQueryRequest) -> str:
        """Build NRQL query from request parameters.
        
        Args:
            request: Log query request
            
        Returns:
            NRQL query string
        """
        if request.query:
            return request.query
        
        # Start with basic SELECT
        nrql = "SELECT * FROM Log"
        
        # Build WHERE clause
        where_conditions = []
        
        if request.message_search:
            where_conditions.append(f"message LIKE '%{request.message_search}%'")
        
        if request.filters:
            for key, value in request.filters.items():
                # Handle different value types
                if value.lower() in ('true', 'false'):
                    where_conditions.append(f"{key} = {value.lower()}")
                elif value.replace('.', '').replace('-', '').isdigit():
                    where_conditions.append(f"{key} = {value}")
                else:
                    where_conditions.append(f"{key} = '{value}'")
        
        if where_conditions:
            nrql += " WHERE " + " AND ".join(where_conditions)
        
        # Add time range
        nrql += f" SINCE {request.since}"
        
        # Add limit
        nrql += f" LIMIT {request.limit}"
        
        return nrql
    
    async def query_logs(self, request: LogQueryRequest) -> LogQueryResponse:
        """Query New Relic logs.
        
        Args:
            request: Log query request
            
        Returns:
            Log query response with results
        """
        nrql = self._build_nrql_query(request)
        logger.info(f"Executing NRQL query: {nrql}")
        
        graphql_query = """
        {
          actor {
            account(id: %s) {
              nrql(query: "%s") {
                results
                totalResult
                metadata {
                  eventTypes
                  facets
                  messages
                }
              }
            }
          }
        }
        """ % (request.account_id, nrql.replace('"', '\\"'))
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                self.endpoint,
                headers=self.headers,
                json={"query": graphql_query}
            )
            
            if response.status_code == 429:
                raise Exception("Rate limit exceeded. Please wait before retrying.")
            
            response.raise_for_status()
            data = response.json()
            
            if "errors" in data:
                error_messages = [err.get("message", "Unknown error") for err in data["errors"]]
                raise Exception(f"GraphQL errors: {'; '.join(error_messages)}")
            
            # Extract results
            nrql_data = data.get("data", {}).get("actor", {}).get("account", {}).get("nrql", {})
            results = nrql_data.get("results", [])
            
            # Convert to LogEntry objects
            logs = []
            for result in results:
                log_entry = LogEntry(
                    timestamp=result.get("timestamp"),
                    message=result.get("message", ""),
                    level=result.get("level", "INFO"),
                    attributes={k: v for k, v in result.items() 
                              if k not in ["timestamp", "message", "level"]}
                )
                logs.append(log_entry)
            
            total_results = len(results)
            if nrql_data.get("totalResult"):
                total_results = nrql_data["totalResult"].get("count", len(results))
            
            return LogQueryResponse(
                logs=logs,
                total_results=total_results,
                query_executed=nrql
            )
    
    async def get_account_id(self, account_name: str) -> str:
        """Get account ID by account name.
        
        Args:
            account_name: Name of the New Relic account
            
        Returns:
            Account ID
        """
        graphql_query = """
        {
          actor {
            accounts {
              id
              name
            }
          }
        }
        """
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                self.endpoint,
                headers=self.headers,
                json={"query": graphql_query}
            )
            
            response.raise_for_status()
            data = response.json()
            
            if "errors" in data:
                error_messages = [err.get("message", "Unknown error") for err in data["errors"]]
                raise Exception(f"GraphQL errors: {'; '.join(error_messages)}")
            
            accounts = data.get("data", {}).get("actor", {}).get("accounts", [])
            
            for account in accounts:
                if account.get("name", "").lower() == account_name.lower():
                    return str(account.get("id"))
            
            raise Exception(f"Account '{account_name}' not found. Available accounts: {', '.join([a.get('name', 'Unknown') for a in accounts])}")