import streamlit as st
from database import SessionLocal
import models
import pandas as pd
from datetime import date
import os
import bcrypt
import time
from streamlit_option_menu import option_menu

session = SessionLocal()

st.set_page_config(
    page_title="Canteiro de Obras",
    page_icon="🏗️",
    layout="wide"
)

BASE_UPLOAD_PATH = "uploads"

# ==========================
# SESSION STATE
# ==========================
if "projeto_custos_id" not in st.session_state:
    st.session_state.projeto_custos_id = None

if "projeto_arquivos_id" not in st.session_state:
    st.session_state.projeto_arquivos_id = None

if "editar_projeto_id" not in st.session_state:
    st.session_state.editar_projeto_id = None

if "editar_lancamento_id" not in st.session_state:
    st.session_state.editar_lancamento_id = None

if "somar_lancamento_id" not in st.session_state:
    st.session_state.somar_lancamento_id = None

if "projeto_unidades_id" not in st.session_state:
    st.session_state.projeto_unidades_id = None

# ==========================
# RESET DE VIEWS
# ==========================
def reset_views():
    st.session_state.projeto_unidades_id = None
    st.session_state.projeto_custos_id = None
    st.session_state.projeto_arquivos_id = None
    st.session_state.editar_projeto_id = None
    st.session_state.editar_lancamento_id = None
    

# ==========================
# LOGIN PERSISTENTE FUNCIONAL
# ==========================

if "logado" not in st.session_state:
    st.session_state.logado = False

if "usuario_id" not in st.session_state:
    st.session_state.usuario_id = None

# ==========================
# RECUPERA LOGIN VIA QUERY PARAM
# ==========================
query_user = st.query_params.get("user")

if query_user and not st.session_state.logado:
    try:
        st.session_state.usuario_id = int(query_user)
        st.session_state.logado = True
    except:
        pass

import base64

def get_base64(file_path):
    base_dir = os.path.dirname(os.path.abspath(__file__))
    full_path = os.path.join(base_dir, file_path)

    if not os.path.exists(full_path):
        st.error(f"Imagem não encontrada: {full_path}")
        return ""

    with open(full_path, "rb") as f:
        return base64.b64encode(f.read()).decode()

bg_img = get_base64("assets/background.png")

# ==========================
# LOGIN
# ==========================
if not st.session_state.logado:

    st.markdown(f"""
    <style>
    .stApp {{
        background-image: url("data:image/png;base64,{bg_img}");
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
    }}

    header, footer {{visibility: hidden;}}
    section[data-testid="stSidebar"] {{display: none;}}

    .block-container {{
        padding-top: 0rem !important;
    }}

    /* CARD */
    .login-card {{
        background: rgba(255,255,255,0.08);
        backdrop-filter: blur(20px);
        padding: 40px;
        border-radius: 20px;
        box-shadow: 0 20px 60px rgba(0,0,0,0.5);
    }}

    .login-title {{
        text-align: center;
        font-size: 28px;
        font-weight: bold;
        color: white;
        margin-bottom: 20px;
    }}
    </style>
    """, unsafe_allow_html=True)

    st.markdown("""
    <style>
    header, footer {visibility: hidden;}
    section[data-testid="stSidebar"] {display: none;}

    .block-container {
        padding-top: 0rem !important;
    }

    /* CARD */
    .login-card {
        background: rgba(255,255,255,0.08);
        backdrop-filter: blur(20px);
        padding: 40px;
        border-radius: 20px;
        box-shadow: 0 20px 60px rgba(0,0,0,0.5);
        display: none;
    }

    .login-title {
        text-align: center;
        font-size: 28px;
        font-weight: bold;
        color: white;
        margin-bottom: 20px;
    }
    </style>
    """, unsafe_allow_html=True)

    # CENTRALIZA HORIZONTALMENTE (ESSA É A CHAVE)
    col1, col2, col3 = st.columns([1, 2, 1])

    with col2:
        st.markdown('<div class="login-card">', unsafe_allow_html=True)
        st.markdown('<div class="login-title">🏗️ Canteiro de Obras</div>', unsafe_allow_html=True)

        username = st.text_input("Usuário")
        senha = st.text_input("Senha", type="password")

        if st.button("Entrar", use_container_width=True):
            user = session.query(models.Usuario).filter_by(
                username=username
            ).first()

            if user and bcrypt.checkpw(
                senha.encode(),
                user.senha_hash.encode()
            ):
                st.session_state.logado = True
                st.session_state.usuario_id = user.id
                st.query_params["user"] = str(user.id)

                st.success("Login realizado com sucesso!")
                time.sleep(1)
                st.rerun()
            else:
                st.error("Usuário ou senha inválidos")

        st.markdown('</div>', unsafe_allow_html=True)

    st.stop()

