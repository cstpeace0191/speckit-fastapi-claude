import os
import mimetypes
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

# Fix Windows registry MIME type issue for JS module scripts (.js, .mjs, .css, etc.)
mimetypes.add_type("application/javascript", ".js")
mimetypes.add_type("application/javascript", ".mjs")
mimetypes.add_type("text/css", ".css")
mimetypes.add_type("image/svg+xml", ".svg")
mimetypes.add_type("application/json", ".json")
mimetypes.add_type("image/x-icon", ".ico")

from . import persistence as db
from .routes.greeting import router as greeting_router
from .routes.items import router as items_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Initialize Database
    try:
        await db.init()
    except Exception as e:
        print(f"Error during database initialization: {e}")
        raise e

    yield

    # Shutdown: Teardown Database
    try:
        await db.teardown()
    except Exception as e:
        print(f"Error during database teardown: {e}")


app = FastAPI(
    title="Getting Started Todo App API",
    description="FastAPI + Uvicorn Async Backend for Todo App",
    version="1.0.0",
    lifespan=lifespan,
)

# Enable CORS for local development and cross-origin requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API Routers
app.include_router(greeting_router)
app.include_router(items_router)

# Mount static files (React SPA) if directory exists
static_dir = os.path.join(os.path.dirname(__file__), "static")
if os.path.exists(static_dir):
    app.mount("/", StaticFiles(directory=static_dir, html=True), name="static")
