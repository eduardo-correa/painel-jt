import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os

# 1. Page Configuration (Must be the first Streamlit command)
st.set_page_config(
    page_title="Painel Estatístico da Justiça do Trabalho",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Regional TRT Headquarters/States Mapping
REGIOES_MAP = {
    "01ª Região": "01ª Região (RJ)",
    "02ª Região": "02ª Região (SP Capital)",
    "03ª Região": "03ª Região (MG)",
    "04ª Região": "04ª Região (RS)",
    "05ª Região": "05ª Região (BA)",
    "06ª Região": "06ª Região (PE)",
    "07ª Região": "07ª Região (CE)",
    "08ª Região": "08ª Região (PA/AP)",
    "09ª Região": "09ª Região (PR)",
    "10ª Região": "10ª Região (DF/TO)",
    "11ª Região": "11ª Região (AM/RR)",
    "12ª Região": "12ª Região (SC)",
    "13ª Região": "13ª Região (PB)",
    "14ª Região": "14ª Região (RO/AC)",
    "15ª Região": "15ª Região (SP Interior)",
    "16ª Região": "16ª Região (MA)",
    "17ª Região": "17ª Região (ES)",
    "18ª Região": "18ª Região (GO)",
    "19ª Região": "19ª Região (AL)",
    "20ª Região": "20ª Região (SE)",
    "21ª Região": "21ª Região (RN)",
    "22ª Região": "22ª Região (PI)",
    "23ª Região": "23ª Região (MT)",
    "24ª Região": "24ª Região (MS)",
    "TST (Nacional)": "TST (Nacional)",
}


# 2. Cache Data Loading
@st.cache_data
def load_data():
    parquet_path = "data/Base_de_Dados_JT_Historico_Limpa.parquet"
    if not os.path.exists(parquet_path):
        # Fallback to CSV if parquet is not found
        csv_path = "data/Base de Dados JT Historico - CSV.csv"
        df = pd.read_csv(csv_path, sep=";", encoding="latin1", low_memory=False)
        # Quick inline cleanup
        df = df[["Variavel", "Ano", "Instancia", "Regiao Judiciaria", "Quantidade"]]
        df = df.dropna(subset=["Variavel", "Ano", "Instancia", "Quantidade"])
        df["Variavel"] = (
            df["Variavel"]
            .astype(str)
            .str.strip()
            .replace(
                {"Arrecada  o": "Arrecadação", "Res duo": "Resíduo", "Tempo M dio": "Tempo Médio"}
            )
        )
        df.loc[df["Instancia"] == "TST", "Regiao Judiciaria"] = df.loc[
            df["Instancia"] == "TST", "Regiao Judiciaria"
        ].fillna("TST (Nacional)")
        df = df.dropna(subset=["Regiao Judiciaria"])
        df["Quantidade"] = pd.to_numeric(
            df["Quantidade"]
            .astype(str)
            .str.replace(".", "", regex=False)
            .str.replace(",", ".", regex=False),
            errors="coerce",
        )
        df = df.dropna(subset=["Quantidade"])
        df["Quantidade"] = df["Quantidade"].round().astype(int)
        df["Ano"] = df["Ano"].astype(int)
        return df

    df = pd.read_parquet(parquet_path)
    return df


df_raw = load_data()

# Apply the mapping for display purposes
df_display = df_raw.copy()
df_display["Regiao_Display"] = (
    df_display["Regiao Judiciaria"].map(REGIOES_MAP).fillna(df_display["Regiao Judiciaria"])
)

# 3. Theme Configuration (Modern Pastel Tones)
LIGHT_THEME = {
    "bg": "#F8F9FA",
    "card_bg": "#FFFFFF",
    "sidebar_bg": "#F1F3F5",
    "text": "#212529",
    "text_muted": "#6C757D",
    "border": "#E2E8F0",
    "grid": "#E9ECEF",
    "primary": "#4EA8DE",  # Pastel Blue
    "accent": "#72EFDD",  # Pastel Teal
    "success": "#A7C957",  # Pastel Green
    "warning": "#F4A261",  # Pastel Peach
    "danger": "#E63946",  # Pastel Red
    # Pastel palette for charts
    "colors": [
        "#A8DADC",
        "#4EA8DE",
        "#BDB2FF",
        "#FFC6FF",
        "#FFD166",
        "#CAFFBF",
        "#FFADAD",
        "#9BF6FF",
        "#E9C46A",
        "#F4A261",
    ],
}

DARK_THEME = {
    "bg": "#0F172A",  # Tailwind Slate-900
    "card_bg": "#1E293B",  # Tailwind Slate-800
    "sidebar_bg": "#111827",  # Tailwind Gray-900
    "text": "#F1F5F9",
    "text_muted": "#94A3B8",
    "border": "#334155",
    "grid": "#334155",
    "primary": "#56CFE1",  # Pastel Cyan
    "accent": "#72EFDD",  # Pastel Teal
    "success": "#A7C957",
    "warning": "#F4A261",
    "danger": "#E63946",
    # Pastel palette for charts
    "colors": [
        "#83C5BE",
        "#4EA8DE",
        "#BDB2FF",
        "#FFC6FF",
        "#FFD166",
        "#CAFFBF",
        "#FFADAD",
        "#9BF6FF",
        "#E9C46A",
        "#F4A261",
    ],
}

# Theme selection in Sidebar
# st.sidebar.markdown("### Tema do painel")
theme_choice = st.sidebar.radio("Tema do painel:", ["Claro", "Escuro"], index=0, horizontal=True)

# Select active theme parameters
theme = LIGHT_THEME if theme_choice == "Claro" else DARK_THEME

# Inject Custom CSS for themes (including card transitions, fonts, and scrollbars)
theme_css = f"""
<style>
    /* Main Layout */
    .stApp {{
        background-color: {theme["bg"]} !important;
        color: {theme["text"]} !important;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif !important;
    }}

    /* Sidebar styling */
    [data-testid="stSidebar"] {{
        background-color: {theme["sidebar_bg"]} !important;
        border-right: 1px solid {theme["border"]} !important;
    }}

    /* Custom Card Style with Glassmorphism & Hover Animations */
    .custom-card {{
        background-color: {theme["card_bg"]} !important;
        border: 1px solid {theme["border"]} !important;
        border-radius: 16px !important;
        padding: 24px !important;
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.05), 0 4px 6px -2px rgba(0, 0, 0, 0.02) !important;
        margin-bottom: 20px !important;
        transition: transform 0.3s cubic-bezier(0.4, 0, 0.2, 1), box-shadow 0.3s ease !important;
    }}

    .custom-card:hover {{
        transform: translateY(-4px) !important;
        box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04) !important;
    }}

    /* KPI Typography */
    .kpi-title {{
        font-size: 13px !important;
        font-weight: 600 !important;
        color: {theme["text_muted"]} !important;
        text-transform: uppercase !important;
        letter-spacing: 0.1em !important;
        margin-bottom: 8px !important;
    }}

    .kpi-value {{
        font-size: 32px !important;
        font-weight: 700 !important;
        color: {theme["text"]} !important;
        margin: 0 !important;
    }}

    .kpi-delta {{
        font-size: 12px !important;
        font-weight: 600 !important;
        margin-top: 6px !important;
        display: inline-block !important;
    }}

    .kpi-delta-up {{
        color: #2D6A4F !important;
    }}

    .kpi-delta-down {{
        color: #B7094C !important;
    }}

    /* Headers and Tabs */
    h1, h2, h3, h4, h5, h6 {{
        color: {theme["text"]} !important;
        font-weight: 700 !important;
    }}

    .stTabs [data-baseweb="tab-list"] {{
        background-color: {theme["sidebar_bg"]} !important;
        border-radius: 12px !important;
        padding: 5px !important;
        border: 1px solid {theme["border"]} !important;
    }}

    .stTabs [data-baseweb="tab"] {{
        color: {theme["text_muted"]} !important;
        border-radius: 8px !important;
        padding: 8px 16px !important;
        transition: all 0.2s ease !important;
    }}

    .stTabs [data-baseweb="tab"][aria-selected="true"] {{
        background-color: {theme["card_bg"]} !important;
        color: {theme["primary"]} !important;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05) !important;
        font-weight: 600 !important;
    }}
</style>
"""
st.markdown(theme_css, unsafe_allow_html=True)

# 4. Sidebar Navigation & Filters
# st.sidebar.image("https://img.icons8.com/pastel-glyph/128/scale.png", width=70)
st.sidebar.title("Filtros de Análise")

# Reset Filter Button
if st.sidebar.button("🧹 Limpar Filtros"):
    st.session_state.clear()
    st.rerun()

# 4.1 Filter by Year
min_year = int(df_display["Ano"].min())
max_year = int(df_display["Ano"].max())

st.sidebar.subheader("📅 Período")
year_range = st.sidebar.slider(
    "Selecione o intervalo de anos:",
    min_value=min_year,
    max_value=max_year,
    value=(2015, 2026),
    step=1,
)

# 4.2 Filter by Instance
st.sidebar.subheader("🏢 Instância")
instances = sorted(df_display["Instancia"].unique())
selected_instances = st.sidebar.multiselect(
    "Selecione as instâncias:", options=instances, default=instances
)

# 4.3 Filter by Judicial Region
st.sidebar.subheader("📍 Região Judiciária (TRT)")
# Get available regions based on selected instances to keep it dynamic
if selected_instances:
    available_regions = sorted(
        df_display[df_display["Instancia"].isin(selected_instances)]["Regiao_Display"].unique()
    )
else:
    available_regions = sorted(df_display["Regiao_Display"].unique())

select_all_regions = st.sidebar.checkbox("Selecionar todas as regiões", value=True)

if select_all_regions:
    selected_regions = available_regions
else:
    selected_regions = st.sidebar.multiselect(
        "Selecione as regiões judiciárias:",
        options=available_regions,
        default=available_regions[:3],
    )

# 4.4 Primary Indicator Selector
st.sidebar.subheader("📊 Indicador de Análise")
variables = sorted(df_display["Variavel"].unique())
# Put Casos Novos first if available, otherwise just use sorted order
default_idx = variables.index("Casos Novos") if "Casos Novos" in variables else 0
primary_variable = st.sidebar.selectbox(
    "Escolha o indicador principal para detalhamento:", options=variables, index=default_idx
)

# 5. Data Filtering
df_filtered = df_display[
    (df_display["Ano"] >= year_range[0])
    & (df_display["Ano"] <= year_range[1])
    & (df_display["Instancia"].isin(selected_instances))
    & (df_display["Regiao_Display"].isin(selected_regions))
]

# Safeguard if no data is available with current filters
if df_filtered.empty:
    st.warning(
        "⚠️ Nossos dados estão vazios com os filtros aplicados. Ajuste os filtros na barra lateral para ver os dados."
    )
    st.stop()


# Helper function to format numbers dynamically as integer process count
def format_num(val, var_name=None):
    return f"{int(val):,}".replace(",", ".")


# Helper to calculate KPI and percentage change compared to the previous period of same duration
def calculate_kpi(variable, df_all, years):
    current_years = list(range(years[0], years[1] + 1))
    duration = len(current_years)
    prev_years = list(range(years[0] - duration, years[0]))

    # Current value
    current_val = df_all[(df_all["Ano"].isin(current_years)) & (df_all["Variavel"] == variable)][
        "Quantidade"
    ].sum()

    # Previous value
    prev_val = df_all[(df_all["Ano"].isin(prev_years)) & (df_all["Variavel"] == variable)][
        "Quantidade"
    ].sum()

    if prev_val > 0:
        pct_change = ((current_val - prev_val) / prev_val) * 100
        delta_str = f"{pct_change:+.1f}% vs período anterior"
        is_positive = pct_change >= 0
    else:
        delta_str = "Série anterior indisponível"
        is_positive = True

    return current_val, delta_str, is_positive


# Helper to apply standard Plotly pastel styling based on current theme
def apply_plotly_theme(fig):
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font_color=theme["text"],
        font_family="Inter, sans-serif",
        margin=dict(l=40, r=40, t=50, b=40),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        xaxis=dict(gridcolor=theme["grid"], linecolor=theme["border"], zerolinecolor=theme["grid"]),
        yaxis=dict(gridcolor=theme["grid"], linecolor=theme["border"], zerolinecolor=theme["grid"]),
    )