# ==========================
# LOGOUT
# ==========================
if st.button("🚪 Sair"):
    st.session_state.clear()

    # Remove query param
    st.query_params.clear()

    st.rerun()

# ==========================
# CONTROLE DE EXPIRAÇÃO
# ==========================
if "last_activity" not in st.session_state:
    st.session_state.last_activity = time.time()

if time.time() - st.session_state.last_activity > 1800:
    st.session_state.clear()
    st.query_params.clear()

    st.warning("Sessão expirada. Faça login novamente.")
    st.rerun()

st.session_state.last_activity = time.time()


# 5. Add on_change callback
def on_change(key):
    selection = st.session_state[key]
    st.write(f"Selection changed to {selection}")

# ==========================
# MENU
# ==========================

with st.sidebar:
    menu = option_menu(
        "Main Menu",
        ["Dashboard", "Projetos", "Categorias", "Recursos", "Etapas da Obra", "Tipos de Arquivo"],
        icons=["house", "journal-check", "gear", "tags-fill", "diagram-3", "file-earmark"],
        menu_icon="cast",
        default_index=0,
    )

# ==========================
# DASHBOARD
# ==========================
if menu == "Dashboard":
    st.title("📊 Dashboard")

    st.subheader("🌎 Visão Geral de Todos os Projetos")

    import plotly.express as px

    projetos_all = session.query(models.Projeto).all()

    data_projetos = []
    total_geral = 0

    for p in projetos_all:
        custos = session.query(models.Custo).filter(
            models.Custo.projeto_id == p.id
        ).all()

        total_pago = sum([float(c.valor_pago or 0) for c in custos])

        total_geral += total_pago

        data_projetos.append({
            "Projeto": p.nome,
            "Total Pago": total_pago
        })

    # KPI total geral
    st.metric("💰 Total Geral Investido", f"R$ {total_geral:,.2f}")

    # gráfico pizza
    df_proj = pd.DataFrame(data_projetos)

    if not df_proj.empty and df_proj["Total Pago"].sum() > 0:
        fig_proj = px.pie(
            df_proj,
            values="Total Pago",
            names="Projeto",
            hole=0.4
        )

        fig_proj.update_layout(template="plotly_white")

        st.plotly_chart(fig_proj, use_container_width=True)
    else:
        st.info("Sem dados de custos nos projetos.")
        

    projetos = session.query(models.Projeto).all()

    projeto_filtro = st.selectbox(
        "Selecione um Projeto",
        [None] + projetos,
        format_func=lambda x: "Selecione..." if x is None else x.nome
    )

    if projeto_filtro is None:
        st.info("Selecione um projeto para visualizar o dashboard.")
        st.stop()

    lancamentos = session.query(models.Custo).filter(
        models.Custo.projeto_id == projeto_filtro.id
    ).all()

    data_pago = []
    data_saldo = []

    total_pago_geral = 0

    for c in lancamentos:
        valor_previsto = c.valor_previsto or 0
        valor_pago = c.valor_pago or 0
        saldo = valor_previsto - valor_pago

        total_pago_geral += valor_pago

        data_pago.append({
            "Categoria": c.categoria.nome if c.categoria else "-",
            "Observação": c.descricao if c.descricao else "-",
            "Etapa": c.etapa.nome if c.etapa else "Não definido",
            "Pago": valor_pago
        })

        if saldo > 0:
            data_saldo.append({
                "Categoria": c.categoria.nome if c.categoria else "-",
                "Observação": c.descricao if c.descricao else "-",
                "Saldo": saldo
            })

    meta_lucro = total_pago_geral * 0.3
    valor_venda_total = total_pago_geral + meta_lucro

    unidades = projeto_filtro.quantidade_unidades or 0

    if unidades > 0:
        custo_por_unidade = total_pago_geral / unidades
        venda_por_unidade = valor_venda_total / unidades
    else:
        custo_por_unidade = 0
        venda_por_unidade = 0

    col1, col2, col3, col4, col5 = st.columns(5)

    col1.metric("💰 Total Pago", f"R$ {total_pago_geral:,.2f}")
    col2.metric("📈 Lucro (30%)", f"R$ {meta_lucro:,.2f}")
    col3.metric("🏷️ Venda Total", f"R$ {valor_venda_total:,.2f}")
    col4.metric("📦 Custo por Unidade", f"R$ {custo_por_unidade:,.2f}")
    col5.metric("🏠 Venda por Unidade", f"R$ {venda_por_unidade:,.2f}")

    st.divider()

    if data_pago:
        import plotly.express as px
        from streamlit_plotly_events import plotly_events

        df_pago = pd.DataFrame(data_pago)

        resumo_pago = (
            df_pago.groupby("Categoria", as_index=False)["Pago"]
            .sum()
            .sort_values("Pago", ascending=False)
            .reset_index(drop=True)
        )

        resumo_pago["Percentual"] = (
            resumo_pago["Pago"] / resumo_pago["Pago"].sum() * 100
        )

        st.subheader("💰 Distribuição de Pagamentos por Categoria")

        if "categoria_click" not in st.session_state:
            st.session_state.categoria_click = None

        fig = px.pie(
            resumo_pago,
            values="Pago",
            names="Categoria",
            hole=0.3
        )

        fig.update_layout(template="plotly_white")

        selected = plotly_events(
            fig,
            click_event=True,
            hover_event=False,
            key="pizza_pagamentos"
        )

        if selected:
            index = selected[0]["pointNumber"]
            categoria = resumo_pago.iloc[index]["Categoria"]
            st.session_state.categoria_click = categoria

        col1, col2 = st.columns([4, 1])

        if st.session_state.categoria_click:
            col1.info(f"📌 Filtrando por: {st.session_state.categoria_click}")

            if col2.button("❌ Limpar filtro"):
                st.session_state.categoria_click = None
                st.rerun()

        st.subheader("📄 Detalhamento de Pagamentos")

        df_detalhe = df_pago.copy()

        if st.session_state.categoria_click:
            df_detalhe = df_detalhe[
                df_detalhe["Categoria"] == st.session_state.categoria_click
            ]

        df_detalhe = df_detalhe.sort_values(
            by=["Categoria", "Pago"],
            ascending=[True, False]
        )

        st.dataframe(
            df_detalhe[["Categoria", "Observação", "Pago"]],
            use_container_width=True
        )

    else:
        st.info("Sem pagamentos registrados.")

    st.divider()
    st.subheader("🏗️ Distribuição de Custos por Etapa da Obra")

    if data_pago:
        import plotly.express as px
        from streamlit_plotly_events import plotly_events

        df_etapa = pd.DataFrame(data_pago)

        resumo_etapa = (
            df_etapa.groupby("Etapa", as_index=False)["Pago"]
            .sum()
            .sort_values("Pago", ascending=False)
            .reset_index(drop=True)
        )

        resumo_etapa["Percentual"] = (
            resumo_etapa["Pago"] / resumo_etapa["Pago"].sum() * 100
        )

        if "etapa_click" not in st.session_state:
            st.session_state.etapa_click = None

        fig = px.pie(
            resumo_etapa,
            values="Pago",
            names="Etapa",
            hole=0.3
        )

        fig.update_layout(template="plotly_white")

        selected = plotly_events(
            fig,
            click_event=True,
            hover_event=False,
            key="pizza_etapas"
        )

        if selected:
            index = selected[0]["pointNumber"]
            etapa = resumo_etapa.iloc[index]["Etapa"]
            st.session_state.etapa_click = etapa

        col1, col2 = st.columns([4, 1])

        if st.session_state.etapa_click:
            col1.info(f"📌 Filtrando etapa: {st.session_state.etapa_click}")

            if col2.button("❌ Limpar filtro etapa"):
                st.session_state.etapa_click = None
                st.rerun()

        st.subheader("📄 Detalhamento por Etapa")

        df_detalhe = df_etapa.copy()

        if st.session_state.etapa_click:
            df_detalhe = df_detalhe[
                df_detalhe["Etapa"] == st.session_state.etapa_click
            ]

        df_detalhe = df_detalhe.sort_values(
            by=["Etapa", "Pago"],
            ascending=[True, False]
        )

        st.dataframe(
            df_detalhe[["Etapa", "Categoria", "Observação", "Pago"]],
            use_container_width=True
        )
    else:
        st.info("Sem dados para etapas.")

    st.subheader("💸 Saldo Ainda a Pagar")

    if data_saldo:
        import altair as alt

        df_saldo = pd.DataFrame(data_saldo)

        total_pendente = df_saldo["Saldo"].sum()

        st.metric("Total Pendente", f"R$ {total_pendente:,.2f}")

        resumo_saldo = (
            df_saldo.groupby("Categoria", as_index=False)["Saldo"]
            .sum()
            .sort_values("Saldo", ascending=False)
        )

        resumo_saldo["Percentual"] = resumo_saldo["Saldo"] / total_pendente * 100

        st.subheader("📊 Distribuição de Saldo por Categoria")

        chart = (
            alt.Chart(resumo_saldo)
            .mark_arc()
            .encode(
                theta=alt.Theta(field="Saldo", type="quantitative"),
                color=alt.Color(field="Categoria", type="nominal"),
                tooltip=[
                    "Categoria",
                    alt.Tooltip("Saldo:Q", format=",.2f"),
                    alt.Tooltip("Percentual:Q", format=".2f")
                ]
            )
        )

        st.altair_chart(chart, use_container_width=True)

        st.subheader("📄 Lançamentos Pendentes")
        st.dataframe(
            df_saldo[["Categoria", "Observação", "Saldo"]],
            use_container_width=True
        )

    else:
        st.info("Sem saldo pendente.")


