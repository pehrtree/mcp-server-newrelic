# New Relic MCP Server

A minimal MCP (Model Context Protocol) server for accessing New Relic logs through Claude.

## Features

- Query New Relic logs using NRQL or simple filters
- Search log messages by text
- Filter logs by arbitrary attributes (user_email, service, etc.)
- Look up account IDs by account name
- Simple, minimal implementation focused on clarity

## Installation

```bash
# Clone the repository
git clone <your-repo>
cd mcp-server-newrelic/oneshot

# Install dependencies
pip install -e .
```

## Configuration

Set your New Relic User API Key as an environment variable:

```bash
export NEW_RELIC_API_KEY="NRAK-YOUR-API-KEY-HERE"
```

Optional: Set a custom API endpoint (defaults to US datacenter):
```bash
export NEW_RELIC_API_ENDPOINT="https://api.eu.newrelic.com/graphql"  # For EU
```

## Usage with Claude Desktop & Claude Code

Add to your Claude configuration (`~/Library/Application Support/Claude/claude_desktop_config.json`).

**Note**: This same configuration works for both Claude Desktop and Claude Code.

```json
{
  "mcpServers": {
    "newrelic": {
      "command": "python",
      "args": ["-m", "newrelic_mcp.server"],
      "env": {
        "NEW_RELIC_API_KEY": "NRAK-YOUR-API-KEY-HERE"
      }
    }
  }
}
```

## Available Tools

### `query_logs`

Query New Relic logs with various options:

**Parameters:**
- `account_id` (required): Your New Relic account ID
- `query` (optional): Full NRQL query - overrides all other parameters
- `message_search` (optional): Text to search in log messages
- `filters` (optional): Key-value pairs for filtering
- `since` (optional): Time range, default "1 hour ago"
- `limit` (optional): Max results, default 100

**Examples:**

```json
// Simple message search
{
  "tool": "query_logs",
  "arguments": {
    "account_id": "123456",
    "message_search": "error",
    "since": "2 hours ago"
  }
}

// Filter by user email
{
  "tool": "query_logs",
  "arguments": {
    "account_id": "123456",
    "filters": {
      "user_email": "john@example.com",
      "level": "ERROR"
    }
  }
}

// Direct NRQL query
{
  "tool": "query_logs",
  "arguments": {
    "account_id": "123456",
    "query": "SELECT * FROM Log WHERE service = 'payment-api' AND level = 'ERROR' SINCE 1 day ago LIMIT 50"
  }
}
```

### `get_account_id`

Look up account ID by account name:

```json
{
  "tool": "get_account_id",
  "arguments": {
    "account_name": "Production Account"
  }
}
```

## Example Claude Interactions

```
You: "Show me any errors in the payment service from the last hour"
Claude: [Uses query_logs with filters: {"service": "payment-api", "level": "ERROR"}]

You: "Find logs for user john@example.com who had issues yesterday"
Claude: [Uses query_logs with filters: {"user_email": "john@example.com"}, since: "1 day ago"]

You: "Search for 'timeout' errors in production"
Claude: [Uses query_logs with message_search: "timeout", filters: {"level": "ERROR"}]
```

## Using with Claude Code for Bug Investigation

This MCP server is perfect for debugging workflows with Claude Code:

```
You (in Claude Code): "I'm seeing timeout errors in production. Can you search New Relic logs for timeout issues and help me identify the problem in my codebase?"

Claude Code workflow:
1. Uses query_logs to search for "timeout" errors in your New Relic account
2. Analyzes the log patterns and error messages
3. Examines your codebase to find related code
4. Suggests fixes based on both the logs and your code structure
```

## Development

### Running Tests

```bash
pip install -e ".[dev]"
pytest
```

### Code Style

```bash
black src/
ruff check src/
```

## Architecture

The server consists of three main components:

1. **server.py**: MCP protocol implementation
   - Registers available tools
   - Handles tool execution
   - Manages client initialization

2. **client.py**: New Relic API client
   - Builds NRQL queries from parameters
   - Executes GraphQL requests
   - Handles authentication

3. **models.py**: Data models
   - Pydantic models for validation
   - Request/response structures
   - Type safety

## Limitations

- Rate limits: 3,000 NRQL queries per account per minute
- Query timeout: 30 seconds
- Max results per query: 2,000 (configurable via limit parameter)

## Security

- API keys are never logged or exposed
- Uses environment variables for sensitive configuration
- Validates API key format (should start with "NRAK")

## Troubleshooting

### "API key does not start with 'NRAK'"
Your API key might be outdated. Generate a new User API Key from the New Relic UI.

### Rate limit errors
You've exceeded the 3,000 queries/minute limit. Wait a moment before retrying.

### Empty results
- Check your account ID is correct
- Verify the time range includes data
- Ensure your API key has access to the account

## License

MIT