# 6. Main Dashboard Interface
st.title("⚖️ Painel Estatístico da Justiça do Trabalho")
st.markdown(
    f"Análise histórica da quantidade de processos trabalhistas no Brasil de **{year_range[0]}** a **{year_range[1]}**."
)

# 6.1 KPI Cards Row
st.write("")  # Spacer

# Filter data ignoring Year for KPI calculations
df_kpi_filtered = df_display[
    (df_display["Instancia"].isin(selected_instances))
    & (df_display["Regiao_Display"].isin(selected_regions))
]

kpi_vars = ["Casos Novos", "Julgados", "Iniciadas", "Encerradas"]
kpi_cols = st.columns(4)

for idx, var in enumerate(kpi_vars):
    val, delta, is_pos = calculate_kpi(var, df_kpi_filtered, year_range)
    val_formatted = format_num(val, var)

    # Format Delta Color
    delta_class = "kpi-delta-up" if is_pos else "kpi-delta-down"
    delta_icon = "📈" if is_pos else "📉"

    delta_html = (
        f'<span class="kpi-delta {delta_class}">{delta_icon} {delta}</span>'
        if delta != "Série anterior indisponível"
        else f'<span class="kpi-delta" style="color: {theme["text_muted"]}">{delta}</span>'
    )

    # Custom HTML Card injection
    kpi_cols[idx].markdown(
        f"""
        <div class="custom-card">
            <div class="kpi-title">{var}</div>
            <div class="kpi-value">{val_formatted}</div>
            {delta_html}
        </div>
        """,
        unsafe_allow_html=True,
    )

