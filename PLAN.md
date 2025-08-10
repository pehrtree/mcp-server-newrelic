# New Relic MCP Server Implementation Plan

## Project Overview
Build a minimal, simple MCP (Model Context Protocol) server in Python to access the New Relic API, starting with log querying capabilities.

## Core Principles
- **Simplicity first** - minimal dependencies, straightforward code
- **Focus on logs** - initial version only implements log querying
- **MCP compliance** - follows MCP server specification

## Architecture

### 1. Project Structure
```
mcp-server-newrelic/
├── pyproject.toml           # Project configuration and dependencies
├── src/
│   └── newrelic_mcp/
│       ├── __init__.py
│       ├── server.py        # Main MCP server implementation
│       ├── client.py        # New Relic API client
│       └── models.py        # Data models for requests/responses
├── tests/
│   ├── test_server.py
│   └── test_client.py
└── README.md
```

### 2. Core Components

#### MCP Server (`server.py`)
- Implements MCP protocol using `mcp` Python library
- Exposes tools for New Relic log queries
- Handles authentication via environment variables or configuration

#### New Relic Client (`client.py`)
- Simple GraphQL client for NerdGraph API
- Handles authentication with User API Key
- Constructs and executes NRQL queries
- Minimal dependencies (just `httpx` or `requests`)

#### Data Models (`models.py`)
- Pydantic models for type safety and validation
- Request/response structures for MCP tools
- New Relic query parameters

### 3. MCP Tools to Implement

#### Tool: `query_logs`
**Purpose:** Query New Relic logs using NRQL

**Parameters:**
- `account_id` (required): New Relic account ID
- `query` (optional): Full NRQL query string
- `message_search` (optional): Simple text search in message field
- `filters` (optional): Key-value pairs for filtering (e.g., {"user_email": "someone@example.com"})
- `since` (optional): Time range (default: "1 hour ago")
- `limit` (optional): Max results (default: 100)

**Behavior:**
- If `query` provided: Use it directly
- If `message_search` provided: Build `WHERE message LIKE '%{search}%'`
- If `filters` provided: Add to WHERE clause
- Combine all parameters into valid NRQL

**Example Usage:**
```json
{
  "tool": "query_logs",
  "arguments": {
    "account_id": "123456",
    "message_search": "error",
    "filters": {"user_email": "someone@example.com"},
    "since": "2 hours ago"
  }
}
```

#### Tool: `get_account_id` (Optional Enhancement)
**Purpose:** Look up account ID by account name

**Parameters:**
- `account_name` (required): Name of the New Relic account

**Returns:** Account ID

### 4. Authentication Strategy
- Use environment variable `NEW_RELIC_API_KEY` for User API Key
- Optional: Support configuration file for multiple accounts
- Validate key format (should start with "NRAK")

### 5. Implementation Phases

#### Phase 1: Basic Setup ✅ Planning
- Set up Python project structure
- Configure pyproject.toml with minimal dependencies
- Implement basic MCP server skeleton

#### Phase 2: New Relic Client
- Implement GraphQL client for NerdGraph
- Build NRQL query constructor
- Add authentication handling
- Test with simple queries

#### Phase 3: MCP Integration
- Implement `query_logs` tool
- Handle parameter validation
- Format responses for Claude
- Add error handling

#### Phase 4: Testing & Documentation
- Unit tests for client and server
- Integration tests with mock New Relic API
- README with setup instructions
- Example usage documentation

### 6. Dependencies (Minimal)
```toml
[project]
dependencies = [
    "mcp",           # MCP protocol implementation
    "httpx",         # HTTP client for API calls
    "pydantic>=2.0", # Data validation
]
```

### 7. Configuration
Environment variables:
- `NEW_RELIC_API_KEY`: User API Key for authentication
- `NEW_RELIC_API_ENDPOINT`: API endpoint (default: https://api.newrelic.com/graphql)

### 8. Error Handling
- Validate API key format
- Handle rate limiting (429 responses)
- Timeout handling for long-running queries
- Clear error messages for missing configuration

### 9. Response Format
Return structured data that Claude can easily interpret:
```json
{
  "logs": [
    {
      "timestamp": "2024-01-01T12:00:00Z",
      "message": "Error occurred in payment processing",
      "level": "ERROR",
      "attributes": {
        "user_email": "someone@example.com",
        "service": "payment-api"
      }
    }
  ],
  "total_results": 150,
  "query_executed": "SELECT * FROM Log WHERE message LIKE '%error%' SINCE 1 hour ago LIMIT 100"
}
```

## Issues to Resolve
None identified - New Relic API capabilities align with all requirements:
- ✅ Personal API Keys (User Keys) are supported
- ✅ Arbitrary query parameters work via NRQL
- ✅ Account ID is required and can be looked up
- ✅ Message attribute search is fully supported

## Next Steps
1. Review and approve this plan
2. Set up basic project structure
3. Implement New Relic client with simple NRQL query
4. Build MCP server wrapper
5. Test with real New Relic account
6. Iterate based on testing feedback

## Success Criteria
- Claude can query New Relic logs with natural language
- Support for complex filtering (user email, service, etc.)
- Clear error messages for configuration issues
- Minimal code complexity
- Fast response times (< 5 seconds for typical queries)