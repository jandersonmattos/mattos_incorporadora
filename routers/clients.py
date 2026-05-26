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

@router.get("/clients")
def get_clients(db: Session = Depends(get_db)):
    clientes = db.query(models.Cliente).all()
    resultado = []
    for cliente in clientes:
        resultado.append({
            "id": str(cliente.id),
            "nome": cliente.name or cliente.trade_name or cliente.corporate_name or "",
            "tipo_pessoa": cliente.person_type,
            "telefone": cliente.phone or "",
            "celular": cliente.phone or "",
            "cep": cliente.zip_code or "",
            "endereco": cliente.street or "",
            "numero": cliente.number or "",
            "bairro": cliente.neighborhood or "",
            "complemento": cliente.complement or "",
            "cidade": cliente.city or "",
            "estado": cliente.state or "",
            "pais": cliente.country or ""
        })
    return resultado

@router.get("/clients/{client_id}")
def get_client(client_id: str, db: Session = Depends(get_db)):
    cliente = db.query(models.Cliente).filter(models.Cliente.id == client_id).first()
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente não encontrado")
    return {
        "id": str(cliente.id),
        "tipo": cliente.person_type,
        "nome": cliente.name,
        "cpf": cliente.cpf,
        "rg": cliente.rg,
        "razao_social": cliente.corporate_name,
        "nome_fantasia": cliente.trade_name,
        "cnpj": cliente.cnpj,
        "email": cliente.email,
        "telefone": cliente.phone,
        "cep": cliente.zip_code,
        "endereco": cliente.street,
        "numero": cliente.number,
        "bairro": cliente.neighborhood,
        "complemento": cliente.complement,
        "cidade": cliente.city,
        "estado": cliente.state,
        "pais": cliente.country
    }
