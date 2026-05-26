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

@router.get("/cost-bases/{version_id}/services")
def get_cost_base_services(version_id: str, search: str = None, limit: int = 1000, offset: int = 0, db: Session = Depends(get_db)):
    version = db.query(models.CostBaseVersion).filter(models.CostBaseVersion.id == version_id).first()
    if not version:
        raise HTTPException(status_code=404, detail="Versão da base não encontrada")
    query = db.query(models.CostService).filter(models.CostService.version_id == version_id)
    if search:
        search_term = f"%{search}%"
        query = query.filter(
            (models.CostService.description.ilike(search_term)) |
            (models.CostService.code.ilike(search_term))
        )
    total = query.count()
    services = query.order_by(models.CostService.code.asc()).offset(offset).limit(limit).all()
    nodes = {}
    for service in services:
        nodes[service.code] = {
            "id": str(service.id),
            "code": service.code,
            "description": service.description,
            "unit": service.unit,
            "unit_cost": float(service.unit_cost or 0),
            "labor_cost": float(service.labor_cost or 0),
            "material_cost": float(service.material_cost or 0),
            "equipment_cost": float(service.equipment_cost or 0),
            "total_cost": float(service.total_cost or 0),
            "children": []
        }
    tree = []
    for code, node in nodes.items():
        parts = code.split(".")
        if len(parts) == 1:
            tree.append(node)
        else:
            parent_code = ".".join(parts[:-1])
            parent = nodes.get(parent_code)
            if parent:
                parent["children"].append(node)
            else:
                tree.append(node)
    return {
        "total": total,
        "limit": limit,
        "offset": offset,
        "version": {
            "id": str(version.id),
            "month": version.month,
            "year": version.year,
            "state_code": version.state_code,
            "is_desonerado": version.is_desonerado
        },
        "tree": tree
    }
