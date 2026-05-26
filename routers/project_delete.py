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

@router.delete("/projects/{project_id}")
def delete_project(project_id: str, db: Session = Depends(get_db)):
    projeto = db.query(models.Projeto).filter(models.Projeto.id == project_id).first()
    if not projeto:
        raise HTTPException(status_code=404, detail="Projeto não encontrado")
    db.query(models.ProjetoEtapa).filter(models.ProjetoEtapa.projeto_id == project_id).delete()
    db.query(models.Custo).filter(models.Custo.projeto_id == project_id).delete()
    db.delete(projeto)
    db.commit()
    return {"message": "Obra deletada com sucesso"}
