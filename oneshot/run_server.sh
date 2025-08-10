#!/bin/bash

echo "🚀 Starting New Relic MCP Server..."
echo "Working directory: $(pwd)"

# Load environment variables from .env file
if [ -f .env ]; then
    echo "✓ Loading environment variables from .env file"
    export $(grep -v '^#' .env | xargs)
else
    echo "⚠ No .env file found - environment variables may need to be set manually"
fi

# Check for required environment variables
if [ -z "$NEW_RELIC_API_KEY" ]; then
    echo "⚠ NEW_RELIC_API_KEY not set - server will fail when tools are called"
else
    echo "✓ NEW_RELIC_API_KEY is set (length: ${#NEW_RELIC_API_KEY})"
fi

# Install dependencies if needed (check if package is installed)
echo "Checking Python dependencies..."
if ! python -c "import newrelic_mcp" 2>/dev/null; then
    echo "Installing dependencies..."
    pip install -e . > /dev/null 2>&1
    if [ $? -eq 0 ]; then
        echo "✓ Dependencies installed successfully"
    else
        echo "❌ Failed to install dependencies"
        exit 1
    fi
else
    echo "✓ Dependencies already installed"
fi

echo "Launching New Relic MCP server..."
echo "----------------------------------------"

# Run the Python MCP server
exec ./server