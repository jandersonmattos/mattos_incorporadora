from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from database import SessionLocal
import models
from datetime import datetime
import base64

router = APIRouter()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/projects/{project_id}/stages")
def get_project_stages(
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
            models.ProjetoEtapa.projeto_id == project_id
        )
        .order_by(
            models.ProjetoEtapa.ordem.asc()
        )
        .all()
    )

    result = []

    for item in etapas:

        total_previsto = 0.0
        total_pago = 0.0

        if item.etapa_id:
            total_previsto, total_pago = (
                db.query(
                    func.coalesce(func.sum(models.Custo.valor_previsto), 0.0),
                    func.coalesce(func.sum(models.Custo.valor_pago), 0.0)
                )
                .filter(
                    models.Custo.projeto_id == project_id,
                    models.Custo.etapa_id == item.etapa_id
                )
                .first()
            )

        total_previsto = round(float(total_previsto or 0), 2)
        total_pago = round(float(total_pago or 0), 2)
        total_a_pagar = round(total_previsto - total_pago, 2)

        # =====================================
        # ETAPA PADRÃO
        # =====================================

        if item.etapa:

            result.append({

                "id":
                    str(item.id),

                "etapaid":
                    str(item.etapa.id),

                "name":
                    item.etapa.nome,

                "customizada":
                    False,

                "ordem":
                    item.ordem,

                "concluida":
                    item.concluida,

                "data_inicio_prevista":
                    item.data_inicio_prevista,

                "data_fim_prevista":
                    item.data_fim_prevista,

                "data_inicio_real":
                    item.data_inicio_real,

                "data_fim_real":
                    item.data_fim_real,

                "total_etapa":
                    total_previsto,

                "total_pago":
                    total_pago,

                "total_a_pagar":
                    total_a_pagar
            })

        # =====================================
        # ETAPA CUSTOMIZADA
        # =====================================

        else:

            result.append({

                "id":
                    str(item.id),

                "name":
                    item.nome_customizado,

                "customizada":
                    True,

                "ordem":
                    item.ordem,

                "concluida":
                    item.concluida,

                "data_inicio_prevista":
                    item.data_inicio_prevista,

                "data_fim_prevista":
                    item.data_fim_prevista,

                "data_inicio_real":
                    item.data_inicio_real,

                "data_fim_real":
                    item.data_fim_real,

                "total_etapa":
                    total_previsto,

                "total_pago":
                    total_pago,

                "total_a_pagar":
                    total_a_pagar
            })

    return result


