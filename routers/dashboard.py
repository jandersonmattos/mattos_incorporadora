from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import SessionLocal
import models

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/dashboard/projects")
def get_dashboard_projects(db: Session = Depends(get_db)):
    projetos = db.query(models.Projeto).all()
    result = []
    for p in projetos:
        custos = db.query(models.Custo).filter(models.Custo.projeto_id == p.id).all()
        total_pago = sum([c.valor_pago or 0 for c in custos])
        total_previsto = sum([c.valor_previsto or 0 for c in custos])
        progress = 0
        if total_previsto > 0:
            progress = round((total_pago / total_previsto) * 100, 2)
        if progress >= 90:
            status = "Fase final"
        elif progress >= 50:
            status = "Em andamento"
        else:
            status = "Fundação"
        result.append({
            "id": p.id,
            "name": p.nome,
            "status": status,
            "progress": progress,
            "budget": total_previsto
        })
    return result

@router.get("/dashboard/project/{project_id}")
def get_dashboard_project(project_id: str, db: Session = Depends(get_db)):
    p = db.query(models.Projeto).filter(models.Projeto.id == project_id).first()
    if not p:
        raise HTTPException(status_code=404, detail="Projeto não encontrado")
    custos = db.query(models.Custo).filter(models.Custo.projeto_id == p.id).all()
    total_pago = sum([c.valor_pago or 0 for c in custos])
    total_previsto = sum([c.valor_previsto or 0 for c in custos])
    unidades = p.quantidade_unidades or 0
    lucro = round(total_pago * 0.3, 2)
    venda_total = round(total_pago + lucro, 2)
    costs = []
    for c in custos:
        costs.append({
            "id": c.id,
            "category": c.categoria.nome if c.categoria else "-",
            "stage": c.etapa.nome if c.etapa else "-",
            "description": c.descricao,
            "paid": c.valor_pago or 0,
            "planned": c.valor_previsto or 0
        })
    return {
        "project": {"id": p.id, "name": p.nome},
        "total_paid": total_pago,
        "total_planned": total_previsto,
        "units": unidades,
        "profit": lucro,
        "sale_total": venda_total,
        "costs": costs
    }
