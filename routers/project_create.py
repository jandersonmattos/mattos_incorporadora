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

@router.post("/projects")
def create_project(data: dict, db: Session = Depends(get_db)):
    data_inicio = None
    data_fim = None
    if data.get("data_inicio"):
        data_inicio = datetime.strptime(data.get("data_inicio"), "%Y-%m-%d").date()
    if data.get("data_fim"):
        data_fim = datetime.strptime(data.get("data_fim"), "%Y-%m-%d").date()
    projeto = models.Projeto(
        nome=data.get("nome"),
        categoria=data.get("categoria"),
        status=data.get("status"),
        data_inicio=data_inicio,
        data_fim=data_fim,
        proprietario=data.get("proprietario"),
        proprietario_email=data.get("proprietario_email"),
        proprietario_telefone=data.get("proprietario_telefone"),
        cep=data.get("cep"),
        endereco=data.get("endereco"),
        numero=data.get("numero"),
        bairro=data.get("bairro"),
        cidade=data.get("cidade"),
        estado=data.get("estado"),
        descricao=data.get("descricao"),
        area_construida=data.get("area_construida"),
        quantidade_unidades=data.get("quantidade_unidades")
    )
    db.add(projeto)
    db.commit()
    db.refresh(projeto)
    etapas = data.get("etapas", [])
    for index, etapa_id in enumerate(etapas):
        relacao = models.ProjetoEtapa(
            projeto_id=projeto.id,
            etapa_id=etapa_id,
            ordem=index + 1
        )
        db.add(relacao)
    db.commit()
    return {"message": "Obra criada com sucesso", "id": projeto.id}