@router.put("/projects/{project_id}")
def update_project(
    project_id: str,
    data: dict,
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

    data_inicio = None
    data_fim = None

    if data.get("data_inicio"):
        data_inicio = datetime.strptime(
            data.get("data_inicio"),
            "%Y-%m-%d"
        ).date()

    if data.get("data_fim"):
        data_fim = datetime.strptime(
            data.get("data_fim"),
            "%Y-%m-%d"
        ).date()

    projeto.nome = data.get("nome")
    projeto.categoria = data.get("categoria")
    projeto.status = data.get("status")
    projeto.data_inicio = data_inicio
    projeto.data_fim = data_fim
    projeto.proprietario = data.get("proprietario")
    projeto.proprietario_email = data.get("proprietario_email")
    projeto.proprietario_telefone = data.get("proprietario_telefone")
    projeto.area_construida = data.get("area_construida")
    projeto.quantidade_unidades=data.get("quantidade_unidades")
    projeto.cep = data.get("cep")
    projeto.endereco = data.get("endereco")
    projeto.numero = data.get("numero")
    projeto.bairro = data.get("bairro")
    projeto.cidade = data.get("cidade")
    projeto.estado = data.get("estado")
    projeto.descricao = data.get("descricao")

    imagem_base64 = data.get("imagem")

    if imagem_base64:

        if "," in imagem_base64:
            imagem_base64 = imagem_base64.split(",")[1]

        projeto.imagem = base64.b64decode(imagem_base64)

    else:
        projeto.imagem = None

    db.query(models.ProjetoEtapa).filter(
        models.ProjetoEtapa.projeto_id == projeto.id
    ).delete()

    etapas = data.get("etapas", [])

    for index, etapa_id in enumerate(etapas):

        relacao = models.ProjetoEtapa(
            projeto_id=projeto.id,
            etapa_id=etapa_id,
            ordem=index + 1
        )

        db.add(relacao)

    db.commit()

    return {
        "message": "Obra atualizada com sucesso"
    }


@router.put("/projects/{project_id}/stages")
def update_project_stages(
    project_id: str,
    data: dict,
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

    # =========================================
    # REMOVE ETAPAS ANTIGAS
    # =========================================

    db.query(models.ProjetoEtapa).filter(
        models.ProjetoEtapa.projeto_id == project_id
    ).delete()

    ordem = 1

    # =========================================
    # ETAPAS PADRÃO
    # =========================================

    etapas = data.get("etapas", [])

    for etapa_id in etapas:

        etapa = (
            db.query(models.EtapaObra)
            .filter(
                models.EtapaObra.id == etapa_id
            )
            .first()
        )

        if not etapa:
            continue

        nova_etapa = models.ProjetoEtapa(
            projeto_id=project_id,
            etapa_id=etapa_id,
            nome_customizado=None,
            ordem=ordem,
            concluida=False
        )

        db.add(nova_etapa)

        ordem += 1

    # =========================================
    # ETAPAS CUSTOMIZADAS
    # =========================================

    etapas_customizadas = data.get(
        "etapas_customizadas_detalhes",
        []
    )

    for item in etapas_customizadas:

        nome = item.get("name")

        if not nome:
            continue

        nova_etapa = models.ProjetoEtapa(
            projeto_id=project_id,
            etapa_id=None,
            nome_customizado=nome,
            ordem=ordem,
            concluida=False
        )

        db.add(nova_etapa)

        ordem += 1

    db.commit()

    return {
        "message": "Etapas atualizadas com sucesso"
    }


@router.put("/project-stages/{project_stage_id}")
def update_project_stage(
    project_stage_id: str,
    data: dict,
    db: Session = Depends(get_db)
):

    projeto_etapa = (
        db.query(models.ProjetoEtapa)
        .filter(models.ProjetoEtapa.id == project_stage_id)
        .first()
    )

    if not projeto_etapa:
        raise HTTPException(
            status_code=404,
            detail="Etapa do projeto nao encontrada"
        )

    if "etapa_id" in data:

        etapa_id = data.get("etapa_id")

        if etapa_id:
            etapa = (
                db.query(models.EtapaObra)
                .filter(models.EtapaObra.id == etapa_id)
                .first()
            )

            if not etapa:
                raise HTTPException(
                    status_code=404,
                    detail="Etapa nao encontrada"
                )

        projeto_etapa.etapa_id = etapa_id

    if "nome_customizado" in data:
        projeto_etapa.nome_customizado = data.get("nome_customizado")

    if "ordem" in data:
        projeto_etapa.ordem = data.get("ordem")

    if "concluida" in data:
        projeto_etapa.concluida = data.get("concluida")

    if "data_inicio_prevista" in data:
        if data.get("data_inicio_prevista"):
            try:
                projeto_etapa.data_inicio_prevista = datetime.strptime(
                    data.get("data_inicio_prevista"),
                    "%Y-%m-%d"
                ).date()
            except ValueError:
                raise HTTPException(
                    status_code=400,
                    detail="data_inicio_prevista invalida. Use o formato YYYY-MM-DD"
                )
        else:
            projeto_etapa.data_inicio_prevista = None

    if "data_fim_prevista" in data:
        if data.get("data_fim_prevista"):
            try:
                projeto_etapa.data_fim_prevista = datetime.strptime(
                    data.get("data_fim_prevista"),
                    "%Y-%m-%d"
                ).date()
            except ValueError:
                raise HTTPException(
                    status_code=400,
                    detail="data_fim_prevista invalida. Use o formato YYYY-MM-DD"
                )
        else:
            projeto_etapa.data_fim_prevista = None

    if "data_inicio_real" in data:
        if data.get("data_inicio_real"):
            try:
                projeto_etapa.data_inicio_real = datetime.strptime(
                    data.get("data_inicio_real"),
                    "%Y-%m-%d"
                ).date()
            except ValueError:
                raise HTTPException(
                    status_code=400,
                    detail="data_inicio_real invalida. Use o formato YYYY-MM-DD"
                )
        else:
            projeto_etapa.data_inicio_real = None

    if "data_fim_real" in data:
        if data.get("data_fim_real"):
            try:
                projeto_etapa.data_fim_real = datetime.strptime(
                    data.get("data_fim_real"),
                    "%Y-%m-%d"
                ).date()
            except ValueError:
                raise HTTPException(
                    status_code=400,
                    detail="data_fim_real invalida. Use o formato YYYY-MM-DD"
                )
        else:
            projeto_etapa.data_fim_real = None

    db.commit()

    return {
        "message": "Etapa atualizada com sucesso",
        "id": projeto_etapa.id
    }