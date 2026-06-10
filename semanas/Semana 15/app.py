import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
import streamlit as st

# 1. Configuración del entorno y diseño visual profesional
st.set_page_config(
    page_title="Dashboard Profesional de Mercado Laboral",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Estilización avanzada mediante CSS para estructurar las tarjetas de análisis y fijar contrastes
st.markdown(
    """
    <style>
    .reportview-container { background: #F8F9FA; }
    .main .block-container { padding-top: 1.5rem; }
    div[data-testid="stMetricValue"] { font-size: 1.6rem; font-weight: bold; color: #1A237E; }
    .stRadio p { font-size: 1.1rem; font-weight: 500; }
    .analysis-card { background-color: #FFFFFF; color: #212529; padding: 18px; border-radius: 8px; border-left: 4px solid #1A237E; margin-top: 12px; font-size: 0.95rem; line-height: 1.5; box-shadow: 0 1px 3px rgba(0,0,0,0.05); }
    </style>
    """,
    unsafe_allow_html=True,
)

# Encabezado formal corporativo
st.markdown("### Control de Gestión: Panel Analítico del Mercado Laboral")
st.markdown("**Analista:** Sofía Urquieta Palma | Departamento de Control de Gestión")
st.markdown("---")


# 2. Ingesta y Limpieza de Datos conforme al Repositorio
@st.cache_data
def procesar_datos_mercado():
    data = pd.read_csv("datos_mercado_laboral.csv")

    if "es_ti" in data.columns:
        data["es_ti"] = data["es_ti"].fillna(False).astype(bool)

    if "es_remoto" in data.columns:
        data["es_remoto"] = data["es_remoto"].fillna(False).astype(bool)

    if "modalidad" in data.columns:
        data["modalidad"] = (
            data["modalidad"]
            .str.strip()
            .str.capitalize()
            .fillna("No especificada")
        )
        data = data[data["modalidad"] != "No especificada"]

    if "tipo_horario" in data.columns:
        data["tipo_horario"] = (
            data["tipo_horario"]
            .str.strip()
            .str.capitalize()
            .fillna("No especificado")
        )
        data = data[data["tipo_horario"] != "No especificado"]

    if "nivel_seniority" in data.columns:
        data["nivel_seniority"] = (
            data["nivel_seniority"]
            .str.strip()
            .str.capitalize()
            .fillna("No especificado")
        )

    return data


try:
    df = procesar_datos_mercado()

    # Sistema de navegación lateral por niveles jerárquicos de decisión
    nivel_organizacional = st.sidebar.radio(
        "Seleccione el nivel jerárquico a analizar:",
        options=[
            "Nivel Estratégico (Dirección / CEO)",
            "Nivel Táctico (Gerencia de RRHH)",
            "Nivel Operacional (Supervisión de Procesos)",
        ],
    )

    # ══════════════════════════════════════════════════════════════
    # 1. NIVEL ESTRATÉGICO
    # ══════════════════════════════════════════════════════════════
    if nivel_organizacional == "Nivel Estratégico (Dirección / CEO)":
        st.markdown("#### Reporte de Indicadores Estratégicos")
        st.caption(
            "Monitoreo macro de la composición sectorial y niveles de flexibilidad en el mercado de contratación."
        )

        col1, col2 = st.columns(2, gap="large")

        with col1:
            st.markdown("##### KPI 1: Composición de la Fuerza Laboral (TI vs No TI)")
            conteo_ti = df["es_ti"].value_counts()
            total_ofertas = len(df)
            total_ti = conteo_ti.get(True, 0)
            pct_ti = (total_ti / total_ofertas) * 100 if total_ofertas > 0 else 0

            # Corrección Semana 13: Uso de Gráfico de Anillo (Donut Chart) para liberar aire visual
            fig1, ax1 = plt.subplots(figsize=(5, 4), facecolor="white")
            ax1.set_facecolor("white")
            conteo_ti.plot(
                kind="pie",
                labels=["Estructuras TI", "Sectores Tradicionales"],
                autopct="%1.1f%%",
                colors=["#1A237E", "#CFD8DC"],
                ax=ax1,
                startangle=90,
                wedgeprops=dict(width=0.4, edgecolor="w"),
                textprops={"color": "#212529", "fontsize": 10},
            )
            ax1.set_ylabel("")
            st.pyplot(fig1)

            st.markdown(
                f"""
                <div class="analysis-card">
                    <strong>Análisis de Composición:</strong> De un universo total de {total_ofertas:,} ofertas de trabajo consolidadas, 
                    las plazas orientadas al área de tecnologías de la información alcanzan una tasa del <strong>{pct_ti:.1f}%</strong> ({total_ti:,} vacantes). 
                    Esta distribución establece la representatividad y el peso relativo del sector digital dentro de los flujos de contratación actuales.
                </div>
                """,
                unsafe_allow_html=True,
            )

        with col2:
            st.markdown(
                "##### KPI 2: Índice de Flexibilidad Laboral (Distribución Remota)"
            )
            if "es_remoto" in df.columns and "es_ti" in df.columns:
                # Corrección Semana 13: Barras Apiladas al 100% Horizontal para una comparación directa de estructuras binarias
                tabla_flex = (
                    df.groupby("es_ti")["es_remoto"]
                    .value_counts(normalize=True)
                    .unstack()
                    .mul(100)
                )

                fig2, ax2 = plt.subplots(figsize=(6, 3.8), facecolor="white")
                ax2.set_facecolor("white")
                tabla_flex.plot(
                    kind="barh", stacked=True, color=["#CFD8DC", "#0D47A1"], ax=ax2
                )
                ax2.set_yticklabels(
                    ["Sectores Tradicionales", "Estructuras TI"],
                    rotation=0,
                    fontsize=10,
                    color="#212529",
                )
                ax2.set_xlabel("% Proporcional dentro del Sector", fontsize=10)
                ax2.set_ylabel("")
                ax2.legend(
                    ["Formato Local/Híbrido", "Formato Remoto"], loc="lower left"
                )
                sns.despine(left=True, bottom=True)
                st.pyplot(fig2)

                pct_remoto_ti = tabla_flex.loc[True, True]
                pct_remoto_noti = tabla_flex.loc[False, True]

                st.markdown(
                    f"""
                    <div class="analysis-card" style="border-left-color: #0288D1;">
                        <strong>Análisis de Flexibilidad:</strong> El indicador evidencia que la modalidad de trabajo remota alcanza un <strong>{pct_remoto_ti:.1f}%</strong> dentro del sector tecnológico, 
                        frente al <strong>{pct_remoto_noti:.1f}%</strong> registrado en los sectores tradicionales. Esta brecha confirma que las estructuras TI asimilan con mayor rapidez la flexibilidad como elemento corporativo estratégico.
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

    # ══════════════════════════════════════════════════════════════
    # 2. NIVEL TÁCTICO
    # ══════════════════════════════════════════════════════════════
    elif nivel_organizacional == "Nivel Táctico (Gerencia de RRHH)":
        st.markdown("#### Reporte de Indicadores Tácticos")
        st.caption(
            "Segmentación de los requerimientos específicos de contratación en función del formato de trabajo."
        )

        modalidades_disponibles = sorted(
            [m for m in df["modalidad"].unique() if m != "No especificada"]
        )
        modalidad_sel = st.selectbox(
            "Filtro de Modalidad Laboral:", options=modalidades_disponibles
        )

        df_filtrado_tactico = df[df["modalidad"] == modalidad_sel]

        col3, col4 = st.columns(2, gap="large")

        with col3:
            st.markdown("##### KPI 3: Distribución de Horarios por Modalidad")
            conteo_horario = (
                df_filtrado_tactico["tipo_horario"]
                .value_counts(normalize=True)
                .mul(100)
                .sort_values(ascending=True)
            )

            if not conteo_horario.empty:
                # Corrección Foto: Rotación a Barras Horizontales Ordenadas para lectura natural de etiquetas largas
                fig3, ax3 = plt.subplots(figsize=(6, 3.8), facecolor="white")
                ax3.set_facecolor("white")
                conteo_horario.plot(kind="barh", color="#1A237E", ax=ax3)
                ax3.set_xlabel("% de Distribución de Ofertas", fontsize=10)
                ax3.set_ylabel("")
                ax3.tick_params(axis="y", labelsize=10, colors="#212529")
                sns.despine(left=True, bottom=True)
                st.pyplot(fig3)

                horario_lider = conteo_horario.index[-1]
                pct_horario_lider = conteo_horario.iloc[-1]

                st.markdown(
                    f"""
                    <div class="analysis-card">
                        <strong>Análisis de Estructuras de Jornada:</strong> Al aislar la modalidad de trabajo <em>{modalidad_sel}</em>, la jornada de tipo <strong>{horario_lider}</strong> 
                        predomina ampliamente en el mercado con el <strong>{pct_horario_lider:.1f}%</strong> de las plazas publicadas bajo este segmento.
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

        with col4:
            st.markdown("##### KPI 4: Progresión de Demanda por Nivel de Seniority")

            # Ordenamiento estricto manual y posicionado para forzar la escala jerárquica cualitativa ordinal
            orden_seniority = ["Junior", "Semi-senior", "Senior", "Lead"]
            df_filtrado_tactico["nivel_seniority"] = (
                df_filtrado_tactico["nivel_seniority"]
                .str.strip()
                .str.capitalize()
            )
            conteo_raw = df_filtrado_tactico["nivel_seniority"].value_counts(
                normalize=True
            )
            conteo_seniority = (
                conteo_raw.reindex(orden_seniority).fillna(0).mul(100)
            )

            if not conteo_seniority.empty:
                # Corrección Foto: Se fijó el rango e índice numérico explícito en X para corregir la línea diagonal incorrecta
                fig4, ax4 = plt.subplots(figsize=(6, 3.8), facecolor="white")
                ax4.set_facecolor("white")
                ax4.plot(
                    range(len(orden_seniority)),
                    conteo_seniority.values,
                    color="#009688",
                    marker="o",
                    linewidth=2.5,
                    markersize=8,
                )
                ax4.set_xticks(range(len(orden_seniority)))
                ax4.set_xticklabels(
                    orden_seniority, fontsize=10, color="#212529"
                )
                ax4.set_ylabel("% de Demanda de Candidatos", fontsize=10)
                ax4.set_xlabel(
                    "Evolución de Experiencia (Eje Ordinal)", fontsize=10
                )
                ax4.tick_params(axis="y", labelsize=10, colors="#212529")
                ax4.set_ylim(0, max(conteo_seniority.values) + 15)
                sns.despine()
                plt.grid(axis="y", linestyle="--", alpha=0.3)
                st.pyplot(fig4)

                # Identificación dinámica sobre la muestra limpia excluyendo los omitidos
                df_clean_sens = df_filtrado_tactico[
                    df_filtrado_tactico["nivel_seniority"].isin(orden_seniority)
                ]
                if not df_clean_sens.empty:
                    seniority_lider = (
                        df_clean_sens["nivel_seniority"].value_counts().index[0]
                    )
                    pct_seniority_lider = (
                        df_clean_sens["nivel_seniority"]
                        .value_counts(normalize=True)
                        .iloc[0]
                        * 100
                    )
                else:
                    seniority_lider = "No detectado"
                    pct_seniority_lider = 0.0

                st.markdown(
                    f"""
                    <div class="analysis-card" style="border-left-color: #009688;">
                        <strong>Análisis de Curva de Experiencia:</strong> El análisis de tendencia en la modalidad <em>{modalidad_sel}</em> identifica que el requerimiento 
                        máximo se concentra en el perfil <strong>{seniority_lider}</strong>, abarcando un <strong>{pct_seniority_lider:.1f}%</strong> de las solicitudes registradas, permitiendo mapear la madurez requerida en el reclutamiento.
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

    # ══════════════════════════════════════════════════════════════
    # 3. NIVEL OPERACIONAL
    # ══════════════════════════════════════════════════════════════
    elif nivel_organizacional == "Nivel Operacional (Supervisión de Procesos)":
        st.markdown("#### Monitoreo de Indicadores Operacionales")
        st.caption(
            "Aseguramiento de la calidad de la información, consistencia de la ingesta y gobernanza de los datos."
        )

        col5, col6 = st.columns(2, gap="large")

        with col5:
            st.markdown("##### KPI 5: Control de Integridad (Tasa de Vacíos en Seniority)")
            total_registros = len(df)
            nulos_seniority = len(df[df["nivel_seniority"] == "No especificado"])
            tasa_nulidad = (
                (nulos_seniority / total_registros) * 100
                if total_registros > 0
                else 0
            )

            # Tarjeta de control KPI 5 con alto contraste y color semántico rojo
            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown(
                f"""
                <div style="
                    background-color: #F8F9FA; 
                    border-left: 6px solid #C62828; 
                    padding: 20px; 
                    border-radius: 8px; 
                    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                    margin-bottom: 15px;
                ">
                    <p style="margin: 0; font-size: 0.95rem; color: #555555; font-weight: bold; text-transform: uppercase; letter-spacing: 0.5px;">
                        Tasa de Registros Omitidos (Calidad de Datos)
                    </p>
                    <h2 style="margin: 10px 0 5px 0; font-size: 2.8rem; color: #C62828; font-weight: 800;">
                        {tasa_nulidad:.1f}%
                    </h2>
                    <p style="margin: 0; font-size: 0.9rem; color: #212529; font-weight: 500;">
                        ⚠️ Alerta Operativa: <span style="color: #C62828; font-weight: bold;">{nulos_seniority:,} filas</span> detectadas sin nivel de seniority especificado.
                    </p>
                </div>
                """,
                unsafe_allow_html=True,
            )

            st.markdown(
                f"""
                <div class="analysis-card" style="border-left-color: #C62828;">
                    <strong>Control de Integridad de Datos:</strong> El sistema detecta que un <strong>{tasa_nulidad:.1f}%</strong> del lote actual carece de las etiquetas lógicas requeridas de nivel de experiencia. 
                    Este indicador sirve de alerta operativa diaria para calibrar los diccionarios de extracción del pipeline automatizado.
                </div>
                """,
                unsafe_allow_html=True,
            )

        with col6:
            st.markdown(
                "##### KPI 6: Control de Redundancia y Registros Duplicados"
            )
            if "titulo" in df.columns and "empresa" in df.columns:
                conteo_duplicados = (
                    df.groupby(["titulo", "empresa"])
                    .size()
                    .reset_index(name="Frecuencia")
                )
                registros_duplicados = conteo_duplicados[
                    conteo_duplicados["Frecuencia"] > 1
                ]
                total_duplicados = (
                    registros_duplicados["Frecuencia"].sum()
                    - len(registros_duplicados)
                )

                # CORRECCIÓN KPI 6: Tarjeta de control de redundancia integrada con alto contraste en color azul/gris corporativo
                st.markdown("<br>", unsafe_allow_html=True)
                st.markdown(
                    f"""
                    <div style="
                        background-color: #F8F9FA; 
                        border-left: 6px solid #78909C; 
                        padding: 20px; 
                        border-radius: 8px; 
                        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                        margin-bottom: 15px;
                    ">
                        <p style="margin: 0; font-size: 0.95rem; color: #555555; font-weight: bold; text-transform: uppercase; letter-spacing: 0.5px;">
                            Volumen de Filas Redundantes Detectadas
                        </p>
                        <h2 style="margin: 10px 0 5px 0; font-size: 2.8rem; color: #78909C; font-weight: 800;">
                            {total_duplicados:,} <span style="font-size: 1.5rem; font-weight: 500;">registros</span>
                        </h2>
                        <p style="margin: 0; font-size: 0.9rem; color: #212529; font-weight: 500;">
                            📊 Control de Redundancia: Base de datos optimizada para modelos analíticos.
                        </p>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

                if total_duplicados > 0:
                    top_duplicados_tabla = registros_duplicados.sort_values(
                        "Frecuencia", ascending=False
                    ).head(3)
                    st.dataframe(
                        top_duplicados_tabla[
                            ["titulo", "empresa", "Frecuencia"]
                        ],
                        use_container_width=True,
                        hide_index=True,
                    )

                st.markdown(
                    """
                    <div class="analysis-card" style="border-left-color: #78909C;">
                        <strong>Control de Redundancia:</strong> Mide la tasa de duplicación temporal provocada por la republicación de ofertas idénticas en portales laborales. Funciona como umbral operativo básico para activar scripts de depuración automatizados.
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

        st.markdown("---")
        st.markdown("##### Estado General del Pipeline de Datos")
        st.metric(
            label="Volumen Neto de Ofertas de Trabajo en Producción",
            value=f"{len(df):,} registros",
        )

except FileNotFoundError:
    st.error(
        "El origen de datos 'datos_mercado_laboral.csv' no fue detectado en el directorio. Ejecute primero la celda final de su Jupyter Notebook."
    )