import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

st.set_page_config(page_title="Dashboard — Mercado Laboral TI Chile", layout="wide")
st.title("Cuadro de Mando Integral — Mercado Laboral TI Chile")
st.markdown("**Grupo 4 | Big Data para la Toma de Decisiones | UCN 2026**")
st.markdown("---")

@st.cache_data
def cargar_datos():
    return pd.read_csv("datos_mercado_laboral.csv")

df = cargar_datos()

if "es_ti"    in df.columns: df["es_ti"]    = df["es_ti"].fillna(False).astype(bool)
if "es_remoto" in df.columns: df["es_remoto"] = df["es_remoto"].fillna(False).astype(bool)
if "modalidad"       in df.columns: df["modalidad"]       = df["modalidad"].str.strip().str.capitalize().fillna("No especificada")
if "tipo_horario"    in df.columns: df["tipo_horario"]     = df["tipo_horario"].str.strip().str.capitalize().fillna("No especificado")
if "nivel_seniority" in df.columns: df["nivel_seniority"]  = df["nivel_seniority"].fillna("No especificado")
if "titulo" not in df.columns and "titulo_cargo" in df.columns: df["titulo"] = df["titulo_cargo"]

tab_est, tab_tac, tab_op = st.tabs([
    "Nivel Estratégico",
    "Nivel Táctico",
    "Nivel Operacional"
])

# ══════════════════════════════════════════════════════════════
# PESTAÑA 1 — ESTRATÉGICO
# ══════════════════════════════════════════════════════════════
with tab_est:
    st.header("Nivel Estratégico")
    st.caption("Frecuencia: Mensual | Usuario: Dirección / CEO")

    total        = len(df)
    total_ti     = int(df["es_ti"].sum())     if "es_ti"    in df.columns else 0
    total_no_ti  = total - total_ti
    total_remoto = int(df["es_remoto"].sum()) if "es_remoto" in df.columns else 0

    # ── KPI 1: Participación TI ───────────────────────────────
    st.subheader("KPI 1 — Participación TI en el Mercado")
    st.caption("Del total de ofertas laborales, ¿cuántas son empleos TI?")

    c1, c2, c3 = st.columns(3)
    c1.metric("Total Ofertas", f"{total:,}")
    c2.metric("Ofertas TI",    f"{total_ti:,}", delta=f"{total_ti/total*100:.1f}% del total")
    c3.metric("Ofertas No-TI", f"{total_no_ti:,}", delta=f"{total_no_ti/total*100:.1f}% del total")

    fig, ax = plt.subplots(figsize=(4, 4))
    ax.pie([total_ti, total_no_ti], labels=["TI", "No-TI"],
           autopct="%1.1f%%", colors=["#1565C0", "#B0BEC5"], startangle=90)
    ax.set_title("Participación Sector TI")
    col_pie, _ = st.columns([1, 2])
    with col_pie:
        st.pyplot(fig)

    st.divider()

    # ── KPI 2: Índice de Flexibilidad Laboral ─────────────────
    st.subheader("KPI 2 — Índice de Flexibilidad Laboral")
    st.caption("% de ofertas en modalidad remota: TI vs No-TI")

    if "es_remoto" in df.columns and "es_ti" in df.columns:
        rem_ti    = df[df["es_ti"] == True]["es_remoto"].mean() * 100
        rem_no_ti = df[df["es_ti"] == False]["es_remoto"].mean() * 100
        brecha    = rem_ti - rem_no_ti

        c4, c5, c6 = st.columns(3)
        c4.metric("Remoto en TI",    f"{rem_ti:.1f}%")
        c5.metric("Remoto en No-TI", f"{rem_no_ti:.1f}%")
        c6.metric("Brecha TI vs No-TI", f"+{brecha:.1f} pp", delta="Ventaja TI")

        fig2, ax2 = plt.subplots(figsize=(5, 3))
        ax2.bar(["TI", "No-TI"], [rem_ti, rem_no_ti], color=["#1565C0", "#B0BEC5"])
        ax2.set_ylabel("% Ofertas Remotas")
        ax2.set_title("Flexibilidad Laboral: % Remoto por Sector")
        for i, v in enumerate([rem_ti, rem_no_ti]):
            ax2.text(i, v + 0.5, f"{v:.1f}%", ha="center", fontweight="bold")
        col_bar, _ = st.columns([1, 2])
        with col_bar:
            st.pyplot(fig2)

    st.divider()

    # ── KPI 3: Índice de Horarios TI/No-TI ───────────────────
    st.subheader("KPI 3 — Índice de Horarios Laborales TI vs No-TI")
    st.caption("¿Cuánto Full Time / Part Time según si es TI o No?")

    if "tipo_horario" in df.columns and "es_ti" in df.columns:
        hor = (df.groupby(["es_ti", "tipo_horario"])
               .size().reset_index(name="n"))
        hor["sector"] = hor["es_ti"].map({True: "TI", False: "No-TI"})
        hor_pct = hor.copy()
        totales = hor.groupby("sector")["n"].transform("sum")
        hor_pct["pct"] = (hor["n"] / totales * 100).round(1)

        fig3, ax3 = plt.subplots(figsize=(7, 4))
        sns.barplot(x="tipo_horario", y="pct", hue="sector",
                    data=hor_pct, palette=["#1565C0", "#B0BEC5"], ax=ax3)
        ax3.set_title("Distribución de Horario por Sector (%)")
        ax3.set_xlabel("Tipo de Horario")
        ax3.set_ylabel("% dentro del sector")
        plt.xticks(rotation=15)
        st.pyplot(fig3)


