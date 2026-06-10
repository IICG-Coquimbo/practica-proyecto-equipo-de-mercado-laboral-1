import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# 1. Configuración de la página web
st.set_page_config(page_title="Dashboard Mercado Laboral", layout="wide")

st.title("📊 Cuadro de Mando Integral - Analítica de Empleo")
st.markdown("---")

# 2. Carga de datos optimizada
@st.cache_data
def cargar_datos():
    # Cargamos tus datos reales del mercado laboral
    df_lab = pd.read_csv("datos_mercado_laboral.csv")
    # Limpieza básica de espacios
    df_lab['empresa'] = df_lab['empresa'].fillna('No Especificada').astype(str).str.strip()
    df_lab['categoria_horario_modalidad'] = df_lab['categoria_horario_modalidad'].fillna('No Especificado').astype(str).str.strip()
    return df_lab

df = cargar_datos()

# 3. Creación de las Pestañas por Nivel Organizacional
tab_est, tab_tac, tab_op = st.tabs([
    "📈 Nivel Estratégico (CEO / Dirección)",
    "🎯 Nivel Táctico (Gerencia de RRHH)",
    "🛠️ Nivel Operacional (Supervisor de Selección)"
])

# ==========================================
# PESTAÑA 1: NIVEL ESTRATÉGICO
# ==========================================
with tab_est:
    st.header("Concentración del Mercado por Empresa")
    st.caption("Frecuencia: Mensual | Objetivo: Evaluar qué empresas dominan la oferta de vacantes")
    
    total_ofertas = len(df)
    df_est = df['empresa'].value_counts().reset_index()
    df_est.columns = ['Empresa', 'Cantidad_Ofertas']
    df_est['Participacion'] = (df_est['Cantidad_Ofertas'] / total_ofertas) * 100
    
    col1, col2 = st.columns([1, 2])
    with col1:
        st.metric(label="Total Ofertas Analizadas", value=total_ofertas)
        st.metric(
            label="Empleador Líder", 
            value=df_est['Empresa'].iloc[0], 
            delta=f"{df_est['Participacion'].iloc[0]:.1f}% del total de vacantes"
        )
        st.dataframe(df_est.head(10), hide_index=True)
        
    with col2:
        fig, ax = plt.subplots(figsize=(8, 4.5))
        # Graficamos el Top 10 de empresas con más ofertas
        sns.barplot(x="Participacion", y="Empresa", data=df_est.head(10), hue="Empresa", palette="Blues_r", legend=False, ax=ax)
        sns.despine(left=True, bottom=False)
        ax.set_xlabel("Participación en el Mercado (%)")
        st.pyplot(fig)

# ==========================================
# PESTAÑA 2: NIVEL TÁCTICO
# ==========================================
with tab_tac:
    st.header("Análisis de Modalidad y Tipos de Contrato")
    st.caption("Frecuencia: Semanal | Objetivo: Diseñar estrategias atractivas de contratación (Remoto vs Presencial)")
    
    # Filtro interactivo por Empresa utilizando tus datos reales
    empresas_unicas = df['empresa'].unique()
    empresas_seleccionadas = st.multiselect(
        "Filtrar Empresas para Analizar sus Modalidades:", 
        options=empresas_unicas, 
        default=df['empresa'].value_counts().head(5).index.tolist()
    )
    
    df_filtrado = df[df['empresa'].isin(empresas_seleccionadas)]
    
    if not df_filtrado.empty:
        df_modalidad = df_filtrado['categoria_horario_modalidad'].value_counts().reset_index()
        df_modalidad.columns = ['Modalidad_Horario', 'Conteo']
        
        fig, ax = plt.subplots(figsize=(10, 4.5))
        sns.barplot(x="Conteo", y="Modalidad_Horario", data=df_modalidad, hue="Modalidad_Horario", palette="Dark2", legend=False, ax=ax)
        ax.set_xlabel("Número de Ofertas")
        ax.set_ylabel("Categoría / Horario / Modalidad")
        sns.despine(left=True)
        st.pyplot(fig)
    else:
        st.warning("Por favor, selecciona al menos una empresa.")

# ==========================================
# PESTAÑA 3: NIVEL OPERACIONAL
# ==========================================
with tab_op:
    st.header("Buscador Operacional y Alertas de Vacantes")
    st.caption("Frecuencia: Diario | Objetivo: Monitorear puestos y revisar la descripción de ofertas críticas")
    
    # Buscador en tiempo real por palabras clave en el cargo o descripción
    busqueda = st.text_input("Buscar Cargos Específicos (ej. 'Data', 'Desarrollador', 'Administrador'):", "")
    
    df_op = df.copy()
    if busqueda:
        df_op = df_op[df_op['cargo_nombre'].str.contains(busqueda, case=False, na=False)]
        
    st.info(f"📋 Se encontraron {len(df_op)} vacantes que coinciden con los criterios de búsqueda.")
    
    # Vista de tabla operativa detallada
    st.subheader("Lista de Vacantes Activas:")
    st.dataframe(
        df_op[['cargo_nombre', 'empresa', 'salario_texto', 'categoria_horario_modalidad']], 
        hide_index=True,
        use_container_width=True
    )