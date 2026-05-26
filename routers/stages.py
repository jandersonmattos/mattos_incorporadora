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

@router.get("/stages")
def get_stages(db: Session = Depends(get_db)):
    etapas = db.query(models.EtapaObra).order_by(models.EtapaObra.nome.asc()).all()
    return [{"id": etapa.id, "name": etapa.nome} for etapa in etapas]