elif menu == "Etapas da Obra":
    st.title("🏗️ Etapas da Obra")

    nome = st.text_input("Nome da Etapa (ex: Fundação, Alvenaria)")

    if st.button("Salvar Etapa"):
        session.add(models.EtapaObra(nome=nome))
        session.commit()
        st.success("Etapa cadastrada!")
        st.rerun()

    st.subheader("Etapas cadastradas")

    h1, h2, h3 = st.columns([1,5,2])
    h1.markdown("**ID**")
    h2.markdown("**Nome**")
    h3.markdown("**Ações**")

    for e in session.query(models.EtapaObra).all():
        col1, col2, col3 = st.columns([1,5,2])
        col1.write(e.id)
        col2.write(e.nome)

        if col3.button("Deletar", key=f"etapa_{e.id}"):
            session.delete(e)
            session.commit()
            st.rerun()
# ==========================
# PROJETOS
# ==========================
elif menu == "Projetos":
    st.title("🏗️ Projetos")

    if (
        st.session_state.projeto_custos_id is None and
        st.session_state.projeto_arquivos_id is None and
        st.session_state.projeto_unidades_id is None
    ):

        # ==========================
        # EDITAR PROJETO
        # ==========================
        if st.session_state.editar_projeto_id:
            projeto_editar = session.query(models.Projeto).get(
                st.session_state.editar_projeto_id
            )

            st.subheader("✏️ Editar Projeto")

            nome = st.text_input("Nome", value=projeto_editar.nome)
            data_inicio = st.date_input("Data de Início", value=projeto_editar.data_inicio)
            data_fim = st.date_input("Data de Fim", value=projeto_editar.data_fim)
            endereco = st.text_input("Endereço", value=projeto_editar.endereco)
            valor_venda = st.number_input(
                "Valor de Venda do Projeto",
                min_value=0.0,
                value=float(projeto_editar.valor_venda or 0)
            )

            quantidade_unidades = st.number_input(
                "Quantidade de Unidades",
                min_value=0,
                value=int(projeto_editar.quantidade_unidades or 0)
            )

            col1, col2 = st.columns(2)

            if col1.button("Atualizar Projeto"):
                projeto_editar.nome = nome
                projeto_editar.data_inicio = data_inicio
                projeto_editar.data_fim = data_fim
                projeto_editar.endereco = endereco
                projeto_editar.quantidade_unidades = quantidade_unidades
                projeto_editar.valor_venda = valor_venda

                session.commit()
                st.session_state.editar_projeto_id = None
                st.success("Projeto atualizado com sucesso!")
                st.rerun()

            if col2.button("Cancelar Edição"):
                st.session_state.editar_projeto_id = None
                st.rerun()

        # ==========================
        # NOVO PROJETO
        # ==========================
        else:
            st.subheader("➕ Novo Projeto")

            nome = st.text_input("Nome")
            data_inicio = st.date_input("Data de Início", value=None)
            data_fim = st.date_input("Data de Fim", value=None)
            endereco = st.text_input("Endereço")
            valor_venda = st.number_input(
                "Valor de Venda do Projeto",
                min_value=0.0,
                value=0.0
            ) 

            quantidade_unidades = st.number_input(
                "Quantidade de Unidades",
                min_value=0,
                value=0
            )

            if st.button("Salvar Projeto"):
                session.add(models.Projeto(
                    nome=nome,
                    data_inicio=data_inicio,
                    data_fim=data_fim,
                    endereco=endereco,
                    quantidade_unidades=quantidade_unidades,
                    valor_venda=valor_venda
                ))
                session.commit()
                st.success("Projeto cadastrado com sucesso!")
                st.rerun()

        # ==========================
        # LISTAGEM
        # ==========================
        st.subheader("Projetos cadastrados")

        h1, h2, h3, h4, h5, h6, h7, h8, h9 = st.columns([3,2,2,2,2,2,2,2,2])

        h1.markdown("**Nome**")
        h2.markdown("**Período**")
        h3.markdown("**Endereço**")
        h4.markdown("**Unidades**")
        h5.markdown("**Valor de Venda**")
        h6.markdown("**Lançamentos**")
        h7.markdown("**Arquivos**")
        h8.markdown("**Editar**")
        h9.markdown("**Excluir**")

        for p in session.query(models.Projeto).all():
            col1, col2, col3, col4, col5, col6, col7, col8, col9 = st.columns([3,2,2,2,2,2,2,2,2])

            col1.write(p.nome)
            col2.write(f"{p.data_inicio} até {p.data_fim}" if p.data_fim else f"{p.data_inicio}")
            col3.write(p.endereco)
            col4.write(p.quantidade_unidades or 0)

            if col5.button("Unidades", key=f"unidades_{p.id}"):
                reset_views()
                st.session_state.projeto_unidades_id = p.id
                st.rerun()

            if col6.button("Lançamentos", key=f"custos_projeto_{p.id}"):
                reset_views()
                st.session_state.projeto_custos_id = p.id
                st.rerun()

            if col7.button("Arquivos", key=f"arquivos_projeto_{p.id}"):
                reset_views()
                st.session_state.projeto_arquivos_id = p.id
                st.rerun()

            if col8.button("Editar", key=f"editar_projeto_{p.id}"):
                reset_views()
                st.session_state.editar_projeto_id = p.id
                st.rerun()

            if col9.button("Deletar", key=f"deletar_projeto_{p.id}"):
                reset_views()
                session.delete(p)
                session.commit()
                st.success("Projeto deletado com sucesso!")
                st.rerun()

    elif st.session_state.projeto_unidades_id is not None:
        projeto = session.query(models.Projeto).get(
            st.session_state.projeto_unidades_id
        )

        st.subheader(f"🏠 Unidades do Projeto: {projeto.nome}")

        if st.button("← Voltar para Projetos"):
            st.session_state.projeto_unidades_id = None
            reset_views()
            st.rerun()

        st.divider()

        # ==========================
        # NOVA UNIDADE
        # ==========================
        st.subheader("➕ Nova Unidade")

        numero = st.text_input("Número / Identificação")
        valor_venda = st.number_input("Valor de Venda", min_value=0.0, value=0.0)

        if st.button("Salvar Unidade"):
            session.add(models.Unidade(
                numero=numero,
                valor_venda=valor_venda,
                projeto_id=projeto.id
            ))
            session.commit()
            st.success("Unidade cadastrada!")
            st.rerun()

        # ==========================
        # LISTAGEM
        # ==========================
        st.subheader("Unidades cadastradas")

        unidades = session.query(models.Unidade).filter_by(
            projeto_id=projeto.id
        ).all()

        if not unidades:
            st.info("Nenhuma unidade cadastrada.")
        else:
            h1, h2, h3 = st.columns([3,3,2])
            h1.markdown("**Número**")
            h2.markdown("**Valor Venda**")
            h3.markdown("**Ações**")

            for u in unidades:
                col1, col2, col3 = st.columns([3,3,2])

                col1.write(u.numero)
                col2.write(f"R$ {float(u.valor_venda or 0):,.2f}")

                if col3.button("Deletar", key=f"del_un_{u.id}"):
                    session.delete(u)
                    session.commit()
                    st.rerun()

    # ==========================
    # LANÇAMENTOS
    # ==========================
    elif st.session_state.projeto_custos_id is not None:
        projeto = session.query(models.Projeto).get(
            st.session_state.projeto_custos_id
        )

        st.subheader(f"💰 Lançamentos do Projeto: {projeto.nome}")

        if st.button("← Voltar para Projetos"):
            st.session_state.projeto_custos_id = None
            st.session_state.editar_lancamento_id = None
            st.rerun()

        categorias = session.query(models.Categoria).all()
        etapas = session.query(models.EtapaObra).all()

        @st.dialog("➕ Somar valores no lançamento")
        def modal_somar_lancamento(lancamento_id):
            lancamento_soma = session.query(models.Custo).get(lancamento_id)

            st.write(f"Observação: {lancamento_soma.descricao or '-'}")

            st.write(
                f"Valor previsto atual: R$ {float(lancamento_soma.valor_previsto or 0):,.2f}"
            )

            st.write(
                f"Valor pago atual: R$ {float(lancamento_soma.valor_pago or 0):,.2f}"
            )

            valor_adicional_previsto = st.number_input(
                "Adicionar ao Previsto",
                min_value=0.0,
                value=0.0,
                key=f"modal_prev_{lancamento_id}"
            )

            valor_adicional_pago = st.number_input(
                "Adicionar ao Pago",
                min_value=0.0,
                value=0.0,
                key=f"modal_pago_{lancamento_id}"
            )

            col1, col2 = st.columns(2)

            if col1.button("Salvar"):
                lancamento_soma.valor_previsto = float(
                    lancamento_soma.valor_previsto or 0
                ) + valor_adicional_previsto

                lancamento_soma.valor_pago = float(
                    lancamento_soma.valor_pago or 0
                ) + valor_adicional_pago

                session.commit()

                st.success("Valores somados com sucesso!")
                st.rerun()

            if col2.button("Cancelar"):
                st.rerun()

        
        # ==========================
        # FORMULÁRIO (EDIÇÃO)
        # ==========================
        if st.session_state.editar_lancamento_id:
            lancamento = session.query(models.Custo).get(
                st.session_state.editar_lancamento_id
            )

            st.subheader("✏️ Editar Lançamento")

            categoria = st.selectbox(
                "Categoria",
                categorias,
                index=categorias.index(lancamento.categoria),
                format_func=lambda x: x.nome
            )

            etapa = st.selectbox(
                "Etapa da Obra",
                etapas,
                index=etapas.index(lancamento.etapa) if lancamento.etapa in etapas else 0,
                format_func=lambda x: x.nome
            )

            descricao = st.text_input(
                "Observação",
                value=lancamento.descricao or ""
            )

            valor_previsto = st.number_input(
                "Valor Previsto",
                min_value=0.0,
                value=float(lancamento.valor_previsto or 0)
            )

            valor_pago = st.number_input(
                "Valor Pago",
                min_value=0.0,
                value=float(lancamento.valor_pago or 0)
            )

            quantidade = st.number_input(
                "Quantidade",
                min_value=0.0,
                value=float(lancamento.quantidade or 1)
            )

            valor_unitario = st.number_input(
                "Valor Unitário",
                min_value=0.0,
                value=float(lancamento.valor_unitario or 0)
            )

            data_custo = st.date_input(
                "Data",
                value=lancamento.data
            )

            col1, col2 = st.columns(2)

            if col1.button("Atualizar Lançamento"):
                lancamento.categoria_id = categoria.id
                lancamento.descricao = descricao
                lancamento.valor_previsto = valor_previsto
                lancamento.valor_pago = valor_pago
                lancamento.data = data_custo
                lancamento.quantidade = quantidade
                lancamento.valor_unitario = valor_unitario
                lancamento.etapa_id = etapa.id if etapa else None

                session.commit()
                st.session_state.editar_lancamento_id = None
                st.success("Lançamento atualizado com sucesso!")
                st.rerun()

            if col2.button("Cancelar Edição"):
                st.session_state.editar_lancamento_id = None
                st.rerun()

        # ==========================
        # NOVO LANÇAMENTO
        # ==========================
        else:
            st.subheader("➕ Novo Lançamento")

            categoria = st.selectbox(
                "Categoria",
                categorias,
                format_func=lambda x: x.nome
            )

            descricao = st.text_input("Observação")

            col1, col2 = st.columns(2)

            quantidade = col1.number_input(
                "Quantidade",
                min_value=0.0,
                value=1.0
            )

            valor_unitario = col2.number_input(
                "Valor Unitário",
                min_value=0.0,
                value=0.0
            )

            valor_previsto = st.number_input(
                "Valor Previsto",
                min_value=0.0,
                value=0.0
            )

            valor_pago = st.number_input(
                "Valor Pago",
                min_value=0.0,
                value=0.0
            )

            data_custo = st.date_input(
                "Data",
                value=date.today()
            )

            etapa = st.selectbox(
                "Etapa da Obra",
                etapas,
                format_func=lambda x: x.nome
            )

            if st.button("Salvar Lançamento"):
                session.add(models.Custo(
                    descricao=descricao,
                    quantidade=quantidade,
                    valor_unitario=valor_unitario,
                    valor_previsto=valor_previsto,
                    valor_pago=valor_pago,
                    data=data_custo,
                    projeto_id=projeto.id,
                    categoria_id=categoria.id,
                    etapa_id=etapa.id if etapa else None
                ))

                session.commit()
                st.success("Lançamento salvo com sucesso!")
                st.rerun()

        # ==========================
        # LISTAGEM
        # ==========================
        st.subheader("Lançamentos cadastrados")

        st.subheader("🔎 Filtros")

        colf1, colf2, colf3 = st.columns(3)

        # 🔎 Observação
        filtro_obs = colf1.text_input(
            "Observação",
            key="filtro_obs_lancamentos"
        )

        # 🗂️ Categoria
        categorias_filtro = [None] + categorias
        filtro_categoria = colf2.selectbox(
            "Categoria",
            categorias_filtro,
            format_func=lambda x: "Todas" if x is None else x.nome,
            key="filtro_categoria_lancamentos"
        )

        # 🏗️ Etapa
        etapas_filtro = [None] + etapas
        filtro_etapa = colf3.selectbox(
            "Etapa",
            etapas_filtro,
            format_func=lambda x: "Todas" if x is None else x.nome,
            key="filtro_etapa_lancamentos"
        )

        # ==========================
        # BUSCA NO BANCO
        # ==========================
        query = session.query(models.Custo).filter(
            models.Custo.projeto_id == projeto.id
        )

        # 🔎 filtro por observação
        if filtro_obs:
            query = query.filter(
                models.Custo.descricao.ilike(f"%{filtro_obs}%")
            )

        # 🗂️ filtro por categoria
        if filtro_categoria:
            query = query.filter(
                models.Custo.categoria_id == filtro_categoria.id
            )

        # 🏗️ filtro por etapa
        if filtro_etapa:
            query = query.filter(
                models.Custo.etapa_id == filtro_etapa.id
            )

        # ordenação
        query = query.order_by(models.Custo.id.desc())

        lancamentos = query.limit(50).all()

        # ==========================
        # EXPORTAÇÃO CSV (SEMPRE COMPLETO)
        # ==========================

        lancamentos_export = session.query(models.Custo).filter(
            models.Custo.projeto_id == projeto.id
        ).order_by(models.Custo.id.desc()).all()

        if lancamentos_export:
            data_export = []

            for c in lancamentos_export:
                data_export.append({
                    "ID": c.id,
                    "Observacao": c.descricao,
                    "Categoria": c.categoria.nome if c.categoria else "-",
                    "Valor Previsto": float(c.valor_previsto or 0),
                    "Valor Pago": float(c.valor_pago or 0),
                    "Quantidade": float(c.quantidade or 0),
                    "Valor Unitario": float(c.valor_unitario or 0),
                    "Data": c.data,
                    "Etapa": c.etapa.nome if c.etapa else "-",
                })

            df_export = pd.DataFrame(data_export)

            csv = df_export.to_csv(
                index=False,
                sep=";"
            ).encode("utf-8")

            st.download_button(
                label="📥 Exportar CSV (Completo)",
                data=csv,
                file_name=f"lancamentos_projeto_{projeto.id}.csv",
                mime="text/csv"
            )

        # ==========================
        # TABELA
        # ==========================
        h0, h1, h2, h3, h4, h5, h6, h7, h8, h9 = st.columns(
            [1,3,2,2,2,2,2,2,2,2]
        )

        h0.markdown("**ID**")
        h1.markdown("**Observação**")
        h2.markdown("**Categoria**")
        h3.markdown("**Etapa**")
        h4.markdown("**Previsto**")
        h5.markdown("**Pago**")
        h6.markdown("**Qtd**")
        h7.markdown("**Somar**")
        h8.markdown("**Editar**")
        h9.markdown("**Excluir**")

        if not lancamentos:
            st.info("Nenhum lançamento encontrado.")
        else:
            for c in lancamentos:
                valor_previsto = float(c.valor_previsto or 0)
                valor_pago = float(c.valor_pago or 0)
                quantidade = float(c.quantidade or 0)

                col0, col1, col2, col3, col4, col5, col6, col7, col8, col9 = st.columns(
                    [1,3,2,2,2,2,2,2,2,2]
                )

                col0.write(c.id)
                col1.write(c.descricao or "-")
                col2.write(c.categoria.nome if c.categoria else "-")
                col3.write(c.etapa.nome if c.etapa else "-")
                col4.write(f"R$ {valor_previsto:,.2f}")
                col5.write(f"R$ {valor_pago:,.2f}")
                col6.write(quantidade)

                # SOMAR (modal)
                if col7.button("Somar", key=f"somar_lancamento_{c.id}"):
                    modal_somar_lancamento(c.id)

                # EDITAR
                if col8.button("Editar", key=f"editar_lancamento_{c.id}"):
                    st.session_state.editar_lancamento_id = c.id
                    st.rerun()

                # DELETAR
                if col9.button("Deletar", key=f"deletar_lancamento_{c.id}"):
                    session.delete(c)
                    session.commit()
                    st.success("Lançamento deletado com sucesso!")
                    st.rerun()

    # ==========================
    # ARQUIVOS DO PROJETO
    # ==========================
    elif st.session_state.projeto_arquivos_id is not None:
        projeto = session.query(models.Projeto).get(
            st.session_state.projeto_arquivos_id
        )

        st.subheader(f"📁 Arquivos do Projeto: {projeto.nome}")

        if st.button("← Voltar para Projetos", key="voltar_arquivos"):
            st.session_state.projeto_arquivos_id = None
            st.rerun()

        tipos_arquivo = session.query(models.TipoArquivo).all()

        if not tipos_arquivo:
            st.warning("Cadastre pelo menos um Tipo de Arquivo antes de enviar arquivos.")
            st.stop()

        tipo_arquivo = st.selectbox(
            "Tipo de Arquivo",
            tipos_arquivo,
            format_func=lambda x: x.nome
        )

        uploaded_file = st.file_uploader("Selecionar arquivo")

        # ==========================
        # UPLOAD
        # ==========================
        if st.button("Salvar Arquivo") and uploaded_file:
            projeto_path = os.path.join(
                BASE_UPLOAD_PATH,
                projeto.nome
            )

            tipo_path = os.path.join(
                projeto_path,
                tipo_arquivo.nome
            )

            os.makedirs(tipo_path, exist_ok=True)

            file_path = os.path.join(
                tipo_path,
                uploaded_file.name
            )

            with open(file_path, "wb") as f:
                f.write(uploaded_file.getbuffer())

            st.success("Arquivo enviado com sucesso!")
            st.rerun()

        # ==========================
        # LISTAGEM
        # ==========================
        projeto_path = os.path.join(
            BASE_UPLOAD_PATH,
            projeto.nome
        )

        st.subheader("Arquivos cadastrados")

        if not os.path.exists(projeto_path):
            st.info("Nenhum arquivo cadastrado para este projeto.")

        else:
            encontrou_arquivo = False

            for tipo in os.listdir(projeto_path):
                tipo_dir = os.path.join(projeto_path, tipo)

                if not os.path.isdir(tipo_dir):
                    continue

                arquivos = os.listdir(tipo_dir)

                if not arquivos:
                    continue

                encontrou_arquivo = True

                st.markdown(f"### {tipo}")

                h1, h2, h3 = st.columns([5, 2, 2])
                h1.markdown("**Arquivo**")
                h2.markdown("**Download**")
                h3.markdown("**Ações**")

                for arquivo in arquivos:
                    file_path = os.path.join(tipo_dir, arquivo)

                    col1, col2, col3 = st.columns([5, 2, 2])

                    col1.write(arquivo)

                    with open(file_path, "rb") as file_data:
                        col2.download_button(
                            label="Baixar",
                            data=file_data.read(),
                            file_name=arquivo,
                            mime="application/octet-stream",
                            key=f"download_{projeto.id}_{tipo}_{arquivo}"
                        )

                    if col3.button(
                        "Deletar",
                        key=f"deletar_arquivo_{projeto.id}_{tipo}_{arquivo}"
                    ):
                        os.remove(file_path)

                        if not os.listdir(tipo_dir):
                            os.rmdir(tipo_dir)

                        st.success("Arquivo deletado com sucesso!")
                        st.rerun()

            if not encontrou_arquivo:
                st.info("Nenhum arquivo cadastrado para este projeto.")