# 6.2 Tabs Section
tab_overview, tab_geography, tab_instance, tab_data = st.tabs(
    [
        "Panorama Geral",
        "Análise Regional (TRTs)",
        "Análise por Instância",
        "Consulta de Dados",
    ]
)

# ----------------- TAB 1: PANORAMA GERAL -----------------
with tab_overview:
    st.subheader("Tendência Histórica dos Processos")

    # Group processes (Casos Novos and Julgados) by Year
    df_proc_trend = (
        df_filtered[df_filtered["Variavel"].isin(["Casos Novos", "Julgados"])]
        .groupby(["Ano", "Variavel"])["Quantidade"]
        .sum()
        .reset_index()
    )

    if not df_proc_trend.empty:
        fig_proc = px.line(
            df_proc_trend,
            x="Ano",
            y="Quantidade",
            color="Variavel",
            color_discrete_sequence=[
                theme["colors"][1],
                theme["colors"][4],
            ],  # Pastel Blue & Yellow
            markers=True,
            title="Evolução de Casos Novos vs. Processos Julgados (Quantidade)",
        )
        fig_proc.update_traces(line=dict(width=3.5), marker=dict(size=8))
        apply_plotly_theme(fig_proc)
        fig_proc.update_layout(yaxis_title="Quantidade de Processos")
        st.plotly_chart(fig_proc, width="stretch")
    else:
        st.info("Dados de Casos Novos ou Julgados não disponíveis para os filtros selecionados.")

    # Flow Trends: Iniciadas vs Encerradas
    st.subheader("Evolução de Processos Iniciados vs. Encerrados")
    df_flow_trend = (
        df_filtered[df_filtered["Variavel"].isin(["Iniciadas", "Encerradas"])]
        .groupby(["Ano", "Variavel"])["Quantidade"]
        .sum()
        .reset_index()
    )

    if not df_flow_trend.empty:
        fig_flow = px.bar(
            df_flow_trend,
            x="Ano",
            y="Quantidade",
            color="Variavel",
            barmode="group",
            color_discrete_sequence=[theme["colors"][5], theme["colors"][0]],  # Pastel Green & Teal
            title="Comparativo Anual de Processos Iniciados vs. Encerrados",
        )
        apply_plotly_theme(fig_flow)
        fig_flow.update_layout(yaxis_title="Quantidade de Processos")
        st.plotly_chart(fig_flow, width="stretch")
    else:
        st.info(
            "Dados de Processos Iniciados ou Encerrados não disponíveis para os filtros selecionados."
        )