# ══════════════════════════════════════════════════════════════
# PESTAÑA 2 — TÁCTICO
# ══════════════════════════════════════════════════════════════
with tab_tac:
    st.header("Nivel Táctico")
    st.caption("Frecuencia: Semanal | Usuario: RRHH / Reclutamiento")

    # ── KPI 1: Horario según modalidad ───────────────────────
    st.subheader("KPI 1 — % Horario según Modalidad")
    st.caption("Full Time / Part Time según Presencial, Híbrido o Remoto")

    if "tipo_horario" in df.columns and "modalidad" in df.columns:
        tabla_hor_mod = (df.groupby(["modalidad", "tipo_horario"])
                         .size().unstack(fill_value=0))
        tabla_hor_mod_pct = tabla_hor_mod.div(tabla_hor_mod.sum(axis=1), axis=0).mul(100).round(1)
        st.dataframe(tabla_hor_mod_pct.style.format("{:.1f}%"), use_container_width=True)

        fig4, ax4 = plt.subplots(figsize=(8, 4))
        tabla_hor_mod_pct.plot(kind="bar", ax=ax4, color=["#1565C0", "#90CAF9", "#B0BEC5", "#CFD8DC"])
        ax4.set_title("% Horario por Modalidad")
        ax4.set_xlabel("Modalidad")
        ax4.set_ylabel("% Ofertas")
        ax4.legend(title="Horario", bbox_to_anchor=(1, 1))
        plt.xticks(rotation=15)
        plt.tight_layout()
        st.pyplot(fig4)

    st.divider()

    # ── KPI 2: Seniority según modalidad ─────────────────────
    st.subheader("KPI 2 — Seniority según Modalidad")
    st.caption("¿Qué nivel exige cada modalidad de trabajo?")

    if "nivel_seniority" in df.columns and "modalidad" in df.columns:
        validos = df[df["nivel_seniority"] != "No especificado"]
        tabla_sen_mod = (validos.groupby(["modalidad", "nivel_seniority"])
                         .size().unstack(fill_value=0))
        tabla_sen_mod_pct = tabla_sen_mod.div(tabla_sen_mod.sum(axis=1), axis=0).mul(100).round(1)

        fig5, ax5 = plt.subplots(figsize=(8, 4))
        tabla_sen_mod_pct.plot(kind="bar", ax=ax5,
                               color=["#1565C0", "#42A5F5", "#90CAF9", "#B0BEC5"])
        ax5.set_title("% Seniority por Modalidad")
        ax5.set_xlabel("Modalidad")
        ax5.set_ylabel("% Ofertas")
        ax5.legend(title="Seniority", bbox_to_anchor=(1, 1))
        plt.xticks(rotation=15)
        plt.tight_layout()
        st.pyplot(fig5)

    st.divider()

    # ── KPI 3: Seniority según horario ───────────────────────
    st.subheader("KPI 3 — Seniority según Horario")
    st.caption("¿Qué nivel piden los trabajos Full Time vs Part Time?")

    if "nivel_seniority" in df.columns and "tipo_horario" in df.columns:
        validos2 = df[df["nivel_seniority"] != "No especificado"]
        tabla_sen_hor = (validos2.groupby(["tipo_horario", "nivel_seniority"])
                         .size().unstack(fill_value=0))
        tabla_sen_hor_pct = tabla_sen_hor.div(tabla_sen_hor.sum(axis=1), axis=0).mul(100).round(1)

        fig6, ax6 = plt.subplots(figsize=(8, 4))
        tabla_sen_hor_pct.plot(kind="bar", ax=ax6,
                               color=["#1565C0", "#42A5F5", "#90CAF9", "#B0BEC5"])
        ax6.set_title("% Seniority por Tipo de Horario")
        ax6.set_xlabel("Tipo de Horario")
        ax6.set_ylabel("% Ofertas")
        ax6.legend(title="Seniority", bbox_to_anchor=(1, 1))
        plt.xticks(rotation=15)
        plt.tight_layout()
        st.pyplot(fig6)


