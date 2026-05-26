from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import SessionLocal
import models
import base64

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/projects")
def get_projects(
    db: Session = Depends(get_db)
):

    projetos = (
        db.query(models.Projeto)
        .all()
    )

    result = []

    for projeto in projetos:

        custos = (
            db.query(models.Custo)
            .filter(
                models.Custo.projeto_id == projeto.id
            )
            .all()
        )

        total_pago = sum([
            c.valor_pago or 0
            for c in custos
        ])

        total_previsto = sum([
            c.valor_previsto or 0
            for c in custos
        ])

        progresso = 0

        if total_previsto > 0:

            progresso = round(
                (total_pago / total_previsto) * 100,
                2
            )

        imagem = None

        if projeto.imagem:

            imagem = (
                "data:image/png;base64,"
                + base64.b64encode(
                    projeto.imagem
                ).decode("utf-8")
            )

        result.append({
            "id": projeto.id,
            "nome": projeto.nome,
            "categoria": projeto.categoria,
            "status": projeto.status,

            "proprietario":
                projeto.proprietario,

            "cidade":
                projeto.cidade,

            "estado":
                projeto.estado,

            "endereco":
                projeto.endereco,

            "progresso":
                progresso,

            "m2":
                projeto.area_construida,

            "descricao":
                projeto.descricao,

            "imagem":
                imagem
        })

    return result