import os
import logging
import traceback

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

import models
from database import Base, engine
from routers import (
    auth,
    bdi,
    budgets,
    clients,
    clients_crud,
    cost_bases,
    costs,
    dashboard,
    files,
    folders,
    items,
    project_create,
    project_delete,
    project_detail,
    project_update,
    projects,
    stages,
    supplier_types,
    suppliers,
)

# ---------------------------------------------------------------------------
# Logging — emit to stdout so Railway captures every line
# ---------------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Database bootstrap
# ---------------------------------------------------------------------------
logger.info("Running Base.metadata.create_all …")
try:
    Base.metadata.create_all(bind=engine)
    logger.info("create_all completed successfully")
except Exception as exc:
    logger.error("create_all failed: %s", exc, exc_info=True)
    raise


def run_migrations():
    from sqlalchemy import text

    logger.info("Running safe migrations …")
    try:
        with engine.connect() as conn:
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS itens_etapa (
                    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                    nome VARCHAR NOT NULL,
                    projeto_id VARCHAR REFERENCES projetos(id),
                    etapa_id UUID REFERENCES etapas_obra(id)
                )
            """))
            conn.execute(text("""
                ALTER TABLE custos
                ADD COLUMN IF NOT EXISTS item_id UUID REFERENCES itens_etapa(id)
            """))
            conn.commit()
        logger.info("Migrations completed successfully")
    except Exception as exc:
        logger.error("Migration failed: %s", exc, exc_info=True)
        raise


run_migrations()

# ---------------------------------------------------------------------------
# App
# ---------------------------------------------------------------------------
app = FastAPI(title="Incorporadora API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------------------------
# Global exception handler — log every unhandled error with a full traceback
# ---------------------------------------------------------------------------
@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    logger.error(
        "Unhandled exception on %s %s\n%s",
        request.method,
        request.url,
        traceback.format_exc(),
    )
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error", "error": str(exc)},
    )

# ---------------------------------------------------------------------------
# Request logging middleware
# ---------------------------------------------------------------------------
@app.middleware("http")
async def log_requests(request: Request, call_next):
    logger.info("→ %s %s", request.method, request.url)
    try:
        response = await call_next(request)
        logger.info("← %s %s  status=%s", request.method, request.url, response.status_code)
        return response
    except Exception as exc:
        logger.error(
            "Request %s %s raised an unhandled exception: %s\n%s",
            request.method,
            request.url,
            exc,
            traceback.format_exc(),
        )
        raise

# ---------------------------------------------------------------------------
# Static files (only mount when the directories actually exist)
# ---------------------------------------------------------------------------
if os.path.isdir("uploads"):
    app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

if os.path.isdir("assets"):
    app.mount("/assets", StaticFiles(directory="assets"), name="assets")

# ---------------------------------------------------------------------------
# Routers
# ---------------------------------------------------------------------------
app.include_router(auth.router)
app.include_router(stages.router)
app.include_router(projects.router)
app.include_router(project_detail.router)
app.include_router(project_create.router)
app.include_router(project_update.router)
app.include_router(project_delete.router)
app.include_router(dashboard.router)
app.include_router(supplier_types.router)
app.include_router(suppliers.router)
app.include_router(clients.router)
app.include_router(clients_crud.router)
app.include_router(bdi.router)
app.include_router(cost_bases.router)
app.include_router(costs.router)
app.include_router(items.router)
app.include_router(budgets.router)
app.include_router(folders.router)
app.include_router(files.router)

# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@app.get("/health", tags=["health"])
def health():
    """Lightweight liveness probe — no database access."""
    return {"status": "ok"}


@app.get("/health/db", tags=["health"])
def health_db():
    """Readiness probe — verifies the database is reachable."""
    from sqlalchemy import text
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return {"status": "ok", "database": "reachable"}
    except Exception as exc:
        logger.error("Database health check failed: %s", exc, exc_info=True)
        return JSONResponse(
            status_code=503,
            content={"status": "error", "database": "unreachable", "detail": str(exc)},
        )


@app.get("/")
def root():
    return {"status": "ok"}
