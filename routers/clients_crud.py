from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import SessionLocal
import models
from datetime import datetime

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/clients")
def create_client(data: dict, db: Session = Depends(get_db)):
    try:
        cliente = models.Cliente(
            name=data.get("name"),
            person_type=data.get("person_type"),
            cpf=data.get("cpf"),
            rg=data.get("rg"),
            corporate_name=data.get("corporate_name"),
            trade_name=data.get("trade_name"),
            cnpj=data.get("cnpj"),
            email=data.get("email"),
            phone=data.get("phone"),
            zip_code=data.get("zip_code"),
            street=data.get("street"),
            number=data.get("number"),
            neighborhood=data.get("neighborhood"),
            complement=data.get("complement"),
            city=data.get("city"),
            state=data.get("state"),
            country=data.get("country"),
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        db.add(cliente)
        db.commit()
        db.refresh(cliente)
        return {"message": "Cliente criado com sucesso", "id": str(cliente.id)}
    except Exception as e:
        db.rollback()
        print(e)
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/clients/{client_id}")
def update_client(client_id: str, data: dict, db: Session = Depends(get_db)):
    cliente = db.query(models.Cliente).filter(models.Cliente.id == client_id).first()
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente não encontrado")
    for field in [
        "name", "person_type", "cpf", "rg", "corporate_name", "trade_name", "cnpj", "email", "phone", "zip_code", "street", "number", "neighborhood", "complement", "city", "state", "country"
    ]:
        if field in data:
            setattr(cliente, field, data[field])
    cliente.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(cliente)
    return {"message": "Cliente atualizado com sucesso"}

@router.delete("/clients/{client_id}")
def delete_client(client_id: str, db: Session = Depends(get_db)):
    cliente = db.query(models.Cliente).filter(models.Cliente.id == client_id).first()
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente não encontrado")
    db.delete(cliente)
    db.commit()
    return {"message": "Cliente deletado com sucesso"}