# ----------------- TAB 2: ANÁLISE REGIONAL -----------------
with tab_geography:
    st.subheader(f"Distribuição Regional do Indicador: {primary_variable}")
    st.markdown(
        "Comparativo do volume de processos entre os Tribunais Regionais do Trabalho (TRTs)."
    )

    # Filter by selected primary variable
    df_geo_var = df_filtered[df_filtered["Variavel"] == primary_variable]

    if not df_geo_var.empty:
        # Group by Region
        df_geo_group = (
            df_geo_var.groupby("Regiao_Display")["Quantidade"]
            .sum()
            .reset_index()
            .sort_values("Quantidade", ascending=True)
        )

        col_chart, col_stats = st.columns([2, 1])

        with col_chart:
            fig_geo = px.bar(
                df_geo_group,
                y="Regiao_Display",
                x="Quantidade",
                orientation="h",
                color="Quantidade",
                color_continuous_scale=px.colors.sequential.Tealgrn
                if theme_choice == "Claro"
                else px.colors.sequential.Mint,
                title=f"Quantidade de Processos ({primary_variable}) por TRT (Acumulado)",
            )
            apply_plotly_theme(fig_geo)
            fig_geo.update_layout(
                coloraxis_showscale=False,
                yaxis_title="Tribunal Regional (TRT)",
                xaxis_title="Quantidade de Processos",
            )
            st.plotly_chart(fig_geo, width="stretch")

        with col_stats:
            st.markdown("#### 🏆 Ranking de Regiões")
            # Show a clean table of Top Regions
            df_geo_table = df_geo_group.sort_values("Quantidade", ascending=False).copy()
            df_geo_table["Quantidade Formatada"] = df_geo_table.apply(
                lambda row: format_num(row["Quantidade"]), axis=1
            )
            df_geo_table.columns = ["Região", "Quantidade Bruta", "Processos Consolidados"]

            st.dataframe(
                df_geo_table[["Região", "Processos Consolidados"]].reset_index(drop=True),
                width="stretch",
                height=400,
            )
    else:
        st.info(
            f"Sem dados disponíveis para a variável '{primary_variable}' no período/filtros selecionados."
        )

