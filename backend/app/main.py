"""
ClickComply — FastAPI Application Entry Point.

This module initializes the FastAPI application, registers routers,
configures CORS middleware, and handles database startup.
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.database import init_db
from app.core.logging import logger
from app.routes import documents, analysis


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan handler.
    Runs database initialization on startup and logs shutdown.
    """
    logger.info(f"Starting {settings.APP_NAME} v{settings.APP_VERSION}")
    await init_db()
    logger.info("Database tables initialized")

    try:
        from app.services.rag_service import init_dpdp_knowledge_base

        init_dpdp_knowledge_base()
        logger.info("DPDP vector knowledge base ready")
    except Exception as exc:
        logger.warning(
            f"DPDP knowledge base seeding skipped (configure AI keys in .env): {exc}"
        )

    yield
    logger.info(f"Shutting down {settings.APP_NAME}")


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description=settings.APP_DESCRIPTION,
    lifespan=lifespan,
)

# CORS — explicit origins (allow_credentials + "*" is invalid per browser spec)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register route modules
app.include_router(documents.router)
app.include_router(analysis.router)


@app.get("/", tags=["Health"])
async def root():
    """Root health check endpoint."""
    from app.services.llm_client import is_ai_configured

    return {
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "running",
        "ai_engine": "READY" if is_ai_configured() else "OLLAMA_NOT_RUNNING",
        "ai_provider": settings.AI_PROVIDER,
    }


@app.get("/health", tags=["Health"])
async def health_check():
    """Detailed health check endpoint."""
    from app.services.ai_service import check_ai_health

    ai_status = await check_ai_health()

    return {
        "app": settings.APP_NAME,
        "status": "healthy",
        "database": "connected",
        "ai": ai_status,
    }
