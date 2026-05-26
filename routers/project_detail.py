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


def _format_brl(value: float):
    amount = float(value or 0)
    formatted = f"{amount:,.2f}"
    formatted = formatted.replace(",", "#").replace(".", ",").replace("#", ".")
    return f"R$ {formatted}"


def _build_stage_totals(
    db: Session,
    project_id: str,
    projeto_etapa: models.ProjetoEtapa
):

    custos = []

    if projeto_etapa.etapa_id:
        custos = (
            db.query(models.Custo)
            .filter(
                models.Custo.projeto_id == project_id,
                models.Custo.etapa_id == projeto_etapa.etapa_id
            )
            .all()
        )

    total_pago = round(sum([
        c.valor_pago or 0
        for c in custos
    ]), 2)

    total_previsto = round(sum([
        c.valor_previsto or 0
        for c in custos
    ]), 2)

    total_a_pagar = round(
        total_previsto - total_pago,
        2
    )

    return {
        "project_stage_id": projeto_etapa.id,
        "etapa_id": (
            str(projeto_etapa.etapa.id)
            if projeto_etapa.etapa
            else None
        ),
        "etapa_nome": (
            projeto_etapa.etapa.nome
            if projeto_etapa.etapa
            else projeto_etapa.nome_customizado
        ),
        "total_etapa": total_previsto,
        "total_pago": total_pago,
        "total_a_pagar": total_a_pagar,
        "total_etapa_formatado": _format_brl(total_previsto),
        "total_pago_formatado": _format_brl(total_pago),
        "total_a_pagar_formatado": _format_brl(total_a_pagar),
    }


@router.get("/projects/{project_id}")
def get_project(
    project_id: str,
    db: Session = Depends(get_db)
):

    projeto = (
        db.query(models.Projeto)
        .filter(models.Projeto.id == project_id)
        .first()
    )

    if not projeto:
        raise HTTPException(
            status_code=404,
            detail="Projeto não encontrado"
        )

    etapas = (
        db.query(models.ProjetoEtapa)
        .filter(
            models.ProjetoEtapa.projeto_id == projeto.id
        )
        .order_by(
            models.ProjetoEtapa.ordem.asc()
        )
        .all()
    )

    imagem = None

    if projeto.imagem:

        imagem = (
            "data:image/png;base64,"
            + base64.b64encode(
                projeto.imagem
            ).decode("utf-8")
        )

    return {

        "id": projeto.id,

        "nome": projeto.nome,

        "categoria": projeto.categoria,

        "status": projeto.status,

        "proprietario":
            projeto.proprietario,

        "proprietario_email":
            projeto.proprietario_email,

        "proprietario_telefone":
            projeto.proprietario_telefone,

        "cep":
            projeto.cep,

        "endereco":
            projeto.endereco,

        "numero":
            projeto.numero,

        "bairro":
            projeto.bairro,

        "cidade":
            projeto.cidade,

        "estado":
            projeto.estado,

        "descricao":
            projeto.descricao,

        "m2":
            projeto.area_construida,

        "quantidade_unidades":
            projeto.quantidade_unidades,

        "imagem":
            imagem,

        "etapas": [

            {

                "id": (
                    str(item.etapa.id)
                    if item.etapa
                    else None
                ),

                "nome": (
                    item.etapa.nome
                    if item.etapa
                    else item.nome_customizado
                ),

                "customizada": (
                    item.etapa is None
                ),

                "ordem":
                    item.ordem,

                "concluida":
                    item.concluida
            }

            for item in etapas
        ]
    }


@router.get("/projects/{project_id}/stages/totals")
def get_project_stage_totals(
    project_id: str,
    db: Session = Depends(get_db)
):

    projeto = (
        db.query(models.Projeto)
        .filter(models.Projeto.id == project_id)
        .first()
    )

    if not projeto:
        raise HTTPException(
            status_code=404,
            detail="Projeto nao encontrado"
        )

    etapas = (
        db.query(models.ProjetoEtapa)
        .filter(models.ProjetoEtapa.projeto_id == project_id)
        .order_by(models.ProjetoEtapa.ordem.asc())
        .all()
    )

    return [
        _build_stage_totals(db, project_id, item)
        for item in etapas
    ]


@router.get("/projects/{project_id}/stages/{project_stage_id}/totals")
def get_project_stage_total(
    project_id: str,
    project_stage_id: str,
    db: Session = Depends(get_db)
):

    projeto = (
        db.query(models.Projeto)
        .filter(models.Projeto.id == project_id)
        .first()
    )

    if not projeto:
        raise HTTPException(
            status_code=404,
            detail="Projeto nao encontrado"
        )

    projeto_etapa = (
        db.query(models.ProjetoEtapa)
        .filter(
            models.ProjetoEtapa.id == project_stage_id,
            models.ProjetoEtapa.projeto_id == project_id
        )
        .first()
    )

    if not projeto_etapa:
        raise HTTPException(
            status_code=404,
            detail="Etapa do projeto nao encontrada"
        )

    return _build_stage_totals(
        db,
        project_id,
        projeto_etapa
    )