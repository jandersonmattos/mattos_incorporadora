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


@router.get("/suppliers")
def get_suppliers(
    db: Session = Depends(get_db)
):

    fornecedores = (
        db.query(models.Fornecedor)
        .all()
    )

    result = []

    for fornecedor in fornecedores:

        result.append({
            "id": fornecedor.id,
            "nome": fornecedor.nome,
            "razao_social": fornecedor.razao_social,
            "cpf_cnpj": fornecedor.cpf_cnpj,
            "email": fornecedor.email,
            "site": fornecedor.site,
            "responsavel": fornecedor.responsavel,
            "telefone": fornecedor.telefone,
            "celular": fornecedor.celular,
            "cep": fornecedor.cep,
            "endereco": fornecedor.endereco,
            "numero": fornecedor.numero,
            "bairro": fornecedor.bairro,
            "complemento": fornecedor.complemento,
            "estado": fornecedor.estado,
            "cidade": fornecedor.cidade,
            "observacoes": fornecedor.observacoes,
            "avaliacao": fornecedor.avaliacao,
            "banco": fornecedor.banco,
            "agencia": fornecedor.agencia,
            "numero_conta": fornecedor.numero_conta,
            "chave_pix": fornecedor.chave_pix,

            "tipos": [
                {
                    "id": tipo.id,
                    "nome": tipo.nome
                }
                for tipo in fornecedor.tipos
            ]
        })

    return result


@router.get("/suppliers/{supplier_id}")
def get_supplier(
    supplier_id: str,
    db: Session = Depends(get_db)
):

    fornecedor = (
        db.query(models.Fornecedor)
        .filter(
            models.Fornecedor.id == supplier_id
        )
        .first()
    )

    if not fornecedor:

        raise HTTPException(
            status_code=404,
            detail="Fornecedor não encontrado"
        )

    return {
        "id": fornecedor.id,
        "nome": fornecedor.nome,
        "razao_social": fornecedor.razao_social,
        "cpf_cnpj": fornecedor.cpf_cnpj,
        "email": fornecedor.email,
        "site": fornecedor.site,
        "responsavel": fornecedor.responsavel,
        "telefone": fornecedor.telefone,
        "celular": fornecedor.celular,
        "cep": fornecedor.cep,
        "endereco": fornecedor.endereco,
        "numero": fornecedor.numero,
        "bairro": fornecedor.bairro,
        "complemento": fornecedor.complemento,
        "estado": fornecedor.estado,
        "cidade": fornecedor.cidade,
        "observacoes": fornecedor.observacoes,
        "avaliacao": fornecedor.avaliacao,
        "banco": fornecedor.banco,
        "agencia": fornecedor.agencia,
        "numero_conta": fornecedor.numero_conta,
        "chave_pix": fornecedor.chave_pix,

        "tipos": [
            {
                "id": tipo.id,
                "nome": tipo.nome
            }
            for tipo in fornecedor.tipos
        ]
    }


@router.post("/suppliers")
def create_supplier(
    data: dict,
    db: Session = Depends(get_db)
):

    fornecedor = models.Fornecedor(
        nome=data.get("nome"),
        razao_social=data.get("razao_social"),
        cpf_cnpj=data.get("cpf_cnpj"),
        email=data.get("email"),
        site=data.get("site"),
        responsavel=data.get("responsavel"),
        telefone=data.get("telefone"),
        celular=data.get("celular"),
        cep=data.get("cep"),
        endereco=data.get("endereco"),
        numero=data.get("numero"),
        bairro=data.get("bairro"),
        complemento=data.get("complemento"),
        estado=data.get("estado"),
        cidade=data.get("cidade"),
        observacoes=data.get("observacoes"),
        avaliacao=data.get("avaliacao", 0),
        banco=data.get("banco"),
        agencia=data.get("agencia"),
        numero_conta=data.get("numero_conta"),
        chave_pix=data.get("chave_pix")
    )

    tipo_ids = data.get(
        "tipos",
        []
    )

    tipos = (
        db.query(models.TipoFornecedor)
        .filter(
            models.TipoFornecedor.id.in_(tipo_ids)
        )
        .all()
    )

    fornecedor.tipos = tipos

    db.add(fornecedor)

    db.commit()

    db.refresh(fornecedor)

    return {
        "message": "Fornecedor criado com sucesso",
        "id": fornecedor.id
    }


@router.put("/suppliers/{supplier_id}")
def update_supplier(
    supplier_id: str,
    data: dict,
    db: Session = Depends(get_db)
):

    fornecedor = (
        db.query(models.Fornecedor)
        .filter(
            models.Fornecedor.id == supplier_id
        )
        .first()
    )

    if not fornecedor:

        raise HTTPException(
            status_code=404,
            detail="Fornecedor não encontrado"
        )

    fornecedor.nome = data.get("nome")
    fornecedor.razao_social = data.get("razao_social")
    fornecedor.cpf_cnpj = data.get("cpf_cnpj")
    fornecedor.email = data.get("email")
    fornecedor.site = data.get("site")
    fornecedor.responsavel = data.get("responsavel")
    fornecedor.telefone = data.get("telefone")
    fornecedor.celular = data.get("celular")
    fornecedor.cep = data.get("cep")
    fornecedor.endereco = data.get("endereco")
    fornecedor.numero = data.get("numero")
    fornecedor.bairro = data.get("bairro")
    fornecedor.complemento = data.get("complemento")
    fornecedor.estado = data.get("estado")
    fornecedor.cidade = data.get("cidade")
    fornecedor.observacoes = data.get("observacoes")
    fornecedor.avaliacao = data.get("avaliacao", 0)
    fornecedor.banco = data.get("banco")
    fornecedor.agencia = data.get("agencia")
    fornecedor.numero_conta = data.get("numero_conta")
    fornecedor.chave_pix = data.get("chave_pix")

    tipo_ids = data.get(
        "tipos",
        []
    )

    tipos = (
        db.query(models.TipoFornecedor)
        .filter(
            models.TipoFornecedor.id.in_(tipo_ids)
        )
        .all()
    )

    fornecedor.tipos = tipos

    db.commit()

    db.refresh(fornecedor)

    return {
        "message": "Fornecedor atualizado com sucesso"
    }


@router.delete("/suppliers/{supplier_id}")
def delete_supplier(
    supplier_id: str,
    db: Session = Depends(get_db)
):

    fornecedor = (
        db.query(models.Fornecedor)
        .filter(
            models.Fornecedor.id == supplier_id
        )
        .first()
    )

    if not fornecedor:

        raise HTTPException(
            status_code=404,
            detail="Fornecedor não encontrado"
        )

    db.delete(fornecedor)

    db.commit()

    return {
        "message": "Fornecedor deletado com sucesso"
    }