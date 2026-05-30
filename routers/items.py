from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import SessionLocal
import models
import re
from uuid import UUID

router = APIRouter()

UUID_PATTERN = re.compile(
    r"[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}"
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def _parse_uuid(value: str, field_name: str) -> UUID:
    try:
        return UUID(str(value))
    except (ValueError, TypeError):
        matched = UUID_PATTERN.search(str(value or ""))
        if matched:
            return UUID(matched.group(0))
        raise HTTPException(
            status_code=400,
            detail=f"{field_name} invalido. Informe um UUID valido"
        )


# =============================================
# LISTAGEM DE ITENS DE UMA ETAPA DO PROJETO
# =============================================

@router.get("/projects/{project_id}/stages/{project_stage_id}/items")
def get_stage_items(
    project_id: str,
    project_stage_id: str,
    db: Session = Depends(get_db)
):

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

    itens = (
        db.query(models.ItemEtapa)
        .filter(
            models.ItemEtapa.projeto_id == project_id,
            models.ItemEtapa.etapa_id == projeto_etapa.etapa_id
        )
        .all()
    )

    result = []

    for item in itens:

        subitens_data = []
        total_item = 0.0

        for sub in item.subitens:

            total_sub = round(
                (sub.quantidade or 1) * (sub.valor_unitario or 0),
                2
            )
            total_item += total_sub

            subitens_data.append({
                "id": str(sub.id),
                "item_id": str(item.id),
                "item_nome": item.nome,
                "etapa_id": str(projeto_etapa.etapa_id) if projeto_etapa.etapa_id else None,
                "project_stage_id": str(projeto_etapa.id),
                "descricao": sub.descricao,
                "unidade": sub.recurso_nome,
                "quantidade": sub.quantidade,
                "valor_unitario": sub.valor_unitario,
                "total": total_sub,
                "valor_previsto": sub.valor_previsto,
                "valor_pago": sub.valor_pago,
                "data": str(sub.data) if sub.data else None,
            })

        result.append({
            "id": str(item.id),
            "nome": item.nome,
            "total": round(total_item, 2),
            "subitens": subitens_data,
        })

    return result


# =============================================
# CRIAR ITEM EM UMA ETAPA DO PROJETO
# =============================================

@router.post("/projects/{project_id}/stages/{project_stage_id}/items")
def create_stage_item(
    project_id: str,
    project_stage_id: str,
    data: dict,
    db: Session = Depends(get_db)
):

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

    nome = data.get("nome")

    if not nome:
        raise HTTPException(
            status_code=400,
            detail="Campo 'nome' e obrigatorio"
        )

    item = models.ItemEtapa(
        nome=nome,
        projeto_id=project_id,
        etapa_id=projeto_etapa.etapa_id,
    )

    db.add(item)
    db.commit()
    db.refresh(item)

    return {
        "message": "Item criado com sucesso",
        "id": str(item.id),
        "nome": item.nome,
    }


# =============================================
# ATUALIZAR ITEM
# =============================================

@router.put("/items/{item_id}")
def update_stage_item(
    item_id: str,
    data: dict,
    db: Session = Depends(get_db)
):
    parsed_item_id = _parse_uuid(item_id, "item_id")

    item = (
        db.query(models.ItemEtapa)
        .filter(models.ItemEtapa.id == parsed_item_id)
        .first()
    )

    if not item:
        raise HTTPException(
            status_code=404,
            detail="Item nao encontrado"
        )

    if "nome" in data:
        nome = data.get("nome")
        if not nome:
            raise HTTPException(
                status_code=400,
                detail="Campo 'nome' nao pode ser vazio"
            )
        item.nome = nome

    db.commit()

    return {
        "message": "Item atualizado com sucesso",
        "id": str(item.id),
    }


@router.patch("/items/{item_id}")
def patch_stage_item(
    item_id: str,
    data: dict,
    db: Session = Depends(get_db)
):
    return update_stage_item(item_id=item_id, data=data, db=db)


@router.put("/projects/{project_id}/stages/{project_stage_id}/items/{item_id}")
def update_stage_item_scoped(
    project_id: str,
    project_stage_id: str,
    item_id: str,
    data: dict,
    db: Session = Depends(get_db)
):
    parsed_item_id = _parse_uuid(item_id, "item_id")

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

    item = (
        db.query(models.ItemEtapa)
        .filter(
            models.ItemEtapa.id == parsed_item_id,
            models.ItemEtapa.projeto_id == project_id,
        )
        .first()
    )

    if not item:
        raise HTTPException(
            status_code=404,
            detail="Item nao encontrado"
        )

    if "nome" in data:
        nome = data.get("nome")
        if not nome:
            raise HTTPException(
                status_code=400,
                detail="Campo 'nome' nao pode ser vazio"
            )
        item.nome = nome

    db.commit()

    return {
        "message": "Item atualizado com sucesso",
        "id": str(item.id),
    }


@router.patch("/projects/{project_id}/stages/{project_stage_id}/items/{item_id}")
def patch_stage_item_scoped(
    project_id: str,
    project_stage_id: str,
    item_id: str,
    data: dict,
    db: Session = Depends(get_db)
):
    return update_stage_item_scoped(
        project_id=project_id,
        project_stage_id=project_stage_id,
        item_id=item_id,
        data=data,
        db=db
    )


# =============================================
# DELETAR ITEM (e seus subitens em cascade)
# =============================================

@router.delete("/items/{item_id}")
def delete_stage_item(
    item_id: str,
    db: Session = Depends(get_db)
):
    parsed_item_id = _parse_uuid(item_id, "item_id")

    item = (
        db.query(models.ItemEtapa)
        .filter(models.ItemEtapa.id == parsed_item_id)
        .first()
    )

    if not item:
        raise HTTPException(
            status_code=404,
            detail="Item nao encontrado"
        )

    db.delete(item)
    db.commit()

    return {
        "message": "Item deletado com sucesso",
        "id": str(item.id),
    }
