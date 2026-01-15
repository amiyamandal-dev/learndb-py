"""
LearnDB Web - Main FastAPI Application

A web-based interactive learning platform for understanding
database internals through the LearnDB educational database.
"""

import os
import sys
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.api.routes import sessions, schema, challenges
from backend.core.session_manager import get_session_manager


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle manager for the FastAPI app."""
    # Startup: Initialize session manager
    manager = get_session_manager()
    print(f"LearnDB Web started. Sessions dir: {manager.sessions_dir}")

    yield

    # Shutdown: Cleanup stale sessions
    manager.cleanup_stale_sessions()
    print("LearnDB Web shutdown complete.")


# Create FastAPI app
app = FastAPI(
    title="LearnDB Web",
    description="Interactive SQL learning platform built on LearnDB",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS for development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routers
app.include_router(sessions.router, prefix="/api")
app.include_router(schema.router, prefix="/api")
app.include_router(challenges.router, prefix="/api")


# Health check endpoint
@app.get("/api/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "learndb-web"}


# API info endpoint
@app.get("/api/info")
async def api_info():
    """Get API information and available features."""
    return {
        "name": "LearnDB Web API",
        "version": "1.0.0",
        "features": [
            "SQL query execution",
            "Schema browsing",
            "Query history",
            "Isolated sessions",
            "Interactive challenges",
            "Gamification (XP and levels)",
            "Tutorials (coming soon)"
        ],
        "sql_features": [
            "CREATE TABLE",
            "INSERT INTO",
            "SELECT (with WHERE, GROUP BY, ORDER BY, LIMIT)",
            "UPDATE",
            "DELETE",
            "DROP TABLE",
            "JOIN (INNER, LEFT, RIGHT, FULL, CROSS)"
        ]
    }


# Serve static files (React build) in production
static_dir = Path(__file__).parent / "static"
if static_dir.exists():
    app.mount("/assets", StaticFiles(directory=static_dir / "assets"), name="assets")

    @app.get("/")
    async def serve_spa():
        """Serve the React SPA."""
        return FileResponse(static_dir / "index.html")

    @app.get("/{path:path}")
    async def serve_spa_routes(path: str):
        """Serve React SPA for client-side routing."""
        # Check if it's an API route
        if path.startswith("api/"):
            return {"error": "Not found"}

        # Check if file exists in static
        file_path = static_dir / path
        if file_path.exists() and file_path.is_file():
            return FileResponse(file_path)

        # Otherwise serve index.html for SPA routing
        return FileResponse(static_dir / "index.html")


def main():
    """Entry point for the learndb-web command."""
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)


if __name__ == "__main__":
    main()
