# MCP Server for New Relic

This repository contains an MCP (Model Context Protocol) server that enables Claude to query New Relic APIs directly.

## Features

- **Query New Relic Logs** - Search and filter logs using NRQL or simple filters
- **Account Lookup** - Find account IDs by account name
- **Automatic Response Truncation** - Handles large responses automatically to stay within token limits
- **Built for Claude** - Designed specifically for use with Claude Code and Claude Desktop

Currently supports log queries, but can be extended to other New Relic capabilities like metrics, APM data, and more.

## Architecture

The `oneshot` directory contains a Python-based MCP server built by Claude in nearly one shot, based on PLAN.md. Recent revisions add automatic response size limiting to prevent token overruns when New Relic returns large result sets.

## Installation & Configuration

### Prerequisites

- Python 3.10+
- New Relic User API Key (starts with `NRAK-`)
- Claude Code or Claude Desktop

### Setup for Claude Desktop

1. **Clone the repository:**
   ```bash
   git clone https://github.com/yourusername/mcp-server-newrelic.git
   cd mcp-server-newrelic
   ```

2. **Create environment file:**
   Create a `.env` file in the `oneshot` folder with your New Relic API key:
   ```bash
   echo "NEW_RELIC_API_KEY=NRAK-your-key-here" > oneshot/.env
   ```

3. **Build the server:**
   ```bash
   cd oneshot
   ./build.sh
   ```

4. **Configure Claude Desktop:**
   Edit your Claude Desktop configuration file:
   - macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`
   - Windows: `%APPDATA%\Claude\claude_desktop_config.json`
   - Linux: `~/.config/Claude/claude_desktop_config.json`

   Add the New Relic MCP server to the `mcpServers` section:
   ```json
   {
     "mcpServers": {
       "newrelic": {
         "command": "/absolute/path/to/mcp-server-newrelic/oneshot/run_server.sh",
         "cwd": "/absolute/path/to/mcp-server-newrelic/oneshot"
       }
     }
   }
   ```

5. **Restart Claude Desktop** to load the new configuration.

### Setup for Claude Code

For Claude Code, the configuration is similar but uses the `.claudecode/config.json` file in your project:

1. **Create configuration directory:**
   ```bash
   mkdir -p .claudecode
   ```

2. **Create config file:**
   ```json
   {
     "mcpServers": {
       "newrelic": {
         "command": "./oneshot/run_server.sh",
         "cwd": "./oneshot",
         "env": {
           "NEW_RELIC_API_KEY": "NRAK-your-key-here"
         }
       }
     }
   }
   ```

3. **Open your project in Claude Code** - it will automatically detect and load the MCP server.

## Usage Examples

Once configured, you can ask Claude to:

- "Search New Relic logs for errors in the last 24 hours"
- "Find logs with user_email:'user@example.com' in WMG Production account"
- "Query logs with message containing 'timeout' from the payment service"
- "Get the account ID for 'Production' account"

The server automatically handles:
- Large result sets by truncating to fit within token limits
- Account name to ID resolution
- NRQL query construction from simple filters

## Available Tools

### `query_logs`
Query New Relic logs with flexible filtering options:
- `account_id` - New Relic account ID (required)
- `query` - Full NRQL query (overrides other parameters)
- `message_search` - Search text in message field
- `filters` - Key-value pairs for filtering
- `since` - Time range (e.g., '1 hour ago', '24 hours ago')
- `limit` - Maximum results (default: 100, max: 2000)

### `get_account_id`
Look up account ID by name:
- `account_name` - Name of the New Relic account

## Response Size Management

The server automatically manages response sizes to prevent token limit issues:
- Responses larger than 20,000 characters are automatically truncated
- Uses efficient binary search to find the maximum number of logs that fit
- Includes metadata about truncation when it occurs
- Completely transparent - Claude doesn't need to handle pagination

## Development

### Project Structure
```
mcp-server-newrelic/
├── oneshot/
│   ├── src/
│   │   └── newrelic_mcp/
│   │       ├── server.py    # MCP server implementation
│   │       ├── client.py    # New Relic API client
│   │       └── models.py    # Data models
│   ├── build.sh             # Build script
│   ├── run_server.sh        # Server launcher
│   └── .env                 # Environment variables (create this)
├── PLAN.md                  # Original implementation plan
└── README.md               # This file
```

### Extending the Server

To add new New Relic capabilities:

1. Add new tool definitions in `server.py`
2. Implement API methods in `client.py`
3. Create data models in `models.py`
4. Update this README with usage examples

## Troubleshooting

- **"API key does not start with 'NRAK'"** - Ensure you're using a User API Key, not a License Key
- **"Rate limit exceeded"** - Wait a moment and try again, New Relic has API rate limits
- **"Account not found"** - Verify the account name matches exactly (case-insensitive)
- **Large responses timing out** - The server automatically truncates, but you can reduce the `limit` parameter

## License

MIT