import os
from datetime import date

from brevo import Brevo
from brevo.transactional_emails import (
    SendTransacEmailRequestSender,
    SendTransacEmailRequestToItem,
)


BREVO_API_KEY = os.getenv("BREVO_API_KEY", "")
EMAIL_REMETENTE = os.getenv("EMAIL_REMETENTE", "")
EMAIL_REMETENTE_NOME = os.getenv("EMAIL_REMETENTE_NOME", "Canteiro de Obras")


def _enviar_email_brevo(
    email_destino: str,
    assunto: str,
    html_content: str
):
    if not BREVO_API_KEY:
        raise ValueError("BREVO_API_KEY nao configurada.")

    if not EMAIL_REMETENTE:
        raise ValueError("EMAIL_REMETENTE nao configurado.")

    client = Brevo(api_key=BREVO_API_KEY)

    client.transactional_emails.send_transac_email(
        subject=assunto,
        html_content=html_content,
        sender=SendTransacEmailRequestSender(
            name=EMAIL_REMETENTE_NOME,
            email=EMAIL_REMETENTE,
        ),
        to=[
            SendTransacEmailRequestToItem(
                email=email_destino,
            )
        ],
    )


def enviar_codigo_recuperacao(
    email_destino: str,
    codigo: str
):

    assunto = "Recuperacao de senha"

    corpo_texto = f"""
    Recuperação de senha

    Seu código de recuperação é:

    {codigo}

    Esse código expira em 10 minutos.

    Caso você não tenha solicitado a recuperação,
    ignore este e-mail.
    """

    corpo_html = f"""
    <!DOCTYPE html>
    <html lang="pt-BR">

    <head>
        <meta charset="UTF-8" />
    </head>

    <body
        style="
            margin: 0;
            padding: 0;
            background-color: #0f172a;
            font-family: Arial, Helvetica, sans-serif;
        "
    >

        <table
            width="100%"
            cellpadding="0"
            cellspacing="0"
            style="
                padding: 40px 20px;
                background-color: #0f172a;
            "
        >
            <tr>
                <td align="center">

                    <table
                        width="100%"
                        cellpadding="0"
                        cellspacing="0"
                        style="
                            max-width: 600px;
                            background-color: #111827;
                            border-radius: 24px;
                            overflow: hidden;
                            border: 1px solid rgba(255,255,255,0.08);
                        "
                    >

                        <!-- HEADER -->
                        <tr>
                            <td
                                align="center"
                                style="
                                    background: linear-gradient(135deg, #10b981, #059669);
                                    padding: 40px 20px;
                                "
                            >

                                <h1
                                    style="
                                        color: white;
                                        margin: 0;
                                        font-size: 32px;
                                        letter-spacing: 1px;
                                    "
                                >
                                    Canteiro de Obras
                                </h1>

                                <p
                                    style="
                                        color: rgba(255,255,255,0.9);
                                        margin-top: 10px;
                                        font-size: 15px;
                                    "
                                >
                                    Plataforma de gestão para incorporadoras
                                </p>

                            </td>
                        </tr>

                        <!-- CONTENT -->
                        <tr>
                            <td
                                style="
                                    padding: 50px 40px;
                                    color: #e5e7eb;
                                "
                            >

                                <h2
                                    style="
                                        margin-top: 0;
                                        font-size: 28px;
                                        color: white;
                                    "
                                >
                                    Recuperação de senha
                                </h2>

                                <p
                                    style="
                                        font-size: 16px;
                                        line-height: 28px;
                                        color: #d1d5db;
                                    "
                                >
                                    Recebemos uma solicitação para redefinir sua senha.
                                </p>

                                <p
                                    style="
                                        font-size: 16px;
                                        line-height: 28px;
                                        color: #d1d5db;
                                    "
                                >
                                    Utilize o código abaixo para continuar:
                                </p>

                                <!-- CODIGO -->
                                <div
                                    style="
                                        margin: 40px 0;
                                        text-align: center;
                                    "
                                >

                                    <div
                                        style="
                                            display: inline-block;
                                            background-color: #0f172a;
                                            border: 2px dashed #10b981;
                                            border-radius: 20px;
                                            padding: 22px 40px;
                                        "
                                    >

                                        <span
                                            style="
                                                font-size: 42px;
                                                font-weight: bold;
                                                color: #10b981;
                                                letter-spacing: 10px;
                                            "
                                        >
                                            {codigo}
                                        </span>

                                    </div>

                                </div>

                                <p
                                    style="
                                        font-size: 15px;
                                        line-height: 26px;
                                        color: #9ca3af;
                                    "
                                >
                                    Este código expira em
                                    <strong style="color: #ffffff;">
                                        10 minutos
                                    </strong>.
                                </p>

                                <p
                                    style="
                                        font-size: 15px;
                                        line-height: 26px;
                                        color: #9ca3af;
                                        margin-top: 30px;
                                    "
                                >
                                    Se você não solicitou a redefinição da senha,
                                    apenas ignore este e-mail.
                                </p>

                            </td>
                        </tr>

                        <!-- FOOTER -->
                        <tr>
                            <td
                                align="center"
                                style="
                                    padding: 30px;
                                    border-top: 1px solid rgba(255,255,255,0.06);
                                    background-color: #0b1220;
                                "
                            >

                                <p
                                    style="
                                        margin: 0;
                                        color: #6b7280;
                                        font-size: 13px;
                                        line-height: 24px;
                                    "
                                >
                                    © 2026 Canteiro Obras. Todos os direitos reservados.
                                </p>

                                <p
                                    style="
                                        margin-top: 10px;
                                        color: #6b7280;
                                        font-size: 12px;
                                    "
                                >
                                    Este é um e-mail automático. Não responda.
                                </p>

                            </td>
                        </tr>

                    </table>

                </td>
            </tr>
        </table>

    </body>
    </html>
    """

    _enviar_email_brevo(
        email_destino=email_destino,
        assunto=assunto,
        html_content=corpo_html,
    )


