#!/bin/bash

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Redirect all output to stderr to avoid interfering with MCP JSON-RPC on stdout
echo "🚀 Starting New Relic MCP Server..." >&2
echo "Script directory: $SCRIPT_DIR" >&2

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

# Auto-build if needed
needs_build=false
if [ ! -d "$SCRIPT_DIR/venv" ]; then
    echo "📦 Virtual environment not found - building..." >&2
    needs_build=true
elif [ -f "$SCRIPT_DIR/build.sh" ] && [ "$SCRIPT_DIR/build.sh" -nt "$SCRIPT_DIR/venv" ]; then
    echo "📦 Build script is newer than venv - rebuilding..." >&2
    needs_build=true
fi

if [ "$needs_build" = true ]; then
    if [ ! -f "$SCRIPT_DIR/build.sh" ]; then
        echo "❌ No build.sh found and no venv exists. Cannot build server." >&2
        exit 1
    fi
    
    echo "Running build.sh..." >&2
    if ! "$SCRIPT_DIR/build.sh"; then
        echo "❌ Build failed!" >&2
        exit 1
    fi
    echo "✅ Build completed successfully" >&2
fi

echo "✓ Using self-contained virtual environment" >&2
echo "Launching New Relic MCP server..." >&2
echo "----------------------------------------" >&2

# Activate venv and run the Python MCP server
source "$SCRIPT_DIR/venv/bin/activate"
exec python -m newrelic_mcp.main