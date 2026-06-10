"""
PASO 2 — Exportar datos del mercado laboral a CSV para Streamlit
Ejecutar desde la terminal de Jupyter:
    cd /home/jovyan/work/semanas/Semana\ 15/
    python exportar_datos.py
"""

import os, re, certifi
import pandas as pd
from pymongo import MongoClient
from dotenv import load_dotenv

# ─── Carga de credenciales ───────────────────────────────────
load_dotenv()
MONGO_URI = os.getenv("MONGO_URI")
DB_NAME   = os.getenv("DB_NAME", "Proyecto_Bigdata")

client = MongoClient(MONGO_URI, tlsCAFile=certifi.where())
db     = client[DB_NAME]

print(f"Conectado a '{DB_NAME}'. Cargando processed_data...")
datos = list(db["processed_data"].find({}, {"_id": 0}))
df    = pd.DataFrame(datos)
print(f"Registros cargados: {len(df)}")

# ─── Normalización de modalidad ──────────────────────────────
df["modalidad"] = df["modalidad"].fillna("No especificado").str.strip().str.capitalize()
# Corregir "Híbrido" con y sin tilde
df["modalidad"] = df["modalidad"].replace({"Hibrid": "Híbrido", "Hibrido": "Híbrido"})

if "categoria_horario_modalidad" in df.columns:
    mask = df["categoria_horario_modalidad"].str.strip().str.lower() == "hibrid"
    df.loc[mask, "modalidad"] = "Híbrido"

# ─── Normalización de horario ────────────────────────────────
def normalizar_horario(valor):
    if not isinstance(valor, str) or not valor.strip():
        return "Otro"
    v = valor.strip().lower()
    if "full" in v or "tiempo completo" in v or "jornada completa" in v:
        return "Full time"
    if "part" in v or "medio" in v or "parcial" in v:
        return "Part time"
    if "free" in v or "independ" in v:
        return "Freelance"
    return "Otro"

col_horario = "tipo_horario" if "tipo_horario" in df.columns else None
if col_horario:
    df["tipo_horario_norm"] = df[col_horario].apply(normalizar_horario)
elif "tipo_horario_norm" not in df.columns:
    df["tipo_horario_norm"] = "Otro"

# ─── Clasificación de categoría TIC ─────────────────────────
PALABRAS_TI = {
    "QA / Testing":     ["qa", "test", "calidad", "quality"],
    "Data / BI":        ["data", "bi ", "inteligencia", "analista de dato", "bigdata", "machine learning", "ia ", "ml "],
    "DevOps / Cloud":   ["devops", "cloud", "aws", "azure", "infraestructura", "sre", "platform"],
    "Desarrollo / Dev": ["develop", "programad", "software", "backend", "frontend", "fullstack", "java", "python", "react"],
    "TI General":       ["ti ", " ti", "soporte ti", "informatic", "sistemas", "it support", "helpdesk"],
}
PALABRAS_NO_TI = {
    "Ingenieria Civil": ["civil", "obras", "construccion", "hidraulic"],
    "Salud":            ["enfermero", "medic", "doctor", "farmac", "clinico", "salud"],
    "Educacion":        ["docente", "profesor", "educacion", "pedagogia"],
    "Ventas / Comercial": ["venta", "comercial", "ejecutivo de cuentas", "kpi"],
    "Recursos Humanos": ["rrhh", "recursos humanos", "reclutamiento", "talento"],
}

def clasificar(titulo):
    if not isinstance(titulo, str):
        return "Otros"
    t = titulo.lower()
    for cat, kws in PALABRAS_TI.items():
        if any(k in t for k in kws):
            return cat
    for cat, kws in PALABRAS_NO_TI.items():
        if any(k in t for k in kws):
            return cat
    return "Otros"

col_titulo = "titulo_cargo" if "titulo_cargo" in df.columns else "titulo"
if col_titulo in df.columns:
    df["categoria"] = df[col_titulo].apply(clasificar)
else:
    df["categoria"] = "Otros"

# ─── Variable es_ti ──────────────────────────────────────────
TI_CATS = {"QA / Testing", "Data / BI", "DevOps / Cloud", "Desarrollo / Dev", "TI General"}
if "es_ti" not in df.columns:
    df["es_ti"] = df["categoria"].isin(TI_CATS)
else:
    df["es_ti"] = df["es_ti"].astype(bool)

# ─── Variable es_remoto ──────────────────────────────────────
if "es_remoto" not in df.columns:
    df["es_remoto"] = df["modalidad"].isin(["Remoto", "Híbrido"])

# ─── Seniority ───────────────────────────────────────────────
if "nivel_seniority" in df.columns:
    df["nivel_seniority"] = df["nivel_seniority"].fillna("No especificado").replace("", "No especificado")
else:
    df["nivel_seniority"] = "No especificado"

# ─── Empresa ─────────────────────────────────────────────────
if "empresa" in df.columns:
    df["empresa"] = df["empresa"].fillna("No especificada").replace("", "No especificada")
else:
    df["empresa"] = "No especificada"

# ─── Largo descripcion ───────────────────────────────────────
if "largo_descripcion" in df.columns:
    df["largo_descripcion"] = pd.to_numeric(df["largo_descripcion"], errors="coerce").fillna(0).astype(int)
elif "descripcion" in df.columns:
    df["largo_descripcion"] = df["descripcion"].fillna("").apply(lambda x: len(str(x).split()))
else:
    df["largo_descripcion"] = 0

# ─── Titulo limpio ───────────────────────────────────────────
df["titulo"] = df[col_titulo] if col_titulo in df.columns else "Sin titulo"

# ─── Columnas finales para el dashboard ─────────────────────
COLS = ["titulo", "empresa", "modalidad", "tipo_horario_norm",
        "categoria", "nivel_seniority", "es_ti", "es_remoto", "largo_descripcion"]
COLS_OK = [c for c in COLS if c in df.columns]
df_dashboard = df[COLS_OK].copy()

# ─── Exportar CSV ────────────────────────────────────────────
RUTA = "/home/jovyan/work/semanas/Semana 15/datos_mercado_laboral_dashboard.csv"
df_dashboard.to_csv(RUTA, index=False, encoding="utf-8")
print(f"\nDatos exportados correctamente: {len(df_dashboard)} registros")
print(f"Columnas: {df_dashboard.columns.tolist()}")
print(f"Archivo: {RUTA}")
print("\nDistribuciones:")
print("  es_ti:", df_dashboard["es_ti"].value_counts().to_dict())
print("  modalidad:", df_dashboard["modalidad"].value_counts().to_dict())
