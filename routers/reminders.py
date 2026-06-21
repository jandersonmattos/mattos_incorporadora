import os
from datetime import datetime, date
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import SessionLocal
from email_service import enviar_email_lembrete
import models

router = APIRouter()

EMAILS_FIXOS_LEMBRETE = [
    email.strip().lower()
    for email in os.getenv(
        "REMINDER_FIXED_RECIPIENTS",
        "mattosincorporadoraltda@gmail.com,janderson.candido@gmail.com"
    ).split(",")
    if email.strip()
]

DIAS_SEMANA_VALIDOS = {
    "segunda",
    "terca",
    "quarta",
    "quinta",
    "sexta"
}


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def _parse_data(data_str: str, campo: str):
    try:
        return datetime.strptime(data_str, "%Y-%m-%d").date()
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail=f"Campo '{campo}' deve estar no formato YYYY-MM-DD"
        )


def _normalizar_dia_semana(valor: str):
    valor = (valor or "").strip().lower()
    return valor.replace("ç", "c")


def _validar_payload(data: dict):
    descricao = (data.get("descricao") or "").strip()
    recorrente = bool(data.get("recorrente", False))
    tipo_recorrencia = (data.get("tipo_recorrencia") or "").strip().lower()
    dia_semana = _normalizar_dia_semana(data.get("dia_semana"))
    dia_mes = data.get("dia_mes")
    data_especifica_str = data.get("data_especifica")

    if not descricao:
        raise HTTPException(
            status_code=400,
            detail="Descricao do lembrete e obrigatoria"
        )

    data_especifica = None

    if not recorrente:
        if not data_especifica_str:
            raise HTTPException(
                status_code=400,
                detail="Para lembrete nao recorrente, informe 'data_especifica'"
            )
        data_especifica = _parse_data(data_especifica_str, "data_especifica")

    else:
        if tipo_recorrencia not in {"semanal", "mensal"}:
            raise HTTPException(
                status_code=400,
                detail="Para lembrete recorrente, 'tipo_recorrencia' deve ser 'semanal' ou 'mensal'"
            )

        if tipo_recorrencia == "semanal":
            if dia_semana not in DIAS_SEMANA_VALIDOS:
                raise HTTPException(
                    status_code=400,
                    detail="Para recorrencia semanal, informe 'dia_semana' entre segunda e sexta"
                )
            dia_mes = None
            data_especifica = None

        if tipo_recorrencia == "mensal":
            if dia_mes is None:
                raise HTTPException(
                    status_code=400,
                    detail="Para recorrencia mensal, informe 'dia_mes'"
                )
            if not isinstance(dia_mes, int) or dia_mes < 1 or dia_mes > 31:
                raise HTTPException(
                    status_code=400,
                    detail="'dia_mes' deve ser um numero inteiro entre 1 e 31"
                )
            dia_semana = None
            data_especifica = None

    if not recorrente:
        tipo_recorrencia = None
        dia_semana = None
        dia_mes = None

    return {
        "descricao": descricao,
        "recorrente": recorrente,
        "tipo_recorrencia": tipo_recorrencia,
        "dia_semana": dia_semana,
        "dia_mes": dia_mes,
        "data_especifica": data_especifica,
        "ativo": bool(data.get("ativo", True))
    }


def _serialize_reminder(lembrete: models.LembreteProjeto):
    return {
        "id": lembrete.id,
        "projeto_id": lembrete.projeto_id,
        "descricao": lembrete.descricao,
        "recorrente": lembrete.recorrente,
        "tipo_recorrencia": lembrete.tipo_recorrencia,
        "dia_semana": lembrete.dia_semana,
        "dia_mes": lembrete.dia_mes,
        "data_especifica": (
            lembrete.data_especifica.isoformat()
            if lembrete.data_especifica
            else None
        ),
        "ativo": lembrete.ativo,
        "ultimo_envio_em": (
            lembrete.ultimo_envio_em.isoformat()
            if lembrete.ultimo_envio_em
            else None
        ),
        "created_at": (
            lembrete.created_at.isoformat()
            if lembrete.created_at
            else None
        ),
        "updated_at": (
            lembrete.updated_at.isoformat()
            if lembrete.updated_at
            else None
        )
    }