# ----------------- TAB 3: ANÁLISE POR INSTÂNCIA -----------------
with tab_instance:
    st.subheader("Distribuição por Instância do Poder Judiciário")
    st.markdown(
        "Comparação do volume de processos entre a 1ª Instância (Varas do Trabalho), 2ª Instância (TRTs) e TST (Tribunal Superior do Trabalho)."
    )

    df_inst_var = df_filtered[df_filtered["Variavel"] == primary_variable]

    if not df_inst_var.empty:
        df_inst_group = df_inst_var.groupby("Instancia")["Quantidade"].sum().reset_index()

        col_pie, col_inst_trend = st.columns([1, 2])

        with col_pie:
            fig_pie = px.pie(
                df_inst_group,
                names="Instancia",
                values="Quantidade",
                hole=0.4,
                color_discrete_sequence=[
                    theme["colors"][1],
                    theme["colors"][2],
                    theme["colors"][6],
                ],
                title=f"Divisão de {primary_variable}",
            )
            apply_plotly_theme(fig_pie)
            st.plotly_chart(fig_pie, width="stretch")

        with col_inst_trend:
            # Instance evolution over time
            df_inst_time = (
                df_inst_var.groupby(["Ano", "Instancia"])["Quantidade"].sum().reset_index()
            )
            fig_inst_time = px.bar(
                df_inst_time,
                x="Ano",
                y="Quantidade",
                color="Instancia",
                color_discrete_sequence=[
                    theme["colors"][1],
                    theme["colors"][2],
                    theme["colors"][6],
                ],
                title=f"Histórico de {primary_variable} por Instância",
            )
            apply_plotly_theme(fig_inst_time)
            fig_inst_time.update_layout(yaxis_title="Quantidade de Processos")
            st.plotly_chart(fig_inst_time, width="stretch")

        # Summary statistics
        st.markdown("#### 📈 Detalhamento por Instância")
        df_inst_details = (
            df_inst_time.pivot(index="Ano", columns="Instancia", values="Quantidade")
            .fillna(0)
            .astype(int)
        )
        st.dataframe(df_inst_details, width="stretch")
    else:
        st.info(f"Sem dados de instâncias para a variável '{primary_variable}'.")

# ----------------- TAB 4: CONSULTA DE DADOS -----------------
with tab_data:
    st.subheader("Pesquisa e Filtro de Dados Brutos")
    st.markdown(
        "Explore, faça buscas textuais e exporte os dados consolidados da Justiça do Trabalho."
    )

    # Custom Search Input
    search_term = st.text_input("🔍 Buscar por variável ou instância:", "")

    df_search = df_filtered.copy()
    if search_term:
        df_search = df_search[
            df_search["Variavel"].str.contains(search_term, case=False, na=False)
            | df_search["Instancia"].str.contains(search_term, case=False, na=False)
            | df_search["Regiao_Display"].str.contains(search_term, case=False, na=False)
        ]

    # Clean output columns
    df_search_disp = df_search[
        ["Variavel", "Ano", "Instancia", "Regiao_Display", "Quantidade"]
    ].copy()
    df_search_disp.columns = [
        "Variável",
        "Ano",
        "Instância",
        "Região Judiciária",
        "Quantidade de Processos",
    ]

    st.write(f"Exibindo **{len(df_search_disp):,}** registros baseados nos filtros e busca.")

    # Render Dataframe
    st.dataframe(df_search_disp.reset_index(drop=True), width="stretch", height=450)

    # Download Button
    csv = df_search_disp.to_csv(index=False, encoding="utf-8-sig")
    st.download_button(
        label="📥 Baixar Dados em CSV",
        data=csv,
        file_name="dados_justica_trabalho_filtrados.csv",
        mime="text/csv",
    )

# 7. Sidebar Footer Info
st.sidebar.write("---")
st.sidebar.markdown(
    f"""
    <div style="font-size: 11px; color: {theme["text_muted"]}; text-align: center;">
        Base de dados histórica da Justiça do Trabalho<br>
        Os dados podem ser obtidos <a href="https://www.tst.jus.br/documents/d/estatistica/base_de_dados_jt_historico_final-zip">aqui</a><br>
        <b>Versão 1.0.1</b>
    </div>
    """,
    unsafe_allow_html=True,
)
