import streamlit as st
from database import SessionLocal
import models
import pandas as pd
from datetime import date
import os
import bcrypt
import time
from streamlit_option_menu import option_menu

if "logado" not in st.session_state:
    st.session_state.logado = False

session = SessionLocal()

st.set_page_config(layout="wide")

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

# ==========================
# LOGIN
# ==========================
if not st.session_state.logado:
    st.title("🔐 Login")

    username = st.text_input("Usuário")
    senha = st.text_input("Senha", type="password")

    if st.button("Entrar"):
        user = session.query(models.Usuario).filter_by(
            username=username
        ).first()

        if user and bcrypt.checkpw(
            senha.encode(),
            user.senha_hash.encode()
        ):
            st.session_state.logado = True
            st.session_state.usuario_id = user.id
            st.success("Login realizado com sucesso!")
            st.rerun()
        else:
            st.error("Usuário ou senha inválidos")

    st.stop()

if st.button("🚪 Sair"):
    st.session_state.clear()
    st.rerun()

# ==========================
# SESSÃO
# ==========================
if "last_activity" not in st.session_state:
    st.session_state.last_activity = time.time()

if time.time() - st.session_state.last_activity > 1800:
    st.session_state.clear()
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
            "Recurso": c.recurso.nome if c.recurso else "-",
            "Etapa": c.etapa.nome if c.etapa else "Não definido",
            "Pago": valor_pago
        })

        if saldo > 0:
            data_saldo.append({
                "Categoria": c.categoria.nome if c.categoria else "-",
                "Saldo": saldo
            })

    # ==========================
    # CÁLCULOS GERAIS
    # ==========================
    meta_lucro = total_pago_geral * 0.3
    valor_venda_total = total_pago_geral + meta_lucro

    unidades = projeto_filtro.quantidade_unidades or 0

    if unidades > 0:
        custo_por_unidade = total_pago_geral / unidades
        venda_por_unidade = valor_venda_total / unidades
    else:
        custo_por_unidade = 0
        venda_por_unidade = 0

    # ==========================
    # KPIs
    # ==========================
    col1, col2, col3, col4, col5 = st.columns(5)

    col1.metric("💰 Total Pago", f"R$ {total_pago_geral:,.2f}")
    col2.metric("📈 Lucro (30%)", f"R$ {meta_lucro:,.2f}")
    col3.metric("🏷️ Venda Total", f"R$ {valor_venda_total:,.2f}")
    col4.metric("📦 Custo por Unidade", f"R$ {custo_por_unidade:,.2f}")
    col5.metric("🏠 Venda por Unidade", f"R$ {venda_por_unidade:,.2f}")

    st.divider()

    # ==========================
    # PAGAMENTOS POR CATEGORIA (PIZZA INTERATIVA CORRIGIDA)
    # ==========================
    if data_pago:
        import plotly.express as px
        from streamlit_plotly_events import plotly_events

        df_pago = pd.DataFrame(data_pago)

        resumo_pago = (
            df_pago.groupby("Categoria", as_index=False)["Pago"]
            .sum()
            .sort_values("Pago", ascending=False)
            .reset_index(drop=True)  # 🔥 IMPORTANTE
        ) 

        resumo_pago["Percentual"] = (
            resumo_pago["Pago"] / resumo_pago["Pago"].sum() * 100
        )

        st.subheader("💰 Distribuição de Pagamentos por Categoria")

        # ==========================
        # SESSION STATE
        # ==========================
        if "categoria_click" not in st.session_state:
            st.session_state.categoria_click = None

        # ==========================
        # GRÁFICO (CLARO E BONITO)
        # ==========================
        fig = px.pie(
            resumo_pago,
            values="Pago",
            names="Categoria",
            hole=0.3  # estilo donut (opcional)
        )

        fig.update_layout(
            template="plotly_white"  # 🔥 resolve gráfico escuro
        )

        # ==========================
        # EVENTO DE CLIQUE
        # ==========================
        selected = plotly_events(
            fig,
            click_event=True,
            hover_event=False,
            key="pizza_pagamentos"
        )

        # ❗ NÃO usar st.plotly_chart aqui (evita duplicação)

        # ==========================
        # CAPTURA CLIQUE (CORRETO)
        # ==========================
        if selected:
            index = selected[0]["pointNumber"]  # 🔥 CORRETO
            categoria = resumo_pago.iloc[index]["Categoria"]
            st.session_state.categoria_click = categoria

        # ==========================
        # FILTRO VISUAL
        # ==========================
        col1, col2 = st.columns([4, 1])

        if st.session_state.categoria_click:
            col1.info(f"📌 Filtrando por: {st.session_state.categoria_click}")

            if col2.button("❌ Limpar filtro"):
                st.session_state.categoria_click = None
                st.rerun()

        # ==========================
        # TABELA ORDENADA (DO JEITO CERTO)
        # ==========================
        st.subheader("📄 Detalhamento de Pagamentos")

        df_detalhe = df_pago.copy()

        if st.session_state.categoria_click:
            df_detalhe = df_detalhe[
                df_detalhe["Categoria"] == st.session_state.categoria_click
            ]

        # 🔥 ORDENAÇÃO POR CATEGORIA + VALOR
        df_detalhe = df_detalhe.sort_values(
            by=["Categoria", "Pago"],
            ascending=[True, False]
        )

        st.dataframe(
            df_detalhe[["Categoria", "Recurso", "Pago"]],
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

        # tabela filtrada por etapa
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
            df_detalhe[["Etapa", "Categoria", "Recurso", "Pago"]],
            use_container_width=True
        )
    else:
        st.info("Sem dados para etapas.")

    # ==========================
    # SALDO (PIZZA)
    # ==========================
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

        # calcula percentual
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
        st.dataframe(df_saldo, use_container_width=True)

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
        st.session_state.projeto_arquivos_id is None
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
                    quantidade_unidades=quantidade_unidades
                ))
                session.commit()
                st.success("Projeto cadastrado com sucesso!")
                st.rerun()

        # ==========================
        # LISTAGEM
        # ==========================
        st.subheader("Projetos cadastrados")

        h1, h2, h3, h4, h5, h6, h7, h8 = st.columns([3,2,2,3,2,2,2,2])
        h1.markdown("**Nome**")
        h2.markdown("**Período**")
        h3.markdown("**Endereço**")
        h4.markdown("**Unidades**")
        h5.markdown("**Lançamentos**")
        h6.markdown("**Arquivos**")
        h7.markdown("**Editar**")
        h8.markdown("**Excluir**")

        for p in session.query(models.Projeto).all():
            col1, col2, col3, col4, col5, col6, col7, col8 = st.columns([3,2,2,3,2,2,2,2])

            col1.write(p.nome)
            col2.write(f"{p.data_inicio} até {p.data_fim}" if p.data_fim else f"{p.data_inicio}")
            col3.write(p.endereco)
            col4.write(p.quantidade_unidades or 0)

            if col5.button("Lançamentos", key=f"custos_projeto_{p.id}"):
                st.session_state.projeto_custos_id = p.id
                st.rerun()

            if col6.button("Arquivos", key=f"arquivos_projeto_{p.id}"):
                st.session_state.projeto_arquivos_id = p.id
                st.rerun()

            if col7.button("Editar", key=f"editar_projeto_{p.id}"):
                st.session_state.editar_projeto_id = p.id
                st.rerun()

            if col8.button("Deletar", key=f"deletar_projeto_{p.id}"):
                session.delete(p)
                session.commit()
                st.success("Projeto deletado com sucesso!")
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
        recursos = session.query(models.Recurso).all()
        etapas = session.query(models.EtapaObra).all()

        # ==========================
        # FORMULÁRIO (NOVO / EDIÇÃO)
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

            recurso = st.selectbox(
                "Recurso",
                recursos,
                index=recursos.index(lancamento.recurso),
                format_func=lambda x: x.nome
            )

            etapa = st.selectbox(
                "Etapa da Obra",
                etapas,
                index=etapas.index(lancamento.etapa) if lancamento.etapa in etapas else 0,
                format_func=lambda x: x.nome
            )

            descricao = st.text_input("Descrição", value=lancamento.descricao)

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

            data_custo = st.date_input("Data", value=lancamento.data)

            col1, col2 = st.columns(2)

            if col1.button("Atualizar Lançamento"):
                lancamento.categoria_id = categoria.id
                lancamento.recurso_id = recurso.id
                lancamento.descricao = descricao
                lancamento.valor_previsto = valor_previsto
                lancamento.valor_pago = valor_pago
                lancamento.data = data_custo
                lancamento.quantidade = quantidade
                lancamento.valor_unitario = valor_unitario
                lancamento.valor_previsto = valor_previsto
                lancamento.etapa_id = etapa.id if etapa else None

                session.commit()
                st.session_state.editar_lancamento_id = None
                st.success("Lançamento atualizado com sucesso!")
                st.rerun()

            if col2.button("Cancelar Edição"):
                st.session_state.editar_lancamento_id = None
                st.rerun()

        else:
            st.subheader("➕ Novo Lançamento")

            categoria = st.selectbox(
                "Categoria",
                categorias,
                format_func=lambda x: x.nome
            )

            recurso = st.selectbox(
                "Recurso",
                recursos,
                format_func=lambda x: x.nome
            )

            descricao = st.text_input("Descrição")

            col1, col2 = st.columns(2)

            quantidade = col1.number_input("Quantidade", min_value=0.0, value=1.0)
            valor_unitario = col2.number_input("Valor Unitário", min_value=0.0, value=0.0)

            valor_pago = st.number_input("Valor Pago", min_value=0.0, value=0.0)

            data_custo = st.date_input("Data", value=date.today())

            valor_previsto_calculado = quantidade * valor_unitario

            etapa = st.selectbox(
                "Etapa da Obra",
                etapas,
                format_func=lambda x: x.nome
            )

            st.info(f"💰 Total Previsto: R$ {valor_previsto_calculado:,.2f}")

            if st.button("Salvar Lançamento"):
                session.add(models.Custo(
                    descricao=descricao,
                    quantidade=quantidade,
                    valor_unitario=valor_unitario,
                    valor_previsto=valor_previsto_calculado,
                    valor_pago=valor_pago,
                    data=data_custo,
                    projeto_id=projeto.id,
                    categoria_id=categoria.id,
                    recurso_id=recurso.id,
                    etapa_id=etapa.id if etapa else None   # 🔥 FALTAVA ISSO
                ))

                session.commit()
                st.success("Lançamento salvo com sucesso!")
                st.rerun()

        # ==========================
        # LISTAGEM COM HEADER + FILTRO
        # ==========================
        st.subheader("Lançamentos cadastrados")

        # 🔎 FILTRO
        filtro = st.text_input("🔎 Buscar por descrição ou material")

        lancamentos = session.query(models.Custo).filter(
            models.Custo.projeto_id == projeto.id
        ).all()

        # 🔥 APLICA FILTRO
        if filtro:
            filtro_lower = filtro.lower()

            lancamentos = [
                c for c in lancamentos
                if (
                    (c.descricao and filtro_lower in c.descricao.lower()) or
                    (c.recurso and c.recurso.nome and filtro_lower in c.recurso.nome.lower())
                )
            ]

        # ==========================
        # EXPORTAÇÃO CSV
        # ==========================
        if lancamentos:
            data_export = []

            for c in lancamentos:
                data_export.append({
                    "ID": c.id,
                    "Descricao": c.descricao,
                    "Categoria": c.categoria.nome if c.categoria else "-",
                    "Recurso": c.recurso.nome if c.recurso else "-",
                    "Valor Previsto": float(c.total_previsto),
                    "Valor Pago": float(c.valor_pago or 0),
                    "Quantidade": float(c.quantidade or 0),
                    "Valor Unitario": float(c.valor_unitario or 0),
                    "Data": c.data,
                    "Etapa": c.etapa.nome if c.etapa else "-",
                })

            df_export = pd.DataFrame(data_export)

            csv = df_export.to_csv(index=False, sep=";").encode("utf-8")

            st.download_button(
                label="📥 Exportar CSV",
                data=csv,
                file_name=f"lancamentos_projeto_{projeto.id}.csv",
                mime="text/csv"
            )

        # HEADER (AGORA COM ID)
        h0, h1, h2, h3, h4, h5, h6, h7, h8, h9 = st.columns([1,3,2,2,2,2,2,2,2,2])

        h0.markdown("**ID**")
        h1.markdown("**Descrição**")
        h2.markdown("**Categoria**")
        h3.markdown("**Recurso**")
        h4.markdown("**Etapa**")
        h5.markdown("**Previsto**")
        h6.markdown("**Pago**")
        h7.markdown("**Qtd**")
        h8.markdown("**Editar**")
        h9.markdown("**Excluir**")

        # LISTAGEM
        if not lancamentos:
            st.info("Nenhum lançamento encontrado.")
        else:
            for c in lancamentos:
                valor_previsto = float(c.total_previsto)
                valor_pago = float(c.valor_pago or 0)
                valor_unitario = float(c.valor_unitario or 0)
                quantidade = float(c.quantidade or 0)

                col0, col1, col2, col3, col4, col5, col6, col7, col8, col9 = st.columns([1,3,2,2,2,2,2,2,2,2])

                col0.write(c.id)
                col1.write(c.descricao or "-")
                col2.write(c.categoria.nome if c.categoria else "-")
                col3.write(c.recurso.nome if c.recurso else "-")
                col4.write(c.etapa.nome if c.etapa else "-")  # 🔥 NOVO
                col5.write(f"R$ {valor_previsto:,.2f}")
                col6.write(f"R$ {valor_pago:,.2f}")
                col7.write(quantidade)

                if col8.button("Editar", key=f"editar_lancamento_{c.id}"):
                    st.session_state.editar_lancamento_id = c.id
                    st.rerun()

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