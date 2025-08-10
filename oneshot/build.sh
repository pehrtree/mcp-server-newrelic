#!/bin/bash

# Build script to create a self-contained MCP server

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "🏗️  Building self-contained New Relic MCP server..."

# Clean previous build
if [ -d "venv" ]; then
    echo "Removing existing venv..."
    rm -rf venv
fi

# Create virtual environment using uv
echo "Creating virtual environment with uv..."
uv venv venv

# Activate virtual environment
source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
uv pip install -e .

echo "✅ Build complete!"
echo ""
echo "The MCP server is now self-contained in ./venv/"
echo "Run './run_server.sh' to start the server."