# ==========================
# RECURSOS
# ==========================
elif menu == "Recursos":
    st.title("🧩 Recursos")

    nome = st.text_input("Nome do Recurso")

    if st.button("Salvar Recurso"):
        session.add(models.Recurso(nome=nome))
        session.commit()
        st.rerun()

    st.subheader("Recursos cadastrados")

    h1, h2, h3 = st.columns([1,5,2])
    h1.markdown("**ID**")
    h2.markdown("**Nome**")
    h3.markdown("**Ações**")

    for r in session.query(models.Recurso).all():
        col1, col2, col3 = st.columns([1,5,2])
        col1.write(r.id)
        col2.write(r.nome)

        if col3.button("Deletar", key=f"rec_{r.id}"):
            session.delete(r)
            session.commit()
            st.rerun()

# ==========================
# CATEGORIAS
# ==========================
elif menu == "Categorias":
    st.title("📂 Categorias")

    nome = st.text_input("Nome da Categoria")

    if st.button("Salvar Categoria"):
        session.add(models.Categoria(nome=nome))
        session.commit()
        st.rerun()

    st.subheader("Categorias cadastradas")

    h1, h2, h3 = st.columns([1,5,2])
    h1.markdown("**ID**")
    h2.markdown("**Nome**")
    h3.markdown("**Ações**")

    for c in session.query(models.Categoria).all():
        col1, col2, col3 = st.columns([1,5,2])
        col1.write(c.id)
        col2.write(c.nome)

        if col3.button("Deletar", key=f"cat_{c.id}"):
            session.delete(c)
            session.commit()
            st.rerun()

# ==========================
# TIPOS DE ARQUIVO
# ==========================
elif menu == "Tipos de Arquivo":
    st.title("📁 Tipos de Arquivo")

    nome = st.text_input("Nome do Tipo de Arquivo")

    if st.button("Salvar Tipo"):
        session.add(models.TipoArquivo(nome=nome))
        session.commit()
        st.rerun()

    st.subheader("Tipos cadastrados")

    h1, h2, h3 = st.columns([1,5,2])
    h1.markdown("**ID**")
    h2.markdown("**Nome**")
    h3.markdown("**Ações**")

    for t in session.query(models.TipoArquivo).all():
        col1, col2, col3 = st.columns([1,5,2])
        col1.write(t.id)
        col2.write(t.nome)

        if col3.button("Deletar", key=f"tipo_{t.id}"):
            session.delete(t)
            session.commit()
            st.rerun()