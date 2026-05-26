from datetime import datetime

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


@router.post("/projects/{project_id}/costs")
def create_cost(project_id: str, data: dict, db: Session = Depends(get_db)):
    projeto = (
        db.query(models.Projeto)
        .filter(models.Projeto.id == project_id)
        .first()
    )

    if not projeto:
        raise HTTPException(status_code=404, detail="Projeto nao encontrado")

    data_custo = None
    if data.get("data"):
        try:
            data_custo = datetime.strptime(data.get("data"), "%Y-%m-%d").date()
        except ValueError:
            raise HTTPException(status_code=400, detail="Data invalida. Use o formato YYYY-MM-DD")

    categoria_id = data.get("categoria_id")
    if categoria_id:
        categoria = (
            db.query(models.Categoria)
            .filter(models.Categoria.id == categoria_id)
            .first()
        )
        if not categoria:
            raise HTTPException(status_code=404, detail="Categoria nao encontrada")

    etapa_id = data.get("etapa_id")
    if etapa_id:
        etapa = (
            db.query(models.EtapaObra)
            .filter(models.EtapaObra.id == etapa_id)
            .first()
        )
        if not etapa:
            raise HTTPException(status_code=404, detail="Etapa nao encontrada")

    item_id = data.get("item_id")
    if item_id:
        item = (
            db.query(models.ItemEtapa)
            .filter(models.ItemEtapa.id == item_id)
            .first()
        )
        if not item:
            raise HTTPException(status_code=404, detail="Item nao encontrado")
        # herda etapa_id do item se nao informado
        if not etapa_id:
            etapa_id = item.etapa_id

    custo = models.Custo(
        descricao=data.get("descricao"),
        quantidade=data.get("quantidade", 1),
        valor_unitario=data.get("valor_unitario", 0),
        valor_previsto=data.get("valor_previsto", 0),
        valor_pago=data.get("valor_pago", 0),
        data=data_custo,
        projeto_id=project_id,
        categoria_id=categoria_id,
        recurso_nome=data.get("recurso_nome"),
        recurso_id=data.get("recurso_id"),
        etapa_id=etapa_id,
        item_id=item_id,
    )

    db.add(custo)
    db.commit()
    db.refresh(custo)

    return {
        "message": "Custo salvo com sucesso",
        "id": str(custo.id),
    }


@router.put("/costs/{cost_id}")
def update_cost(cost_id: str, data: dict, db: Session = Depends(get_db)):
    custo = (
        db.query(models.Custo)
        .filter(models.Custo.id == cost_id)
        .first()
    )

    if not custo:
        raise HTTPException(status_code=404, detail="Custo nao encontrado")

    if "data" in data:
        if data.get("data"):
            try:
                custo.data = datetime.strptime(data.get("data"), "%Y-%m-%d").date()
            except ValueError:
                raise HTTPException(status_code=400, detail="Data invalida. Use o formato YYYY-MM-DD")
        else:
            custo.data = None

    if "categoria_id" in data:
        categoria_id = data.get("categoria_id")
        if categoria_id:
            categoria = (
                db.query(models.Categoria)
                .filter(models.Categoria.id == categoria_id)
                .first()
            )
            if not categoria:
                raise HTTPException(status_code=404, detail="Categoria nao encontrada")
        custo.categoria_id = categoria_id

    if "etapa_id" in data:
        etapa_id = data.get("etapa_id")
        if etapa_id:
            etapa = (
                db.query(models.EtapaObra)
                .filter(models.EtapaObra.id == etapa_id)
                .first()
            )
            if not etapa:
                raise HTTPException(status_code=404, detail="Etapa nao encontrada")
        custo.etapa_id = etapa_id

    if "descricao" in data:
        custo.descricao = data.get("descricao")

    if "quantidade" in data:
        custo.quantidade = data.get("quantidade")

    if "valor_unitario" in data:
        custo.valor_unitario = data.get("valor_unitario")

    if "valor_previsto" in data:
        custo.valor_previsto = data.get("valor_previsto")

    if "valor_pago" in data:
        custo.valor_pago = data.get("valor_pago")

    if "recurso_nome" in data:
        custo.recurso_nome = data.get("recurso_nome")

    if "recurso_id" in data:
        custo.recurso_id = data.get("recurso_id")

    if "item_id" in data:
        item_id = data.get("item_id")
        if item_id:
            item = (
                db.query(models.ItemEtapa)
                .filter(models.ItemEtapa.id == item_id)
                .first()
            )
            if not item:
                raise HTTPException(status_code=404, detail="Item nao encontrado")
        custo.item_id = item_id

    db.commit()

    return {
        "message": "Custo atualizado com sucesso",
        "id": str(custo.id),
    }
