#!/bin/bash

# Load environment variables from .env file
if [ -f .env ]; then
    export $(grep -v '^#' .env | xargs)
fi

# Install dependencies if needed (check if package is installed)
if ! python -c "import newrelic_mcp" 2>/dev/null; then
    echo "Installing dependencies..."
    pip install -e . > /dev/null 2>&1
fi

# Run the Python MCP server
exec ./server