# ══════════════════════════════════════════════════════════════
# PESTAÑA 3 — OPERACIONAL
# ══════════════════════════════════════════════════════════════
with tab_op:
    st.header("Nivel Operacional")
    st.caption("Frecuencia: Diario | Usuario: Equipo de Datos")

    # ── KPI 1: Tasa de Nulidad en Seniority ──────────────────
    st.subheader("KPI 1 — Tasa de Nulidad en Seniority")

    if "nivel_seniority" in df.columns:
        total_sen    = len(df)
        nulos_sen    = (df["nivel_seniority"].isna().sum()
                        + (df["nivel_seniority"] == "No especificado").sum()
                        + (df["nivel_seniority"] == "no especificado").sum())
        tasa_nulidad = nulos_sen / total_sen * 100

        c7, c8 = st.columns(2)
        c7.metric("Registros sin Seniority", f"{nulos_sen:,}")
        c8.metric("Tasa de Nulidad", f"{tasa_nulidad:.1f}%",
                  delta="Crítico" if tasa_nulidad > 50 else "Aceptable",
                  delta_color="inverse")

        umbral_nul = st.slider("Umbral de alerta nulidad (%):", 0, 100, 50, step=5)
        if tasa_nulidad > umbral_nul:
            st.error(f"La tasa de nulidad en Seniority ({tasa_nulidad:.1f}%) supera el umbral de {umbral_nul}%. "
                     "Esta variable no es confiable como predictor.")
        else:
            st.success(f"Tasa de nulidad ({tasa_nulidad:.1f}%) dentro del umbral de {umbral_nul}%.")

    st.divider()

    # ── KPI 2: Repetición de Duplicados ──────────────────────
    st.subheader("KPI 2 — Repetición de Duplicados")

    if "titulo" in df.columns and "empresa" in df.columns:
        total_reg  = len(df)
        unicos     = df.drop_duplicates(subset=["titulo", "empresa"]).shape[0]
        duplicados = total_reg - unicos
        tasa_dup   = duplicados / total_reg * 100

        c9, c10, c11 = st.columns(3)
        c9.metric("Total Registros",    f"{total_reg:,}")
        c10.metric("Registros Únicos",  f"{unicos:,}")
        c11.metric("Duplicados",        f"{duplicados:,}",
                   delta=f"{tasa_dup:.1f}% del total",
                   delta_color="inverse")

        top_dup = (df[df.duplicated(subset=["titulo", "empresa"], keep=False)]
                   .groupby(["titulo", "empresa"]).size()
                   .reset_index(name="repeticiones")
                   .sort_values("repeticiones", ascending=False).head(10))
        if len(top_dup) > 0:
            st.markdown("**Top 10 registros duplicados:**")
            st.dataframe(top_dup, use_container_width=True, hide_index=True)

    st.divider()

    # ── KPI 3: Precisión del Modelo ──────────────────────────
    st.subheader("KPI 3 — Precisión del Modelo (es_ti)")
    st.caption("Revisión manual de la clasificación TI: ¿qué % de los clasificados como TI realmente lo son?")

    if "es_ti" in df.columns and "titulo" in df.columns:
        ti_sample = df[df["es_ti"] == True][["titulo"]].drop_duplicates().sample(
            min(20, df["es_ti"].sum()), random_state=42)
        st.markdown("**Muestra aleatoria de títulos clasificados como TI (revisar manualmente):**")
        st.dataframe(ti_sample, use_container_width=True, hide_index=True)

        st.markdown("---")
        correctos = st.number_input("¿Cuántos de estos títulos son realmente TI?",
                                    min_value=0, max_value=len(ti_sample),
                                    value=len(ti_sample))
        precision = correctos / len(ti_sample) * 100
        st.metric("Precisión estimada del clasificador es_ti",
                  f"{precision:.1f}%",
                  delta="Buena" if precision >= 80 else "Revisar keywords",
                  delta_color="normal" if precision >= 80 else "inverse")