def enviar_email_lembrete(
    email_destino: str,
    nome_projeto: str,
    descricao: str,
    data_referencia: date,
    recorrente: bool,
    tipo_recorrencia: str = None
):

    assunto = f"Lembrete do projeto: {nome_projeto}"

    tipo = "Data especifica"

    if recorrente:
        if tipo_recorrencia == "semanal":
            tipo = "Recorrente semanal"
        elif tipo_recorrencia == "mensal":
            tipo = "Recorrente mensal"

    corpo_texto = f"""
    Lembrete do projeto: {nome_projeto}

    Data de referencia: {data_referencia.strftime('%d/%m/%Y')}
    Tipo: {tipo}

    Descricao:
    {descricao}
    """

    corpo_html = f"""
    <!DOCTYPE html>
    <html lang="pt-BR">

    <head>
        <meta charset="UTF-8" />
    </head>

    <body
        style="
            margin: 0;
            padding: 0;
            background-color: #0f172a;
            font-family: Arial, Helvetica, sans-serif;
        "
    >

        <table
            width="100%"
            cellpadding="0"
            cellspacing="0"
            style="
                padding: 40px 20px;
                background-color: #0f172a;
            "
        >
            <tr>
                <td align="center">

                    <table
                        width="100%"
                        cellpadding="0"
                        cellspacing="0"
                        style="
                            max-width: 600px;
                            background-color: #111827;
                            border-radius: 24px;
                            overflow: hidden;
                            border: 1px solid rgba(255,255,255,0.08);
                        "
                    >

                        <tr>
                            <td
                                align="center"
                                style="
                                    background: linear-gradient(135deg, #10b981, #059669);
                                    padding: 40px 20px;
                                "
                            >

                                <h1
                                    style="
                                        color: white;
                                        margin: 0;
                                        font-size: 32px;
                                        letter-spacing: 1px;
                                    "
                                >
                                    Canteiro de Obras
                                </h1>

                                <p
                                    style="
                                        color: rgba(255,255,255,0.9);
                                        margin-top: 10px;
                                        font-size: 15px;
                                    "
                                >
                                    Lembrete automatico do projeto
                                </p>

                            </td>
                        </tr>

                        <tr>
                            <td
                                style="
                                    padding: 50px 40px;
                                    color: #e5e7eb;
                                "
                            >

                                <h2
                                    style="
                                        margin-top: 0;
                                        font-size: 28px;
                                        color: white;
                                    "
                                >
                                    {nome_projeto}
                                </h2>

                                <p
                                    style="
                                        font-size: 16px;
                                        line-height: 28px;
                                        color: #d1d5db;
                                        margin-bottom: 10px;
                                    "
                                >
                                    <strong style="color: #ffffff;">Data de referencia:</strong>
                                    {data_referencia.strftime('%d/%m/%Y')}
                                </p>

                                <p
                                    style="
                                        font-size: 16px;
                                        line-height: 28px;
                                        color: #d1d5db;
                                        margin-top: 0;
                                    "
                                >
                                    <strong style="color: #ffffff;">Tipo:</strong>
                                    {tipo}
                                </p>

                                <div
                                    style="
                                        margin: 30px 0 0;
                                        background-color: #0f172a;
                                        border: 1px solid rgba(16, 185, 129, 0.45);
                                        border-radius: 16px;
                                        padding: 20px;
                                    "
                                >
                                    <p
                                        style="
                                            margin: 0 0 10px;
                                            color: #10b981;
                                            font-weight: bold;
                                            font-size: 14px;
                                            letter-spacing: 0.4px;
                                            text-transform: uppercase;
                                        "
                                    >
                                        Descricao
                                    </p>

                                    <p
                                        style="
                                            margin: 0;
                                            white-space: pre-wrap;
                                            font-size: 16px;
                                            line-height: 28px;
                                            color: #e5e7eb;
                                        "
                                    >
                                        {descricao}
                                    </p>
                                </div>

                            </td>
                        </tr>

                        <tr>
                            <td
                                align="center"
                                style="
                                    padding: 30px;
                                    border-top: 1px solid rgba(255,255,255,0.06);
                                    background-color: #0b1220;
                                "
                            >

                                <p
                                    style="
                                        margin: 0;
                                        color: #6b7280;
                                        font-size: 13px;
                                        line-height: 24px;
                                    "
                                >
                                    © 2026 Canteiro Obras. Todos os direitos reservados.
                                </p>

                                <p
                                    style="
                                        margin-top: 10px;
                                        color: #6b7280;
                                        font-size: 12px;
                                    "
                                >
                                    Este e um e-mail automatico. Nao responda.
                                </p>

                            </td>
                        </tr>

                    </table>

                </td>
            </tr>
        </table>

    </body>
    </html>
    """

    _enviar_email_brevo(
        email_destino=email_destino,
        assunto=assunto,
        html_content=corpo_html,
    )