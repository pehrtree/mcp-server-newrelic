"""Data models for New Relic MCP server."""

import json
from typing import Any, Dict, List, Optional
from datetime import datetime
from pydantic import BaseModel, Field


class LogEntry(BaseModel):
    """Represents a single log entry from New Relic."""
    
    timestamp: Optional[int] = Field(None, description="Unix timestamp in milliseconds")
    message: str = Field(..., description="Log message content")
    level: str = Field("INFO", description="Log level (ERROR, WARN, INFO, DEBUG)")
    attributes: Dict[str, Any] = Field(default_factory=dict, description="Additional log attributes")
    
    @property
    def timestamp_str(self) -> str:
        """Get timestamp as ISO format string."""
        if self.timestamp:
            return datetime.fromtimestamp(self.timestamp / 1000).isoformat() + "Z"
        return ""


class LogQueryRequest(BaseModel):
    """Request parameters for querying logs."""
    
    account_id: str = Field(..., description="New Relic account ID")
    query: Optional[str] = Field(None, description="Full NRQL query (overrides other parameters)")
    message_search: Optional[str] = Field(None, description="Search text in message field")
    filters: Optional[Dict[str, str]] = Field(None, description="Key-value pairs for filtering")
    since: str = Field("1 hour ago", description="Time range for query")
    limit: int = Field(100, ge=1, le=2000, description="Maximum number of results")


class LogQueryResponse(BaseModel):
    """Response from log query."""
    
    logs: List[LogEntry] = Field(..., description="List of log entries")
    total_results: int = Field(..., description="Total number of results (may exceed limit)")
    query_executed: str = Field(..., description="The NRQL query that was executed")
    
    def to_json(self) -> str:
        """Convert response to formatted JSON string."""
        data = {
            "logs": [
                {
                    "timestamp": log.timestamp_str if log.timestamp else None,
                    "message": log.message,
                    "level": log.level,
                    "attributes": log.attributes
                }
                for log in self.logs
            ],
            "total_results": self.total_results,
            "query_executed": self.query_executed
        }
        return json.dumps(data, indent=2)