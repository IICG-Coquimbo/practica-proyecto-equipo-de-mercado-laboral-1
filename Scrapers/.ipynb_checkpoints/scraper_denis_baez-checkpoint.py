# =============================================================
#  scrapers/scraper_denis_baez.py
#  Scraper de trabajando.cl — Denis Báez
#  Proyecto Big Data — Grupo: denisBaez
# =============================================================

import os
import time
import re
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager


# ================================================================
# CONFIGURACIÓN
# ================================================================
NOMBRE_GRUPO   = "denisBaez"
LIMITE_PAGINAS = 2
META_REGISTROS = 500
BASE_URL       = "https://www.trabajando.cl"
PAIS           = "Chile"

SELECTOR_CONTENEDOR = "div#listadoOfertas"
SELECTOR_TARJETA    = "div.result-box-container"

CATEGORIAS = {
    "Ingeniería"      : f"{BASE_URL}/trabajo-ingenieria",
    "Finanzas"        : f"{BASE_URL}/trabajo-finanzas",
    "Ventas"          : f"{BASE_URL}/trabajo-ventas",
    "Salud"           : f"{BASE_URL}/trabajo-salud",
    "Educación"       : f"{BASE_URL}/trabajo-profesor",
    "Teletrabajo"     : f"{BASE_URL}/trabajo-remoto",
    "Híbrido"         : f"{BASE_URL}/trabajo-hibrido",
    "Administración"  : f"{BASE_URL}/trabajo-administrador",
    "Gerencia"        : f"{BASE_URL}/trabajo-gerente",
    "Supervisión"     : f"{BASE_URL}/trabajo-supervisor",
    "Marketing"       : f"{BASE_URL}/trabajo-marketing",
    "Tecnología"      : f"{BASE_URL}/trabajo-informatica",
    "Recursos Humanos": f"{BASE_URL}/trabajo-recursos-humanos",
    "Logística"       : f"{BASE_URL}/trabajo-logistica",
    "Construcción"    : f"{BASE_URL}/trabajo-construccion",
    "Contabilidad"    : f"{BASE_URL}/trabajo-contador",
    "Atención Cliente": f"{BASE_URL}/trabajo-atencion-al-cliente",
    "Legal"           : f"{BASE_URL}/trabajo-abogado",
    "Diseño"          : f"{BASE_URL}/trabajo-diseno",
    "Comercio"        : f"{BASE_URL}/trabajo-comercio",
    "Minería"         : f"{BASE_URL}/trabajo-mineria",
    "Transporte"      : f"{BASE_URL}/trabajo-transporte",
    "Gastronomía"     : f"{BASE_URL}/trabajo-gastronomia",
    "Seguridad"       : f"{BASE_URL}/trabajo-seguridad",
    "Agricultura"     : f"{BASE_URL}/trabajo-agricultura",
    "Inmobiliaria"    : f"{BASE_URL}/trabajo-inmobiliaria",
    "Banca"           : f"{BASE_URL}/trabajo-banco",
    "Seguros"         : f"{BASE_URL}/trabajo-seguros",
    "Farmacia"        : f"{BASE_URL}/trabajo-farmacia",
    "Psicología"      : f"{BASE_URL}/trabajo-psicologo",
    "Arquitectura"    : f"{BASE_URL}/trabajo-arquitecto",
    "Comunicaciones"  : f"{BASE_URL}/trabajo-comunicaciones",
    "Electricidad"    : f"{BASE_URL}/trabajo-electricista",
    "Mecánica"        : f"{BASE_URL}/trabajo-mecanico",
    "Turismo"         : f"{BASE_URL}/trabajo-turismo",
    "Retail"          : f"{BASE_URL}/trabajo-retail",
    "Producción"      : f"{BASE_URL}/trabajo-produccion",
    "Medio Ambiente"  : f"{BASE_URL}/trabajo-medio-ambiente",
    "Aseo"            : f"{BASE_URL}/trabajo-aseo",
    "Callcenter"      : f"{BASE_URL}/trabajo-call-center",
}
# ================================================================


# ── HELPERS ─────────────────────────────────────────────────────

