#!/usr/bin/env python3
"""Main entry point for New Relic MCP server."""

import asyncio
from .server import NewRelicMCPServer


async def main():
    """Main entry point."""
    server = NewRelicMCPServer()
    await server.run()


if __name__ == "__main__":
    asyncio.run(main())