def _dia_semana_hoje(referencia: date):
    dias = ["segunda", "terca", "quarta", "quinta", "sexta", "sabado", "domingo"]
    return dias[referencia.weekday()]


def _deve_enviar_hoje(lembrete: models.LembreteProjeto, referencia: date):
    if lembrete.ultimo_envio_em == referencia:
        return False

    if not lembrete.recorrente:
        return lembrete.data_especifica == referencia

    if lembrete.tipo_recorrencia == "semanal":
        return lembrete.dia_semana == _dia_semana_hoje(referencia)

    if lembrete.tipo_recorrencia == "mensal":
        return lembrete.dia_mes == referencia.day

    return False


def _normalizar_emails(email_ou_lista):
    if not email_ou_lista:
        return []

    if isinstance(email_ou_lista, str):
        candidatos = [email_ou_lista]
    elif isinstance(email_ou_lista, list):
        candidatos = email_ou_lista
    else:
        return []

    return [
        email.strip().lower()
        for email in candidatos
        if isinstance(email, str) and email.strip()
    ]


def _destinatarios_lembrete(
    email_projeto: str = None,
    email_destino: str = None,
    email_destinos: list = None
):
    destinatarios = []

    for email in _normalizar_emails(email_destino):
        if email not in destinatarios:
            destinatarios.append(email)

    for email in _normalizar_emails(email_destinos):
        if email not in destinatarios:
            destinatarios.append(email)

    for email in _normalizar_emails(email_projeto):
        if email not in destinatarios:
            destinatarios.append(email)

    for email in EMAILS_FIXOS_LEMBRETE:
        if email not in destinatarios:
            destinatarios.append(email)

    return destinatarios


def _processar_lembretes_do_dia(db: Session, data_referencia: date):
    lembretes = (
        db.query(models.LembreteProjeto)
        .join(models.Projeto)
        .filter(models.LembreteProjeto.ativo == True)
        .all()
    )

    emails_enviados = 0
    lembretes_enviados = 0
    ignorados_sem_destinatario = 0

    for lembrete in lembretes:
        if not _deve_enviar_hoje(lembrete, data_referencia):
            continue

        destinatarios = _destinatarios_lembrete(
            email_projeto=lembrete.projeto.proprietario_email
        )

        if not destinatarios:
            ignorados_sem_destinatario += 1
            continue

        for destinatario in destinatarios:
            enviar_email_lembrete(
                email_destino=destinatario,
                nome_projeto=lembrete.projeto.nome,
                descricao=lembrete.descricao,
                data_referencia=data_referencia,
                recorrente=lembrete.recorrente,
                tipo_recorrencia=lembrete.tipo_recorrencia
            )
            emails_enviados += 1

        lembrete.ultimo_envio_em = data_referencia
        lembretes_enviados += 1

    db.commit()

    return {
        "data_referencia": data_referencia.isoformat(),
        "emails_enviados": emails_enviados,
        "lembretes_enviados": lembretes_enviados,
        "ignorados_sem_destinatario": ignorados_sem_destinatario
    }


@router.post("/projects/{project_id}/reminders")
def create_project_reminder(
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
            detail="Projeto nao encontrado"
        )

    payload = _validar_payload(data)

    lembrete = models.LembreteProjeto(
        projeto_id=project_id,
        descricao=payload["descricao"],
        recorrente=payload["recorrente"],
        tipo_recorrencia=payload["tipo_recorrencia"],
        dia_semana=payload["dia_semana"],
        dia_mes=payload["dia_mes"],
        data_especifica=payload["data_especifica"],
        ativo=payload["ativo"]
    )

    db.add(lembrete)
    db.commit()
    db.refresh(lembrete)

    return {
        "message": "Lembrete criado com sucesso",
        "lembrete": _serialize_reminder(lembrete)
    }


