import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# 1. CONFIGURACION DE LA PAGINA
st.set_page_config(
    page_title="Dashboard Mercado Laboral TIC",
    layout="wide"
)

st.title("Cuadro de Mando Integral - Mercado Laboral TIC Chile")
st.markdown("*Analisis de ofertas laborales: modalidad, jornada, categoria y perfil TIC*")
st.markdown("---")

# 2. CARGA DE DATOS
@st.cache_data
def cargar_datos():
    return pd.read_csv("datos_mercado_laboral_dashboard.csv")

df = cargar_datos()

# Aseguramos tipos correctos
df["es_ti"]     = df["es_ti"].astype(bool)
df["es_remoto"] = df["es_remoto"].astype(bool)

# 3. PESTANAS POR NIVEL ORGANIZACIONAL
tab_est, tab_tac, tab_op = st.tabs([
    "Nivel Estrategico (Director)",
    "Nivel Tactico (Gerente de Talento)",
    "Nivel Operacional (Analista)"
])

# =============================================================
# PESTANA 1: NIVEL ESTRATEGICO
# Indicador 1: Penetracion del sector TIC en el mercado laboral
# Indicador 2: Distribucion general de modalidad de trabajo
# Frecuencia: Mensual | Responsable: Direccion / CEO
# =============================================================
with tab_est:
    st.header("Penetracion del Sector TIC en el Mercado Laboral")
    st.caption("Frecuencia: Mensual | Objetivo: Evaluar el peso del sector TIC en la oferta laboral total")

    total    = len(df)
    n_ti     = df["es_ti"].sum()
    n_remoto = df["es_remoto"].sum()
    n_cats   = df["categoria"].nunique()

    # Metricas clave
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total ofertas", total)
    col2.metric("Ofertas TIC", int(n_ti), delta=f"{n_ti/total*100:.1f}% del total")
    col3.metric("Ofertas con trabajo remoto/hibrido", int(n_remoto), delta=f"{n_remoto/total*100:.1f}%")
    col4.metric("Categorias laborales", n_cats)

    st.markdown("---")

    colA, colB = st.columns(2)

    with colA:
        st.subheader("Modalidad de trabajo: TIC vs No TIC")
        st.caption("Pregunta: Las ofertas TIC tienen mayor flexibilidad de modalidad que las no-TIC?")

        # Bivariate: modalidad x es_ti
        df_mod_ti = (
            df.groupby(["es_ti", "modalidad"])
            .size()
            .reset_index(name="Cantidad")
        )
        df_mod_ti["Sector"] = df_mod_ti["es_ti"].map({True: "TIC", False: "No TIC"})
        pivot_mod = df_mod_ti.pivot_table(index="modalidad", columns="Sector", values="Cantidad", fill_value=0)
        pivot_mod_pct = pivot_mod.div(pivot_mod.sum(axis=0), axis=1) * 100

        fig1, ax1 = plt.subplots(figsize=(6, 4))
        pivot_mod_pct.plot(kind="bar", ax=ax1, color=["#B0BEC5", "#1565C0"], width=0.6)
        ax1.set_xlabel("")
        ax1.set_ylabel("% dentro de cada sector")
        ax1.set_title("Modalidad de trabajo: TIC vs No TIC (%)")
        ax1.legend(title="Sector")
        plt.xticks(rotation=20, ha="right")
        sns.despine(left=True)
        st.pyplot(fig1)

    with colB:
        st.subheader("Concentracion TIC por categoria")
        st.caption("Pregunta: Que categorias concentran las ofertas del sector TIC?")

        # Bivariate: categoria x es_ti (% TIC dentro de cada categoria)
        df_cat_ti = df.groupby("categoria")["es_ti"].agg(["sum", "count"]).reset_index()
        df_cat_ti.columns = ["Categoria", "TIC", "Total"]
        df_cat_ti["No_TIC"] = df_cat_ti["Total"] - df_cat_ti["TIC"]
        df_cat_ti["Pct_TIC"] = (df_cat_ti["TIC"] / df_cat_ti["Total"] * 100).round(1)
        df_cat_ti = df_cat_ti.sort_values("Pct_TIC", ascending=True).tail(10)

        fig2, ax2 = plt.subplots(figsize=(6, 4))
        ax2.barh(df_cat_ti["Categoria"], df_cat_ti["Pct_TIC"], color="#1565C0", label="% TIC")
        ax2.barh(df_cat_ti["Categoria"], 100 - df_cat_ti["Pct_TIC"],
                 left=df_cat_ti["Pct_TIC"], color="#B0BEC5", label="% No TIC")
        ax2.set_xlabel("Porcentaje (%)")
        ax2.set_ylabel("")
        ax2.set_title("Proporcion TIC / No TIC por categoria")
        ax2.legend(loc="lower right")
        sns.despine(left=True)
        st.pyplot(fig2)

    st.markdown("---")
    st.subheader("Volumen de ofertas TIC vs No TIC por categoria")
    st.caption("Pregunta: Cuanto aporta cada categoria al total TIC y al total No TIC?")

    # Bivariate: categoria x es_ti (volumen absoluto lado a lado)
    df_vol = df.groupby(["categoria", "es_ti"]).size().reset_index(name="Cantidad")
    df_vol["Sector"] = df_vol["es_ti"].map({True: "TIC", False: "No TIC"})
    top10 = df["categoria"].value_counts().head(10).index
    df_vol10 = df_vol[df_vol["categoria"].isin(top10)]

    fig3, ax3 = plt.subplots(figsize=(11, 4))
    sns.barplot(data=df_vol10, x="categoria", y="Cantidad", hue="Sector",
                palette=["#1565C0", "#B0BEC5"], ax=ax3)
    ax3.set_xlabel("")
    ax3.set_ylabel("Numero de ofertas")
    ax3.set_title("Ofertas TIC vs No TIC por categoria (top 10)")
    plt.xticks(rotation=30, ha="right")
    ax3.legend(title="Sector")
    sns.despine(left=True)
    st.pyplot(fig3)


