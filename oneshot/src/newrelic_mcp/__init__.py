"""New Relic MCP Server package."""

from .server import NewRelicMCPServer
from .main import main
from .client import NewRelicClient
from .models import LogEntry, LogQueryRequest, LogQueryResponse

__version__ = "0.1.0"
__all__ = [
    "NewRelicMCPServer",
    "NewRelicClient", 
    "LogEntry",
    "LogQueryRequest",
    "LogQueryResponse",
    "main"
]