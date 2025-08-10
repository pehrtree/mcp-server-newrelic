#!/bin/bash

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Redirect all output to stderr to avoid interfering with MCP JSON-RPC on stdout
echo "🚀 Starting New Relic MCP Server..." >&2
echo "Script directory: $SCRIPT_DIR" >&2
echo "Working directory: $(pwd)" >&2

# Load environment variables from .env file (from script directory)
if [ -f "$SCRIPT_DIR/.env" ]; then
    echo "✓ Loading environment variables from .env file" >&2
    export $(grep -v '^#' "$SCRIPT_DIR/.env" | xargs)
else
    echo "⚠ No .env file found - environment variables may need to be set manually" >&2
fi

# Check for required environment variables
if [ -z "$NEW_RELIC_API_KEY" ]; then
    echo "⚠ NEW_RELIC_API_KEY not set - server will fail when tools are called" >&2
else
    echo "✓ NEW_RELIC_API_KEY is set (length: ${#NEW_RELIC_API_KEY})" >&2
fi

# Install dependencies if needed (check if package is installed)
echo "Checking Python dependencies..." >&2
if ! python -c "import newrelic_mcp" 2>/dev/null; then
    echo "Installing dependencies..." >&2
    cd "$SCRIPT_DIR"
    echo "Running: pip install -e . in directory: $(pwd)" >&2
    pip install -e . 2>&1 | tee /tmp/pip_install.log >&2
    if [ ${PIPESTATUS[0]} -eq 0 ]; then
        echo "✓ Dependencies installed successfully" >&2
    else
        echo "❌ Failed to install dependencies" >&2
        echo "Pip install output:" >&2
        tail -10 /tmp/pip_install.log >&2
        exit 1
    fi
else
    echo "✓ Dependencies already installed" >&2
fi

echo "Launching New Relic MCP server..." >&2
echo "----------------------------------------" >&2

# Run the Python MCP server
exec "$SCRIPT_DIR/server"