#!/bin/bash
# Run LearnDB Web in development mode
# This starts both the backend API and frontend dev server

cd "$(dirname "$0")/.."
ROOT_DIR=$(pwd)

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}Starting LearnDB Web Development Environment${NC}"
echo "============================================="

# Install/sync Python dependencies with uv
echo -e "${BLUE}Syncing Python dependencies with uv...${NC}"
uv sync

# Check if frontend dependencies are installed
if [ ! -d "frontend/node_modules" ]; then
    echo -e "${BLUE}Installing frontend dependencies with bun...${NC}"
    cd frontend && bun install && cd ..
fi

# Start backend in background
echo -e "${GREEN}Starting backend API on http://localhost:8000${NC}"
cd "$ROOT_DIR"
uv run uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!

# Wait for backend to start
sleep 2

# Start frontend
echo -e "${GREEN}Starting frontend on http://localhost:5173${NC}"
cd "$ROOT_DIR/frontend"
bun run dev &
FRONTEND_PID=$!

echo ""
echo -e "${GREEN}LearnDB Web is running!${NC}"
echo "  - Frontend: http://localhost:5173"
echo "  - Backend API: http://localhost:8000"
echo "  - API Docs: http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop both servers"

# Cleanup function
cleanup() {
    echo ""
    echo "Shutting down..."
    kill $BACKEND_PID 2>/dev/null
    kill $FRONTEND_PID 2>/dev/null
    exit 0
}

trap cleanup SIGINT SIGTERM

# Wait for processes
wait
