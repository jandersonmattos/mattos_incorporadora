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

    item = (
        db.query(models.ItemEtapa)
        .filter(models.ItemEtapa.id == item_id)
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


# =============================================
# DELETAR ITEM (e seus subitens em cascade)
# =============================================

@router.delete("/items/{item_id}")
def delete_stage_item(
    item_id: str,
    db: Session = Depends(get_db)
):

    item = (
        db.query(models.ItemEtapa)
        .filter(models.ItemEtapa.id == item_id)
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
        "id": item_id,
    }
