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

@router.get("/supplier-types")
def get_supplier_types(db: Session = Depends(get_db)):
    tipos = db.query(models.TipoFornecedor).order_by(models.TipoFornecedor.nome.asc()).all()
    return [{"id": tipo.id, "nome": tipo.nome} for tipo in tipos]

@router.get("/supplier-types/{type_id}")
def get_supplier_type(type_id: int, db: Session = Depends(get_db)):
    tipo = db.query(models.TipoFornecedor).filter(models.TipoFornecedor.id == type_id).first()
    if not tipo:
        raise HTTPException(status_code=404, detail="Tipo não encontrado")
    return {"id": tipo.id, "nome": tipo.nome}

@router.post("/supplier-types")
def create_supplier_type(data: dict, db: Session = Depends(get_db)):
    tipo = models.TipoFornecedor(nome=data.get("nome"))
    db.add(tipo)
    db.commit()
    db.refresh(tipo)
    return {"message": "Tipo criado com sucesso", "id": tipo.id}

@router.put("/supplier-types/{type_id}")
def update_supplier_type(type_id: int, data: dict, db: Session = Depends(get_db)):
    tipo = db.query(models.TipoFornecedor).filter(models.TipoFornecedor.id == type_id).first()
    if not tipo:
        raise HTTPException(status_code=404, detail="Tipo não encontrado")
    tipo.nome = data.get("nome")
    db.commit()
    return {"message": "Tipo atualizado com sucesso"}

@router.delete("/supplier-types/{type_id}")
def delete_supplier_type(type_id: int, db: Session = Depends(get_db)):
    tipo = db.query(models.TipoFornecedor).filter(models.TipoFornecedor.id == type_id).first()
    if not tipo:
        raise HTTPException(status_code=404, detail="Tipo não encontrado")
    db.delete(tipo)
    db.commit()
    return {"message": "Tipo deletado com sucesso"}
