#!/usr/bin/env python3
"""MCP server for New Relic API access."""

import os
import logging
from typing import Any, Dict, Optional

from mcp.server import Server, NotificationOptions
from mcp.server.models import InitializationOptions
from mcp.types import Tool, TextContent, ImageContent, EmbeddedResource
from mcp.server.models import ServerCapabilities
from pydantic import AnyUrl

from .client import NewRelicClient
from .models import LogQueryRequest, LogQueryResponse

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class NewRelicMCPServer:
    """MCP Server for New Relic API interactions."""
    
    def __init__(self):
        logger.info("Initializing New Relic MCP Server...")
        self.server = Server("newrelic-mcp")
        self.client: Optional[NewRelicClient] = None
        
        # Check environment variables
        api_key = os.getenv("NEW_RELIC_API_KEY")
        endpoint = os.getenv("NEW_RELIC_API_ENDPOINT", "https://api.newrelic.com/graphql")
        
        if api_key:
            logger.info(f"✓ NEW_RELIC_API_KEY found (length: {len(api_key)})")
        else:
            logger.warning("⚠ NEW_RELIC_API_KEY not set - will fail when tools are called")
        
        logger.info(f"✓ API Endpoint: {endpoint}")
        
        self._setup_handlers()
        logger.info("✓ MCP handlers configured")
    
    def _setup_handlers(self):
        """Set up MCP protocol handlers."""
        
        @self.server.list_tools()
        async def list_tools() -> list[Tool]:
            """List available New Relic tools."""
            return [
                Tool(
                    name="query_logs",
                    description="Query New Relic logs using NRQL or simple filters",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "account_id": {
                                "type": "string",
                                "description": "New Relic account ID"
                            },
                            "query": {
                                "type": "string",
                                "description": "Full NRQL query (overrides other parameters)"
                            },
                            "message_search": {
                                "type": "string",
                                "description": "Search text in message field"
                            },
                            "filters": {
                                "type": "object",
                                "description": "Key-value pairs for filtering",
                                "additionalProperties": {"type": "string"}
                            },
                            "since": {
                                "type": "string",
                                "description": "Time range (e.g., '1 hour ago')",
                                "default": "1 hour ago"
                            },
                            "limit": {
                                "type": "integer",
                                "description": "Maximum number of results",
                                "default": 100
                            }
                        },
                        "required": ["account_id"],
                        "additionalProperties": False
                    }
                ),
                Tool(
                    name="get_account_id",
                    description="Look up New Relic account ID by name",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "account_name": {
                                "type": "string",
                                "description": "Name of the New Relic account"
                            }
                        },
                        "required": ["account_name"],
                        "additionalProperties": False
                    }
                )
            ]
        
        @self.server.call_tool()
        async def call_tool(name: str, arguments: Dict[str, Any]) -> list[TextContent | ImageContent | EmbeddedResource]:
            """Execute a New Relic tool."""
            if not self.client:
                api_key = os.getenv("NEW_RELIC_API_KEY")
                if not api_key:
                    return [TextContent(
                        type="text",
                        text="Error: NEW_RELIC_API_KEY environment variable not set"
                    )]
                
                endpoint = os.getenv("NEW_RELIC_API_ENDPOINT", "https://api.newrelic.com/graphql")
                self.client = NewRelicClient(api_key, endpoint)
            
            try:
                if name == "query_logs":
                    request = LogQueryRequest(**arguments)
                    result = await self.client.query_logs(request)
                    return [TextContent(type="text", text=result.to_json())]
                
                elif name == "get_account_id":
                    account_name = arguments.get("account_name")
                    account_id = await self.client.get_account_id(account_name)
                    return [TextContent(
                        type="text",
                        text=f"Account ID for '{account_name}': {account_id}"
                    )]
                
                else:
                    return [TextContent(
                        type="text",
                        text=f"Unknown tool: {name}"
                    )]
                    
            except Exception as e:
                logger.error(f"Error executing tool {name}: {e}")
                return [TextContent(
                    type="text",
                    text=f"Error: {str(e)}"
                )]
    
    async def run(self):
        """Run the MCP server."""
        logger.info("Starting New Relic MCP Server...")
        logger.info("Server name: newrelic-mcp")
        logger.info("Server version: 0.1.0")
        logger.info("Available tools: query_logs, get_account_id")
        
        from mcp.server.stdio import stdio_server
        
        logger.info("Setting up stdio transport...")
        async with stdio_server() as (read_stream, write_stream):
            logger.info("🚀 MCP Server ready - waiting for client connections...")
            await self.server.run(
                read_stream,
                write_stream,
                InitializationOptions(
                    server_name="newrelic-mcp",
                    server_version="0.1.0",
                    capabilities=ServerCapabilities(
                        tools={}
                    )
                )
            )