@router.get("/projects/{project_id}/reminders")
def list_project_reminders(
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

    lembretes = (
        db.query(models.LembreteProjeto)
        .filter(models.LembreteProjeto.projeto_id == project_id)
        .order_by(models.LembreteProjeto.created_at.desc())
        .all()
    )

    return [
        _serialize_reminder(item)
        for item in lembretes
    ]


@router.put("/projects/{project_id}/reminders/{reminder_id}")
def update_project_reminder(
    project_id: str,
    reminder_id: str,
    data: dict,
    db: Session = Depends(get_db)
):
    lembrete = (
        db.query(models.LembreteProjeto)
        .filter(
            models.LembreteProjeto.id == reminder_id,
            models.LembreteProjeto.projeto_id == project_id
        )
        .first()
    )

    if not lembrete:
        raise HTTPException(
            status_code=404,
            detail="Lembrete nao encontrado"
        )

    payload = _validar_payload(data)

    lembrete.descricao = payload["descricao"]
    lembrete.recorrente = payload["recorrente"]
    lembrete.tipo_recorrencia = payload["tipo_recorrencia"]
    lembrete.dia_semana = payload["dia_semana"]
    lembrete.dia_mes = payload["dia_mes"]
    lembrete.data_especifica = payload["data_especifica"]
    lembrete.ativo = payload["ativo"]

    db.commit()
    db.refresh(lembrete)

    return {
        "message": "Lembrete atualizado com sucesso",
        "lembrete": _serialize_reminder(lembrete)
    }


@router.delete("/projects/{project_id}/reminders/{reminder_id}")
def delete_project_reminder(
    project_id: str,
    reminder_id: str,
    db: Session = Depends(get_db)
):
    lembrete = (
        db.query(models.LembreteProjeto)
        .filter(
            models.LembreteProjeto.id == reminder_id,
            models.LembreteProjeto.projeto_id == project_id
        )
        .first()
    )

    if not lembrete:
        raise HTTPException(
            status_code=404,
            detail="Lembrete nao encontrado"
        )

    db.delete(lembrete)
    db.commit()

    return {
        "message": "Lembrete removido com sucesso"
    }


@router.post("/projects/{project_id}/reminders/{reminder_id}/send")
def send_project_reminder(
    project_id: str,
    reminder_id: str,
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
            detail="Projeto nao encontrado"
        )

    lembrete = (
        db.query(models.LembreteProjeto)
        .filter(
            models.LembreteProjeto.id == reminder_id,
            models.LembreteProjeto.projeto_id == project_id
        )
        .first()
    )

    if not lembrete:
        raise HTTPException(
            status_code=404,
            detail="Lembrete nao encontrado"
        )

    destinatarios = _destinatarios_lembrete(
        email_projeto=projeto.proprietario_email,
        email_destino=data.get("email_destino"),
        email_destinos=data.get("email_destinos")
    )

    if not destinatarios:
        raise HTTPException(
            status_code=400,
            detail="Nenhum destinatario valido foi informado para envio"
        )

    data_referencia = date.today()

    for destinatario in destinatarios:
        enviar_email_lembrete(
            email_destino=destinatario,
            nome_projeto=projeto.nome,
            descricao=lembrete.descricao,
            data_referencia=data_referencia,
            recorrente=lembrete.recorrente,
            tipo_recorrencia=lembrete.tipo_recorrencia
        )

    lembrete.ultimo_envio_em = data_referencia
    db.commit()

    return {
        "message": "Email de lembrete enviado com sucesso",
        "destinatarios": destinatarios,
        "total_enviados": len(destinatarios)
    }


@router.post("/reminders/send-due")
def send_due_reminders(
    data: Optional[dict] = None,
    db: Session = Depends(get_db)
):
    data_referencia_str = (data or {}).get("data_referencia")
    data_referencia = date.today()

    if data_referencia_str:
        data_referencia = _parse_data(data_referencia_str, "data_referencia")

    resultado = _processar_lembretes_do_dia(
        db=db,
        data_referencia=data_referencia
    )

    return {
        "message": "Processamento de lembretes concluido",
        "data_referencia": resultado["data_referencia"],
        "emails_enviados": resultado["emails_enviados"],
        "lembretes_enviados": resultado["lembretes_enviados"],
        "ignorados_sem_destinatario": resultado["ignorados_sem_destinatario"],
        "emails_fixos": EMAILS_FIXOS_LEMBRETE
    }