def inferir_modalidad(texto):
    """Remoto / Híbrido / Presencial a partir del texto de la tarjeta."""
    t = texto.lower()
    if any(p in t for p in ["remoto", "teletrabajo", "remote", "100% online", "trabajo desde casa"]):
        return "Remoto"
    if any(p in t for p in ["híbrido", "hibrido", "hybrid", "mixto"]):
        return "Híbrido"
    return "Presencial"


def inferir_tipo_horario(texto):
    """Full-time / Part-time / Freelance / Por turnos / No especificado."""
    t = texto.lower()
    if any(p in t for p in ["part time", "part-time", "medio tiempo", "media jornada"]):
        return "Part-time"
    if any(p in t for p in ["freelance", "honorarios", "por proyecto"]):
        return "Freelance"
    if any(p in t for p in ["turno", "turnos", "rotativo", "nocturno"]):
        return "Por turnos"
    if any(p in t for p in ["full time", "full-time", "jornada completa", "tiempo completo"]):
        return "Full-time"
    return "No especificado"


def extraer_fecha_publicacion(tarjeta_texto):
    """Extrae fecha de publicación del texto de la tarjeta."""
    for linea in tarjeta_texto.split("\n"):
        l = linea.lower().strip()
        if any(p in l for p in ["hace ", "hoy", "publicada", "ayer", "publicado"]):
            return linea.strip()
        if re.search(r"\d{1,2}/\d{1,2}/\d{4}", linea):
            return linea.strip()
    return "No especificada"


# ── FUNCIÓN PRINCIPAL ────────────────────────────────────────────

