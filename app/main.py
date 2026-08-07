import contextlib
from collections.abc import AsyncGenerator
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import get_settings
from app.core.logging import setup_logging, get_logger
from app.core.exceptions import register_exception_handlers
from app.database.session import init_db, close_db
from app.api.v1.routes.health import router as health_router
from app.api.v1.routes.restaurant import router as restaurant_router
from app.api.v1.routes.scan import router as scan_router


logger = get_logger(__name__)

@contextlib.asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Lifespan context manager for FastAPI."""
    # Startup
    setup_logging()
    logger.info("Starting up application...")
    await init_db()
    
    yield
    
    # Shutdown
    logger.info("Shutting down application...")
    await close_db()

app = FastAPI(
    title="Restaurant Lead Finder AI",
    description="API for finding and analyzing restaurant leads using Google Places and AI.",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Exception handlers
register_exception_handlers(app)

# Routers
app.include_router(health_router, prefix="/api/v1")
app.include_router(restaurant_router, prefix="/api/v1")
app.include_router(scan_router, prefix="/api/v1")


@app.get("/")
async def root() -> dict[str, str]:
    """Root endpoint."""
    return {
        "message": "Welcome to Restaurant Lead Finder AI API",
        "docs": "/docs",
        "redoc": "/redoc"
    }
