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
from app.api.v1.routes.chennai import router as chennai_router
from app.api.v1.routes.leads import router as leads_router
from app.api.v1.routes.follow_up import router as follow_up_router
from app.api.v1.routes.intelligence import router as intelligence_router
from app.api.v1.routes.watchlist import router as watchlist_router
from app.api.v1.routes.reports import router as reports_router

logger = get_logger(__name__)

@contextlib.asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    setup_logging()
    logger.info("Starting up application...")
    await init_db()
    yield
    logger.info("Shutting down application...")
    await close_db()

app = FastAPI(
    title="Restaurant Lead Finder AI",
    description="AI-Powered Restaurant Lead Intelligence Platform for Chennai",
    version="2.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

register_exception_handlers(app)

app.include_router(health_router, prefix="/api/v1")
app.include_router(restaurant_router, prefix="/api/v1")
app.include_router(scan_router, prefix="/api/v1")
app.include_router(chennai_router, prefix="/api/v1")
app.include_router(leads_router, prefix="/api/v1")
app.include_router(follow_up_router, prefix="/api/v1")
app.include_router(intelligence_router, prefix="/api/v1")
app.include_router(watchlist_router, prefix="/api/v1")
app.include_router(reports_router, prefix="/api/v1")

@app.get("/")
async def root() -> dict[str, str]:
    return {
        "message": "Welcome to Restaurant Lead Finder AI API",
        "docs": "/docs",
        "redoc": "/redoc"
    }
