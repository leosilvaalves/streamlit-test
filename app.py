import os
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import date, timedelta
import random

# ---------------------------------------------------------------------------
# Configuração da página
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------------------------------------------------------------------------
# Versão do sistema — variável sensível
# Lida via st.secrets (local: .streamlit/secrets.toml, nuvem: Secrets do Streamlit Cloud)
# Fallback para variável de ambiente caso secrets não esteja configurado
# ---------------------------------------------------------------------------
def get_app_version() -> str:
    try:
        return st.secrets["APP_VERSION"]
    except (KeyError, FileNotFoundError):
        return os.environ.get("APP_VERSION", "N/A")


APP_VERSION = get_app_version()

# ---------------------------------------------------------------------------
# Dados de exemplo
# ---------------------------------------------------------------------------
@st.cache_data
def load_sample_data() -> pd.DataFrame:
    random.seed(42)
    today = date.today()
    dates = [today - timedelta(days=i) for i in range(29, -1, -1)]
    categorias = ["Produto A", "Produto B", "Produto C"]
    rows = []
    for d in dates:
        for cat in categorias:
            rows.append({
                "data": d,
                "categoria": cat,
                "vendas": random.randint(50, 300),
                "receita": round(random.uniform(1000, 8000), 2),
            })
    return pd.DataFrame(rows)


df = load_sample_data()

# ---------------------------------------------------------------------------
# Sidebar
# ---------------------------------------------------------------------------
with st.sidebar:
    st.title("📊 Dashboard")
    st.markdown("---")

    pagina = st.radio(
        "Navegação",
        ["Visão Geral", "Vendas por Categoria", "Dados Brutos"],
    )

    st.markdown("---")
    st.markdown("**Filtros**")
    categorias_selecionadas = st.multiselect(
        "Categorias",
        options=df["categoria"].unique().tolist(),
        default=df["categoria"].unique().tolist(),
    )

# ---------------------------------------------------------------------------
# Filtragem
# ---------------------------------------------------------------------------
df_filtrado = df[df["categoria"].isin(categorias_selecionadas)] if categorias_selecionadas else df

# ---------------------------------------------------------------------------
# Páginas
# ---------------------------------------------------------------------------
if pagina == "Visão Geral":
    st.title("Visão Geral")

    col1, col2, col3 = st.columns(3)
    col1.metric("Total de Vendas", f"{df_filtrado['vendas'].sum():,}")
    col2.metric("Receita Total", f"R$ {df_filtrado['receita'].sum():,.2f}")
    col3.metric("Média Diária de Vendas", f"{df_filtrado.groupby('data')['vendas'].sum().mean():.0f}")

    st.markdown("---")

    vendas_por_dia = (
        df_filtrado.groupby("data")["vendas"].sum().reset_index()
    )
    fig = px.line(
        vendas_por_dia,
        x="data",
        y="vendas",
        title="Vendas nos Últimos 30 Dias",
        labels={"data": "Data", "vendas": "Unidades Vendidas"},
    )
    fig.update_layout(hovermode="x unified")
    st.plotly_chart(fig, use_container_width=True)

elif pagina == "Vendas por Categoria":
    st.title("Vendas por Categoria")

    col1, col2 = st.columns(2)

    with col1:
        por_cat = df_filtrado.groupby("categoria")["vendas"].sum().reset_index()
        fig_pie = px.pie(
            por_cat,
            names="categoria",
            values="vendas",
            title="Distribuição de Vendas",
        )
        st.plotly_chart(fig_pie, use_container_width=True)

    with col2:
        fig_bar = px.bar(
            df_filtrado.groupby(["data", "categoria"])["receita"].sum().reset_index(),
            x="data",
            y="receita",
            color="categoria",
            title="Receita Diária por Categoria",
            labels={"data": "Data", "receita": "Receita (R$)"},
            barmode="stack",
        )
        st.plotly_chart(fig_bar, use_container_width=True)

elif pagina == "Dados Brutos":
    st.title("Dados Brutos")
    st.dataframe(df_filtrado, use_container_width=True)
    csv = df_filtrado.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="Baixar CSV",
        data=csv,
        file_name="dados.csv",
        mime="text/csv",
    )

# ---------------------------------------------------------------------------
# Rodapé com versão do sistema
# ---------------------------------------------------------------------------
st.markdown("---")
st.caption(f"Sistema v{APP_VERSION} &nbsp;|&nbsp; Dashboard de Dados")