def ejecutar_extraccion():
    """
    Ejecuta el scraping de trabajando.cl y retorna una lista de
    diccionarios con las ofertas laborales encontradas.

    Campos de cada registro:
        titulo_cargo, empresa, pais, fecha_captura, descripcion,
        modalidad, tipo_horario, fecha_publicacion,
        categoria, url_oferta, grupo
    """

    options = Options()
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")
    options.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    )

    driver        = None
    datos_finales = []
    urls_vistas   = set()

    print("🚀 Iniciando scraper Denis Báez (trabajando.cl)...", flush=True)

    try:
        driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()),
            options=options,
        )
        print("✅ Navegador listo. Comenzando extracción...\n", flush=True)

        for categoria_nombre, url_categoria in CATEGORIAS.items():

            if len(datos_finales) >= META_REGISTROS:
                print(f"\n✅ Meta de {META_REGISTROS} registros alcanzada.", flush=True)
                break

            print(f"\n========== Categoría: {categoria_nombre} ==========", flush=True)
            driver.get(url_categoria)
            time.sleep(7)

            for num_pagina in range(1, LIMITE_PAGINAS + 1):

                if len(datos_finales) >= META_REGISTROS:
                    break

                print(f"  --- Página {num_pagina} ---", flush=True)

                try:
                    WebDriverWait(driver, 15).until(
                        EC.presence_of_element_located(
                            (By.CSS_SELECTOR, SELECTOR_CONTENEDOR)
                        )
                    )
                except Exception:
                    print(f"  ⚠️ Timeout esperando {SELECTOR_CONTENEDOR}", flush=True)

                tarjetas = driver.find_elements(By.CSS_SELECTOR, SELECTOR_TARJETA)

                if not tarjetas:
                    print("  ❌ Sin tarjetas. DOM puede haber cambiado.", flush=True)
                    break

                print(f"  ✅ Ofertas encontradas: {len(tarjetas)}")

                for tarjeta in tarjetas:

                    if len(datos_finales) >= META_REGISTROS:
                        break

                    try:
                        texto_tarjeta = tarjeta.text

                        # ── TÍTULO y URL ──────────────────────────────────
                        titulo_cargo = "No especificado"
                        url_oferta   = "No disponible"
                        try:
                            link = tarjeta.find_element(
                                By.XPATH, ".//a[contains(@href,'/trabajo/')]"
                            )
                            titulo_cargo = link.text.strip() or "No especificado"
                            url_oferta   = link.get_attribute("href") or "No disponible"
                        except Exception:
                            pass

                        # ── EMPRESA ───────────────────────────────────────
                        empresa = "No especificada"
                        try:
                            for sel_emp in [
                                "[class*='company']",
                                "[class*='empresa']",
                                "[class*='client']",
                                "[class*='razon']",
                            ]:
                                try:
                                    elem = tarjeta.find_element(By.CSS_SELECTOR, sel_emp)
                                    val  = elem.text.strip()
                                    if val and val != titulo_cargo:
                                        empresa = val
                                        break
                                except Exception:
                                    continue

                            if empresa == "No especificada":
                                lineas = [l.strip() for l in texto_tarjeta.split("\n") if l.strip()]
                                for linea in lineas:
                                    if (
                                        linea != titulo_cargo
                                        and not any(
                                            p in linea.lower()
                                            for p in [
                                                "hace ", "hoy", "ayer", "publicad", "remoto",
                                                "híbrido", "hibrido", "presencial",
                                                "full", "part", "turno",
                                            ]
                                        )
                                        and len(linea) > 3
                                    ):
                                        empresa = linea
                                        break
                        except Exception:
                            pass

                        # ── CAMPOS DERIVADOS ──────────────────────────────
                        pais              = PAIS
                        descripcion       = texto_tarjeta.replace("\n", " ").strip()
                        modalidad         = inferir_modalidad(texto_tarjeta + " " + descripcion)
                        tipo_horario      = inferir_tipo_horario(texto_tarjeta + " " + descripcion)
                        fecha_publicacion = extraer_fecha_publicacion(texto_tarjeta)
                        fecha_captura     = time.strftime("%Y-%m-%d %H:%M:%S")

                        # ── DEDUPLICACIÓN ─────────────────────────────────
                        if url_oferta in urls_vistas:
                            continue
                        urls_vistas.add(url_oferta)

                        registro = {
                            "titulo_cargo"     : titulo_cargo,
                            "empresa"          : empresa,
                            "pais"             : pais,
                            "fecha_captura"    : fecha_captura,
                            "descripcion"      : descripcion,
                            "modalidad"        : modalidad,
                            "tipo_horario"     : tipo_horario,
                            "fecha_publicacion": fecha_publicacion,
                            "categoria"        : categoria_nombre,
                            "url_oferta"       : url_oferta,
                            "grupo"            : NOMBRE_GRUPO,
                        }
                        datos_finales.append(registro)

                    except Exception as e:
                        print(f"  ⚠️ Tarjeta omitida: {e}", flush=True)
                        continue

                print(
                    f"  ✔ Página {num_pagina} procesada | "
                    f"Acumulado: {len(datos_finales)}/{META_REGISTROS} registros"
                )

                # ── SIGUIENTE PÁGINA ──────────────────────────────────────
                if num_pagina < LIMITE_PAGINAS and len(datos_finales) < META_REGISTROS:
                    avanzado = False
                    for sel_next in [
                        "a[rel='next']",
                        ".pagination a[aria-label='Siguiente']",
                        "[aria-label='Siguiente']",
                        "[aria-label='Next']",
                        "li.page-item:last-child a",
                        "[class*='siguiente']",
                        "[class*='next']",
                    ]:
                        try:
                            btn = driver.find_element(By.CSS_SELECTOR, sel_next)
                            driver.execute_script("arguments[0].click();", btn)
                            time.sleep(5)
                            avanzado = True
                            break
                        except Exception:
                            continue

                    if not avanzado:
                        sep = "&" if "?" in url_categoria else "?"
                        driver.get(f"{url_categoria}{sep}page={num_pagina + 1}")
                        time.sleep(5)

        duplicados = len(urls_vistas) - len(datos_finales)
        print(f"\n✅ Extracción finalizada.", flush=True)
        print(f"   Registros únicos  : {len(datos_finales)}")
        print(f"   Duplicados saltados: {duplicados}", flush=True)

    except Exception as e:
        print(f"\n❌ Error fatal: {e}", flush=True)
        import traceback
        traceback.print_exc()

    finally:
        if driver:
            driver.quit()
            print("\nNavegador cerrado.", flush=True)

    return datos_finales


# ── Ejecución directa (prueba local) ─────────────────────────────
if __name__ == "__main__":
    resultados = ejecutar_extraccion()
    print(f"\n📦 Total registros devueltos: {len(resultados)}")
    if resultados:
        import pprint
        pprint.pprint(resultados[0])
