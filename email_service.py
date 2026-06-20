import smtplib

from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


SMTP_HOST = "smtp.gmail.com"
SMTP_PORT = 587

EMAIL_REMETENTE = "janderson.candido@gmail.com"
EMAIL_SENHA = "lzyf dqag yhgx vuek"


def enviar_codigo_recuperacao(
    email_destino: str,
    codigo: str
):

    mensagem = MIMEMultipart("alternative")

    mensagem["From"] = f"Canteiro de Obras <{EMAIL_REMETENTE}>"
    mensagem["To"] = email_destino
    mensagem["Subject"] = "Recuperação de senha"

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

    mensagem.attach(
        MIMEText(corpo_texto, "plain", "utf-8")
    )

    mensagem.attach(
        MIMEText(corpo_html, "html", "utf-8")
    )

    servidor = smtplib.SMTP(
        SMTP_HOST,
        SMTP_PORT
    )

    servidor.starttls()

    servidor.login(
        EMAIL_REMETENTE,
        EMAIL_SENHA
    )

    servidor.sendmail(
        EMAIL_REMETENTE,
        email_destino,
        mensagem.as_string()
    )

    servidor.quit()


def enviar_email_lembrete(
    email_destino: str,
    nome_projeto: str,
    descricao: str,
    data_referencia,
    recorrente: bool,
    tipo_recorrencia: str = None
):

    mensagem = MIMEMultipart("alternative")

    mensagem["From"] = f"Canteiro de Obras <{EMAIL_REMETENTE}>"
    mensagem["To"] = email_destino
    mensagem["Subject"] = f"Lembrete: {nome_projeto}"

    recorrencia_label = ""
    if recorrente and tipo_recorrencia:
        recorrencia_label = tipo_recorrencia.capitalize()
    elif recorrente:
        recorrencia_label = "Sim"
    else:
        recorrencia_label = "Não"

    data_formatada = (
        data_referencia.strftime("%d/%m/%Y")
        if hasattr(data_referencia, "strftime")
        else str(data_referencia)
    )

    corpo_texto = f"""
    Lembrete de Projeto — {nome_projeto}

    Descrição: {descricao}

    Data de referência: {data_formatada}
    Recorrente: {"Sim" if recorrente else "Não"}
    {"Tipo de recorrência: " + recorrencia_label if recorrente else ""}

    Este é um e-mail automático. Não responda.
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
                                    🔔 Lembrete de Projeto
                                </h2>

                                <p
                                    style="
                                        font-size: 16px;
                                        line-height: 28px;
                                        color: #d1d5db;
                                    "
                                >
                                    Você tem um lembrete pendente para o projeto abaixo.
                                </p>

                                <!-- PROJETO -->
                                <div
                                    style="
                                        margin: 30px 0;
                                        background-color: #0f172a;
                                        border-radius: 16px;
                                        padding: 28px 32px;
                                        border: 1px solid rgba(255,255,255,0.06);
                                    "
                                >

                                    <p
                                        style="
                                            margin: 0 0 6px 0;
                                            font-size: 12px;
                                            text-transform: uppercase;
                                            letter-spacing: 1px;
                                            color: #10b981;
                                        "
                                    >
                                        Projeto
                                    </p>

                                    <p
                                        style="
                                            margin: 0 0 20px 0;
                                            font-size: 20px;
                                            font-weight: bold;
                                            color: #ffffff;
                                        "
                                    >
                                        {nome_projeto}
                                    </p>

                                    <p
                                        style="
                                            margin: 0 0 6px 0;
                                            font-size: 12px;
                                            text-transform: uppercase;
                                            letter-spacing: 1px;
                                            color: #10b981;
                                        "
                                    >
                                        Descrição
                                    </p>

                                    <p
                                        style="
                                            margin: 0 0 20px 0;
                                            font-size: 16px;
                                            line-height: 26px;
                                            color: #e5e7eb;
                                        "
                                    >
                                        {descricao}
                                    </p>

                                    <table
                                        width="100%"
                                        cellpadding="0"
                                        cellspacing="0"
                                        style="margin-top: 10px;"
                                    >
                                        <tr>
                                            <td
                                                style="
                                                    width: 50%;
                                                    padding-right: 10px;
                                                    vertical-align: top;
                                                "
                                            >
                                                <p
                                                    style="
                                                        margin: 0 0 6px 0;
                                                        font-size: 12px;
                                                        text-transform: uppercase;
                                                        letter-spacing: 1px;
                                                        color: #10b981;
                                                    "
                                                >
                                                    Data de referência
                                                </p>
                                                <p
                                                    style="
                                                        margin: 0;
                                                        font-size: 15px;
                                                        color: #e5e7eb;
                                                    "
                                                >
                                                    {data_formatada}
                                                </p>
                                            </td>
                                            <td
                                                style="
                                                    width: 50%;
                                                    padding-left: 10px;
                                                    vertical-align: top;
                                                "
                                            >
                                                <p
                                                    style="
                                                        margin: 0 0 6px 0;
                                                        font-size: 12px;
                                                        text-transform: uppercase;
                                                        letter-spacing: 1px;
                                                        color: #10b981;
                                                    "
                                                >
                                                    Recorrência
                                                </p>
                                                <p
                                                    style="
                                                        margin: 0;
                                                        font-size: 15px;
                                                        color: #e5e7eb;
                                                    "
                                                >
                                                    {recorrencia_label if recorrente else "Não recorrente"}
                                                </p>
                                            </td>
                                        </tr>
                                    </table>

                                </div>

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

    mensagem.attach(
        MIMEText(corpo_texto, "plain", "utf-8")
    )

    mensagem.attach(
        MIMEText(corpo_html, "html", "utf-8")
    )

    servidor = smtplib.SMTP(
        SMTP_HOST,
        SMTP_PORT
    )

    servidor.starttls()

    servidor.login(
        EMAIL_REMETENTE,
        EMAIL_SENHA
    )

    servidor.sendmail(
        EMAIL_REMETENTE,
        email_destino,
        mensagem.as_string()
    )

    servidor.quit()