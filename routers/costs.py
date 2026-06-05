from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import re
from uuid import UUID

from database import SessionLocal
import models

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


def _normalize_lookup_name(value: str | None) -> str:
    return " ".join(str(value or "").strip().lower().split())


def _choose_item_label(custo: models.Custo) -> str | None:
    for raw in [custo.recurso_nome, custo.descricao]:
        label = str(raw or "").strip()
        if label:
            return label
    return None


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
        parsed_item_id = _parse_uuid(item_id, "item_id")
        item = (
            db.query(models.ItemEtapa)
            .filter(models.ItemEtapa.id == parsed_item_id)
            .first()
        )
        if not item:
            raise HTTPException(status_code=404, detail="Item nao encontrado")
        item_id = parsed_item_id
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


@router.get("/projects/{project_id}/stages/{project_stage_id}/costs")
def get_stage_costs(
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
        raise HTTPException(status_code=404, detail="Projeto nao encontrado")

    projeto_etapa = (
        db.query(models.ProjetoEtapa)
        .filter(
            models.ProjetoEtapa.id == project_stage_id,
            models.ProjetoEtapa.projeto_id == project_id
        )
        .first()
    )

    if not projeto_etapa:
        raise HTTPException(status_code=404, detail="Etapa do projeto nao encontrada")

    if not projeto_etapa.etapa_id:
        return []

    custos = (
        db.query(models.Custo)
        .filter(
            models.Custo.projeto_id == project_id,
            models.Custo.etapa_id == projeto_etapa.etapa_id
        )
        .order_by(models.Custo.data.desc(), models.Custo.id.desc())
        .all()
    )

    stage_items = (
        db.query(models.ItemEtapa)
        .filter(
            models.ItemEtapa.projeto_id == project_id,
            models.ItemEtapa.etapa_id == projeto_etapa.etapa_id
        )
        .all()
    )

    items_by_name = {}
    for stage_item in stage_items:
        key = _normalize_lookup_name(stage_item.nome)
        if key and key not in items_by_name:
            items_by_name[key] = stage_item

    mutated = False

    for custo in custos:
        if custo.item_id:
            continue

        matched_item = None
        source = None

        for raw_candidate in [custo.recurso_nome, custo.descricao]:
            key = _normalize_lookup_name(raw_candidate)
            if key and key in items_by_name:
                matched_item = items_by_name[key]
                source = "inferred_from_name"
                break

        if not matched_item:
            label = _choose_item_label(custo)
            key = _normalize_lookup_name(label)
            if key:
                matched_item = models.ItemEtapa(
                    nome=label,
                    projeto_id=project_id,
                    etapa_id=projeto_etapa.etapa_id,
                )
                db.add(matched_item)
                db.flush()
                items_by_name[key] = matched_item
                source = "auto_created_from_cost"

        if matched_item:
            custo.item_id = matched_item.id
            custo.item = matched_item
            setattr(custo, "_item_id_source_runtime", source)
            mutated = True

    if mutated:
        db.commit()

    response = []

    for custo in custos:
        resolved_item_id = str(custo.item_id) if custo.item_id else None
        resolved_item_nome = custo.item.nome if custo.item else None
        item_id_source = (
            getattr(custo, "_item_id_source_runtime", None)
            or ("explicit" if resolved_item_id else None)
        )

        response.append({
            "id": str(custo.id),
            "descricao": custo.descricao,
            "quantidade": custo.quantidade,
            "valor_unitario": custo.valor_unitario,
            "valor_previsto": custo.valor_previsto,
            "valor_pago": custo.valor_pago,
            "saldo_restante": custo.saldo_restante,
            "data": custo.data.isoformat() if custo.data else None,
            "projeto_id": custo.projeto_id,
            "etapa_id": str(custo.etapa_id) if custo.etapa_id else None,
            "categoria_id": str(custo.categoria_id) if custo.categoria_id else None,
            "categoria_nome": custo.categoria.nome if custo.categoria else None,
            "item_id": resolved_item_id,
            "item_nome": resolved_item_nome,
            "item_id_source": item_id_source,
            "recurso_id": str(custo.recurso_id) if custo.recurso_id else None,
            "recurso_nome": custo.recurso_nome,
        })

    return response


@router.get("/projects/{project_id}/costs/a-pagar")
def get_project_costs_a_pagar(project_id: str, db: Session = Depends(get_db)):
    projeto = (
        db.query(models.Projeto)
        .filter(models.Projeto.id == project_id)
        .first()
    )

    if not projeto:
        raise HTTPException(status_code=404, detail="Projeto nao encontrado")

    custos = (
        db.query(models.Custo)
        .filter(
            models.Custo.projeto_id == project_id,
            models.Custo.valor_previsto > models.Custo.valor_pago,
        )
        .order_by(models.Custo.etapa_id, models.Custo.data.desc(), models.Custo.id.desc())
        .all()
    )

    return [
        {
            "id": str(custo.id),
            "descricao": custo.descricao,
            "recurso_nome": custo.recurso_nome,
            "valor_previsto": custo.valor_previsto,
            "valor_pago": custo.valor_pago,
            "saldo_a_pagar": custo.saldo_restante,
            "data": custo.data.isoformat() if custo.data else None,
            "etapa_id": str(custo.etapa_id) if custo.etapa_id else None,
            "etapa_nome": custo.etapa.nome if custo.etapa else None,
        }
        for custo in custos
    ]


def _apply_cost_updates(custo: models.Custo, data: dict, db: Session):
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
        parsed_item_id = None
        if item_id:
            parsed_item_id = _parse_uuid(item_id, "item_id")
            item = (
                db.query(models.ItemEtapa)
                .filter(models.ItemEtapa.id == parsed_item_id)
                .first()
            )
            if not item:
                raise HTTPException(status_code=404, detail="Item nao encontrado")
        custo.item_id = parsed_item_id


@router.put("/costs/{cost_id}")
def update_cost(cost_id: str, data: dict, db: Session = Depends(get_db)):
    parsed_cost_id = _parse_uuid(cost_id, "cost_id")

    custo = (
        db.query(models.Custo)
        .filter(models.Custo.id == parsed_cost_id)
        .first()
    )

    if not custo:
        raise HTTPException(status_code=404, detail="Custo nao encontrado")

    _apply_cost_updates(custo, data, db)
    db.commit()

    return {
        "message": "Custo atualizado com sucesso",
        "id": str(custo.id),
    }


@router.patch("/costs/{cost_id}")
def patch_cost(cost_id: str, data: dict, db: Session = Depends(get_db)):
    return update_cost(cost_id=cost_id, data=data, db=db)


@router.put("/projects/{project_id}/costs/{cost_id}")
def update_project_cost(
    project_id: str,
    cost_id: str,
    data: dict,
    db: Session = Depends(get_db)
):
    parsed_cost_id = _parse_uuid(cost_id, "cost_id")

    custo = (
        db.query(models.Custo)
        .filter(
            models.Custo.id == parsed_cost_id,
            models.Custo.projeto_id == project_id
        )
        .first()
    )

    if not custo:
        raise HTTPException(status_code=404, detail="Custo nao encontrado")

    _apply_cost_updates(custo, data, db)
    db.commit()

    return {
        "message": "Custo atualizado com sucesso",
        "id": str(custo.id),
    }


@router.patch("/projects/{project_id}/costs/{cost_id}")
def patch_project_cost(
    project_id: str,
    cost_id: str,
    data: dict,
    db: Session = Depends(get_db)
):
    return update_project_cost(
        project_id=project_id,
        cost_id=cost_id,
        data=data,
        db=db
    )


@router.put("/projects/{project_id}/stages/{project_stage_id}/costs/{cost_id}")
def update_stage_cost(
    project_id: str,
    project_stage_id: str,
    cost_id: str,
    data: dict,
    db: Session = Depends(get_db)
):
    parsed_cost_id = _parse_uuid(cost_id, "cost_id")

    projeto_etapa = (
        db.query(models.ProjetoEtapa)
        .filter(
            models.ProjetoEtapa.id == project_stage_id,
            models.ProjetoEtapa.projeto_id == project_id
        )
        .first()
    )

    if not projeto_etapa:
        raise HTTPException(status_code=404, detail="Etapa do projeto nao encontrada")

    custo = (
        db.query(models.Custo)
        .filter(
            models.Custo.id == parsed_cost_id,
            models.Custo.projeto_id == project_id,
            models.Custo.etapa_id == projeto_etapa.etapa_id
        )
        .first()
    )

    if not custo:
        raise HTTPException(status_code=404, detail="Custo nao encontrado nessa etapa")

    _apply_cost_updates(custo, data, db)
    db.commit()

    return {
        "message": "Custo atualizado com sucesso",
        "id": str(custo.id),
    }


@router.patch("/projects/{project_id}/stages/{project_stage_id}/costs/{cost_id}")
def patch_stage_cost(
    project_id: str,
    project_stage_id: str,
    cost_id: str,
    data: dict,
    db: Session = Depends(get_db)
):
    return update_stage_cost(
        project_id=project_id,
        project_stage_id=project_stage_id,
        cost_id=cost_id,
        data=data,
        db=db
    )


@router.delete("/costs/{cost_id}")
def delete_cost(cost_id: str, db: Session = Depends(get_db)):
    parsed_cost_id = _parse_uuid(cost_id, "cost_id")

    custo = (
        db.query(models.Custo)
        .filter(models.Custo.id == parsed_cost_id)
        .first()
    )

    if not custo:
        raise HTTPException(status_code=404, detail="Custo nao encontrado")

    db.delete(custo)
    db.commit()

    return {
        "message": "Custo deletado com sucesso",
        "id": str(custo.id),
    }


@router.delete("/projects/{project_id}/costs/{cost_id}")
def delete_project_cost(
    project_id: str,
    cost_id: str,
    db: Session = Depends(get_db)
):
    parsed_cost_id = _parse_uuid(cost_id, "cost_id")

    custo = (
        db.query(models.Custo)
        .filter(
            models.Custo.id == parsed_cost_id,
            models.Custo.projeto_id == project_id
        )
        .first()
    )

    if not custo:
        raise HTTPException(status_code=404, detail="Custo nao encontrado")

    db.delete(custo)
    db.commit()

    return {
        "message": "Custo deletado com sucesso",
        "id": str(custo.id),
    }


@router.delete("/projects/{project_id}/stages/{project_stage_id}/costs/{cost_id}")
def delete_stage_cost(
    project_id: str,
    project_stage_id: str,
    cost_id: str,
    db: Session = Depends(get_db)
):
    parsed_cost_id = _parse_uuid(cost_id, "cost_id")

    projeto_etapa = (
        db.query(models.ProjetoEtapa)
        .filter(
            models.ProjetoEtapa.id == project_stage_id,
            models.ProjetoEtapa.projeto_id == project_id
        )
        .first()
    )

    if not projeto_etapa:
        raise HTTPException(status_code=404, detail="Etapa do projeto nao encontrada")

    custo = (
        db.query(models.Custo)
        .filter(
            models.Custo.id == parsed_cost_id,
            models.Custo.projeto_id == project_id,
            models.Custo.etapa_id == projeto_etapa.etapa_id
        )
        .first()
    )

    if not custo:
        raise HTTPException(status_code=404, detail="Custo nao encontrado nessa etapa")

    db.delete(custo)
    db.commit()

    return {
        "message": "Custo deletado com sucesso",
        "id": str(custo.id),
    }
