from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
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

        # Progresso do projeto = media do progresso das etapas (0 a 100)
        media_progresso = (
            db.query(
                func.coalesce(
                    func.avg(models.ProjetoEtapa.progresso),
                    0.0
                )
            )
            .filter(
                models.ProjetoEtapa.projeto_id == projeto.id
            )
            .scalar()
        )

        progresso = round(float(media_progresso or 0), 2)

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