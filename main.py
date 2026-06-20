import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
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
    reminders,
    stages,
    supplier_types,
    suppliers,
)

# Ensure tables exist for local/dev bootstrap.
Base.metadata.create_all(bind=engine)

# Safe migrations: add columns/tables that may not exist yet.
def run_migrations():
    from sqlalchemy import text
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

run_migrations()

app = FastAPI(title="Incorporadora API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

if os.path.isdir("uploads"):
    app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

if os.path.isdir("assets"):
    app.mount("/assets", StaticFiles(directory="assets"), name="assets")

app.include_router(auth.router)
app.include_router(stages.router)
app.include_router(projects.router)
app.include_router(project_detail.router)
app.include_router(project_create.router)
app.include_router(project_update.router)
app.include_router(project_delete.router)
app.include_router(dashboard.router)
app.include_router(reminders.router)
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


@app.get("/")
def healthcheck():
    return {"status": "ok"}
