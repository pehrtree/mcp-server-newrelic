"""New Relic API client for querying logs."""

import json
import logging
from typing import Any, Dict, List, Optional
import httpx

from .models import LogQueryRequest, LogQueryResponse, LogEntry

logger = logging.getLogger(__name__)

# Maximum response size in characters to avoid token limits
MAX_RESPONSE_SIZE = 20000


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
    
    def _estimate_response_size(self, logs: List[LogEntry]) -> int:
        """Estimate the size of the JSON response in characters.
        
        Args:
            logs: List of log entries
            
        Returns:
            Estimated size in characters
        """
        # Create a sample response to measure size
        sample_response = LogQueryResponse(
            logs=logs,
            total_results=len(logs),
            query_executed="sample query"
        )
        return len(sample_response.to_json())
    
    def _truncate_logs_to_size(self, logs: List[LogEntry], max_size: int) -> tuple[List[LogEntry], bool]:
        """Truncate logs list to fit within size limit.
        
        Args:
            logs: Original list of log entries
            max_size: Maximum allowed size in characters
            
        Returns:
            Tuple of (truncated_logs, was_truncated)
        """
        if not logs:
            return logs, False
        
        # Binary search to find the maximum number of logs that fit
        left, right = 1, len(logs)
        best_fit = 0
        
        while left <= right:
            mid = (left + right) // 2
            test_logs = logs[:mid]
            
            if self._estimate_response_size(test_logs) <= max_size:
                best_fit = mid
                left = mid + 1
            else:
                right = mid - 1
        
        if best_fit < len(logs):
            return logs[:best_fit], True
        else:
            return logs, False
    
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
            
            # Check if we need to truncate due to response size
            truncated_logs, was_truncated = self._truncate_logs_to_size(logs, MAX_RESPONSE_SIZE)
            original_limit = None
            truncated_reason = None
            
            if was_truncated:
                original_limit = request.limit
                truncated_reason = f"Response too large ({self._estimate_response_size(logs)} chars). Reduced from {len(logs)} to {len(truncated_logs)} logs to fit within {MAX_RESPONSE_SIZE} character limit."
                logger.warning(f"Truncated logs response: {truncated_reason}")
                logs = truncated_logs
            
            return LogQueryResponse(
                logs=logs,
                total_results=total_results,
                query_executed=nrql,
                truncated=was_truncated,
                truncated_reason=truncated_reason,
                original_limit=original_limit
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