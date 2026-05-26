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

def calcular_percentual_bdi(grupos):
    totais = {}
    for grupo in grupos:
        codigo = grupo.get("codigo") or grupo.get("key")
        itens = grupo.get("itens", [])
        total = sum([
            float(item.get("percentual", item.get("valor", 0)) or 0) for item in itens
        ])
        totais[codigo] = total
    A = (totais.get("A", 0)) / 100
    B = (totais.get("B", 0)) / 100
    C = (totais.get("C", 0)) / 100
    D = (totais.get("D", 0)) / 100
    E = (totais.get("E", 0)) / 100
    F = (totais.get("F", 0)) / 100
    resultado = (((1 + A + B + C) * (1 + D) * (1 + E)) / (1 - F) - 1) * 100
    return round(resultado, 2)

@router.get("/bdis")
def get_bdis(db: Session = Depends(get_db)):
    bdis = db.query(models.BDI).order_by(models.BDI.nome.asc()).all()
    result = []
    for bdi in bdis:
        result.append({
            "id": str(bdi.id),
            "nome": bdi.nome,
            "formula": bdi.formula,
            "percentual_total": bdi.percentual_total,
            "ativo": bdi.ativo
        })
    return result

@router.get("/bdis/{bdi_id}")
def get_bdi(bdi_id: str, db: Session = Depends(get_db)):
    bdi = db.query(models.BDI).filter(models.BDI.id == bdi_id).first()
    if not bdi:
        raise HTTPException(status_code=404, detail="BDI não encontrado")
    return {
        "id": str(bdi.id),
        "nome": bdi.nome,
        "formula": bdi.formula,
        "percentual_total": bdi.percentual_total,
        "ativo": bdi.ativo,
        "grupos": [
            {
                "id": str(grupo.id),
                "codigo": grupo.codigo,
                "titulo": grupo.titulo,
                "ordem": grupo.ordem,
                "total_percentual": grupo.total_percentual,
                "itens": [
                    {
                        "id": str(item.id),
                        "descricao": item.descricao,
                        "percentual": item.percentual,
                        "ordem": item.ordem
                    } for item in grupo.itens
                ]
            } for grupo in bdi.grupos
        ]
    }

@router.post("/bdis")
def create_bdi(data: dict, db: Session = Depends(get_db)):
    try:
        grupos = data.get("grupos", [])
        percentual_total = calcular_percentual_bdi(grupos)
        bdi = models.BDI(
            nome=data.get("nome"),
            descricao=data.get("descricao"),
            formula=data.get("formula", "(((1+A+B+C)*(1+D)*(1+E)/(1-F))-1)"),
            percentual_total=percentual_total,
            ativo=data.get("ativo", True)
        )
        db.add(bdi)
        db.flush()
        for grupo_index, grupo_data in enumerate(grupos):
            itens = grupo_data.get("itens", [])
            total_percentual = sum([
                float(item.get("valor", item.get("percentual", 0)) or 0) for item in itens
            ])
            grupo = models.BDIGrupo(
                bdi_id=bdi.id,
                codigo=grupo_data.get("codigo") or grupo_data.get("key"),
                titulo=grupo_data.get("titulo"),
                ordem=grupo_data.get("ordem", grupo_index),
                total_percentual=round(total_percentual, 2)
            )
            db.add(grupo)
            db.flush()
            for item_index, item_data in enumerate(itens):
                item = models.BDIGrupoItem(
                    grupo_id=grupo.id,
                    descricao=item_data.get("descricao"),
                    percentual=float(item_data.get("percentual", item_data.get("valor", 0)) or 0),
                    ordem=item_data.get("ordem", item_index)
                )
                db.add(item)
        db.commit()
        db.refresh(bdi)
        return {"message": "BDI criado com sucesso", "id": str(bdi.id), "percentual_total": bdi.percentual_total}
    except Exception as e:
        db.rollback()
        print(e)
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/bdis/{bdi_id}")
def update_bdi(bdi_id: str, data: dict, db: Session = Depends(get_db)):
    try:
        bdi = db.query(models.BDI).filter(models.BDI.id == bdi_id).first()
        if not bdi:
            raise HTTPException(status_code=404, detail="BDI não encontrado")
        grupos = data.get("grupos", [])
        percentual_total = calcular_percentual_bdi(grupos)
        bdi.nome = data.get("nome")
        bdi.descricao = data.get("descricao")
        bdi.formula = data.get("formula", "(((1+A+B+C)*(1+D)*(1+E)/(1-F))-1)")
        bdi.percentual_total = percentual_total
        bdi.ativo = data.get("ativo", True)
        db.query(models.BDIGrupo).filter(models.BDIGrupo.bdi_id == bdi.id).delete()
        db.flush()
        for grupo_index, grupo_data in enumerate(grupos):
            itens = grupo_data.get("itens", [])
            total_percentual = sum([
                float(item.get("valor", item.get("percentual", 0)) or 0) for item in itens
            ])
            grupo = models.BDIGrupo(
                bdi_id=bdi.id,
                codigo=grupo_data.get("codigo") or grupo_data.get("key"),
                titulo=grupo_data.get("titulo"),
                ordem=grupo_data.get("ordem", grupo_index),
                total_percentual=round(total_percentual, 2)
            )
            db.add(grupo)
            db.flush()
            for item_index, item_data in enumerate(itens):
                item = models.BDIGrupoItem(
                    grupo_id=grupo.id,
                    descricao=item_data.get("descricao"),
                    percentual=float(item_data.get("percentual", item_data.get("valor", 0)) or 0),
                    ordem=item_data.get("ordem", item_index)
                )
                db.add(item)
        db.commit()
        db.refresh(bdi)
        return {"message": "BDI atualizado com sucesso", "percentual_total": bdi.percentual_total}
    except Exception as e:
        db.rollback()
        print(e)
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/bdis/{bdi_id}")
def delete_bdi(bdi_id: str, db: Session = Depends(get_db)):
    bdi = db.query(models.BDI).filter(models.BDI.id == bdi_id).first()
    if not bdi:
        raise HTTPException(status_code=404, detail="BDI não encontrado")
    db.delete(bdi)
    db.commit()
    return {"message": "BDI deletado com sucesso"}