# =============================================================
# PESTANA 2: NIVEL TACTICO
# Indicador 1: Modalidad de trabajo por categoria
# Indicador 2: Tipo de jornada (Full time / Part time) por sector TIC
# Indicador 3: Seniority requerido en el mercado
# Frecuencia: Semanal | Responsable: Gerente de Talento / RRHH
# =============================================================
with tab_tac:
    st.header("Analisis Tactico de la Oferta Laboral")
    st.caption("Frecuencia: Semanal | Objetivo: Identificar tendencias de modalidad, jornada y seniority por sector")

    # Filtro de sector
    sector = st.radio("Ver analisis para:", ["Todo el mercado", "Solo ofertas TIC", "Solo ofertas No TIC"],
                      horizontal=True)
    if sector == "Solo ofertas TIC":
        df_tac = df[df["es_ti"] == True]
    elif sector == "Solo ofertas No TIC":
        df_tac = df[df["es_ti"] == False]
    else:
        df_tac = df.copy()

    st.markdown("---")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Modalidad de trabajo por categoria")
        st.caption("Que categorias tienen mas trabajo remoto o hibrido?")

        top_cats = df_tac["categoria"].value_counts().head(8).index
        df_mod_cat = df_tac[df_tac["categoria"].isin(top_cats)]

        pivot = df_mod_cat.groupby(["categoria", "modalidad"]).size().unstack(fill_value=0)
        pivot_pct = pivot.div(pivot.sum(axis=1), axis=0) * 100

        fig4, ax4 = plt.subplots(figsize=(8, 5))
        colors = {"Presencial": "#2196F3", "Hibrido": "#FF9800", "Remoto": "#4CAF50",
                  "Hibrido": "#FF9800", "No especificado": "#9E9E9E"}
        pivot_pct.plot(kind="barh", stacked=True, ax=ax4,
                       color=[colors.get(c, "#9E9E9E") for c in pivot_pct.columns])
        ax4.set_xlabel("Porcentaje (%)")
        ax4.set_ylabel("")
        ax4.set_title("Modalidad por categoria (%)")
        ax4.legend(title="Modalidad", bbox_to_anchor=(1.01, 1), loc="upper left")
        sns.despine(left=True)
        st.pyplot(fig4)

    with col2:
        st.subheader("Tipo de jornada por categoria")
        st.caption("Distribucion Full time vs Part time")

        df_hor = df_tac[df_tac["tipo_horario_norm"].isin(["Full time", "Part time"])]
        df_hor_cat = df_hor[df_hor["categoria"].isin(top_cats)]

        pivot_h = df_hor_cat.groupby(["categoria", "tipo_horario_norm"]).size().unstack(fill_value=0)
        pivot_h_pct = pivot_h.div(pivot_h.sum(axis=1), axis=0) * 100

        fig5, ax5 = plt.subplots(figsize=(8, 5))
        pivot_h_pct.plot(kind="barh", stacked=True, ax=ax5,
                         color=["#3F51B5", "#E91E63"])
        ax5.set_xlabel("Porcentaje (%)")
        ax5.set_ylabel("")
        ax5.set_title("Jornada por categoria (%)")
        ax5.legend(title="Jornada", bbox_to_anchor=(1.01, 1), loc="upper left")
        sns.despine(left=True)
        st.pyplot(fig5)

    st.markdown("---")
    st.subheader("Seniority requerido: TIC vs No TIC")
    st.caption("Pregunta: El sector TIC exige mayor nivel de experiencia que el resto del mercado?")

    # Bivariate: nivel_seniority x es_ti
    df_sen2 = df.groupby(["nivel_seniority", "es_ti"]).size().reset_index(name="Cantidad")
    df_sen2["Sector"] = df_sen2["es_ti"].map({True: "TIC", False: "No TIC"})
    # Normalizar por sector para comparar proporciones
    totales = df_sen2.groupby("Sector")["Cantidad"].transform("sum")
    df_sen2["Porcentaje"] = (df_sen2["Cantidad"] / totales * 100).round(1)

    orden_sen = ["Junior", "Semi-Senior", "Senior", "No especificado"]
    orden_ok = [s for s in orden_sen if s in df_sen2["nivel_seniority"].unique()]

    fig6, ax6 = plt.subplots(figsize=(9, 4))
    sns.barplot(data=df_sen2, x="nivel_seniority", y="Porcentaje", hue="Sector",
                order=orden_ok, palette=["#1565C0", "#B0BEC5"], ax=ax6)
    ax6.set_xlabel("Nivel de seniority")
    ax6.set_ylabel("% dentro de cada sector")
    ax6.set_title("Seniority requerido: TIC vs No TIC (%)")
    ax6.legend(title="Sector")
    sns.despine(left=True)
    st.pyplot(fig6)


# =============================================================
# PESTANA 3: NIVEL OPERACIONAL
# Indicador 1: Alertas de ofertas sin seniority especificado
# Indicador 2: Buscador de ofertas interactivo
# Indicador 3: Resumen por empresa (top empleadores)
# Frecuencia: Diario | Responsable: Analista / Supervisor
# =============================================================
with tab_op:
    st.header("Panel Operacional - Gestion de Ofertas")
    st.caption("Frecuencia: Diario | Objetivo: Monitorear calidad y detalle de las ofertas laborales")

    st.subheader("Largo de descripcion: TIC vs No TIC")
    st.caption("Hipotesis 3 del proyecto: Las ofertas TIC tienen descripciones mas largas? (Resultado: NO CONFIRMADA)")

    # Bivariate: largo_descripcion x es_ti (boxplot comparativo)
    df_desc = df[df["largo_descripcion"] > 0].copy()
    df_desc["Sector"] = df_desc["es_ti"].map({True: "TIC", False: "No TIC"})

    col_box1, col_box2 = st.columns([2, 1])
    with col_box1:
        fig_box, ax_box = plt.subplots(figsize=(7, 4))
        sns.boxplot(data=df_desc, x="Sector", y="largo_descripcion",
                    palette=["#1565C0", "#B0BEC5"], width=0.4, ax=ax_box)
        ax_box.set_xlabel("Sector")
        ax_box.set_ylabel("Palabras en descripcion")
        ax_box.set_title("Largo de descripcion: TIC vs No TIC")
        sns.despine(left=True)
        st.pyplot(fig_box)
    with col_box2:
        resumen_desc = df_desc.groupby("Sector")["largo_descripcion"].agg(
            Mediana="median", Promedio="mean", Maximo="max"
        ).round(1).reset_index()
        st.dataframe(resumen_desc, hide_index=True, use_container_width=True)
        media_ti  = df_desc[df_desc["es_ti"]==True]["largo_descripcion"].mean()
        media_nti = df_desc[df_desc["es_ti"]==False]["largo_descripcion"].mean()
        diff = round(media_ti - media_nti, 1)
        if diff < 0:
            st.info(f"Las ofertas TIC tienen en promedio {abs(diff)} palabras MENOS que las No TIC. Hipotesis H3 no confirmada.")
        else:
            st.info(f"Las ofertas TIC tienen en promedio {diff} palabras MAS que las No TIC.")

    st.markdown("---")

    # Filtros interactivos
    st.subheader("Buscador de ofertas")
    col_f1, col_f2, col_f3 = st.columns(3)

    with col_f1:
        cats_sel = st.multiselect("Categoria:",
                                   options=sorted(df["categoria"].unique()),
                                   default=sorted(df["categoria"].unique()))
    with col_f2:
        mod_sel = st.multiselect("Modalidad:",
                                  options=sorted(df["modalidad"].unique()),
                                  default=sorted(df["modalidad"].unique()))
    with col_f3:
        hor_sel = st.multiselect("Jornada:",
                                  options=sorted(df["tipo_horario_norm"].unique()),
                                  default=sorted(df["tipo_horario_norm"].unique()))

    df_filtrado = df[
        df["categoria"].isin(cats_sel) &
        df["modalidad"].isin(mod_sel) &
        df["tipo_horario_norm"].isin(hor_sel)
    ]

    st.caption(f"Mostrando {len(df_filtrado)} de {len(df)} ofertas")
    cols_tabla = ["titulo", "empresa", "modalidad", "tipo_horario_norm", "categoria", "nivel_seniority", "es_ti"]
    cols_ok = [c for c in cols_tabla if c in df_filtrado.columns]
    st.dataframe(df_filtrado[cols_ok].reset_index(drop=True), hide_index=True, use_container_width=True)

    st.markdown("---")
    st.subheader("Top empleadores: ofertas TIC vs No TIC")
    st.caption("Pregunta: Las empresas con mas publicaciones son generalistas o especializadas en TIC?")

    if "empresa" in df.columns:
        df_emp2 = df.groupby(["empresa", "es_ti"]).size().reset_index(name="Cantidad")
        df_emp2["Sector"] = df_emp2["es_ti"].map({True: "TIC", False: "No TIC"})
        top_emp = df.groupby("empresa").size().nlargest(12).index
        df_emp2_top = df_emp2[df_emp2["empresa"].isin(top_emp)]

        fig7, ax7 = plt.subplots(figsize=(10, 5))
        sns.barplot(data=df_emp2_top, x="Cantidad", y="empresa", hue="Sector",
                    palette=["#1565C0", "#B0BEC5"], ax=ax7)
        ax7.set_xlabel("Numero de ofertas")
        ax7.set_ylabel("")
        ax7.set_title("Top empleadores: publicaciones TIC vs No TIC")
        ax7.legend(title="Sector")
        sns.despine(left=True)
        st.pyplot(fig7)
    else:
        st.info("Campo empresa no disponible en los datos.")
