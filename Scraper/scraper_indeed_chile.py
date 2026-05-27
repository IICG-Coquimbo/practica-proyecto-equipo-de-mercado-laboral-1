import time
import certifi
import os
import random
from pymongo import MongoClient
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.core.os_manager import ChromeType


def ejecutar_extraccion():
    NOMBRE_INTEGRANTE = "Denis-Baez"
    META_DATOS = 500
    MAX_PAGINAS_POR_BUSQUEDA = 8
    RESULTADOS_POR_PAGINA = 10  # Indeed muestra 15 por página por defecto
    datos_finales = []
    empleos_vistos = set()

    # Indeed usa términos de búsqueda libres, no categorías por slug
    terminos = [
        "informatica", "administracion", "ventas", "comercial", "bodega",
        "logistica", "secretaria", "recepcion", "contabilidad", "finanzas",
        "recursos humanos", "marketing", "salud", "educacion", "ingenieria",
        "construccion", "transporte", "gastronomia", "turismo", "retail",
        "juridico", "diseño", "comunicaciones", "agricultura", "mineria",
        "manufactura", "seguridad", "limpieza", "telecomunicaciones", "farmacia"
    ]

    # Indeed Chile usa nombres de ciudad/región como filtro de ubicación
    ubicaciones = [
        "Santiago",
        "Valparaíso",
        "Concepción",
        "Temuco",
        "Antofagasta",
        "La Serena",
        "Puerto Montt",
        "Iquique",
        "Rancagua",
        "Talca"
    ]

    def generar_busquedas():
        """
        Genera pares (termino, ubicacion).
        Primero recorre todos los términos sin ubicación,
        luego los términos prioritarios con cada ciudad.
        """
        busquedas = []
        for t in terminos:
            busquedas.append((t, None))
        terminos_prioritarios = [
            "administracion", "ventas", "informatica", "salud",
            "educacion", "logistica", "contabilidad", "construccion",
            "retail", "manufactura"
        ]
        for t in terminos_prioritarios:
            for ub in ubicaciones:
                busquedas.append((t, ub))
        return busquedas

    # ---------- Configuración del navegador ----------
    options = Options()
    if os.path.exists("/usr/bin/brave-browser"):
        options.binary_location = "/usr/bin/brave-browser"
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--lang=es-CL")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])

    try:
        path = ChromeDriverManager(chrome_type=ChromeType.BRAVE).install()
        service = Service(path)
    except Exception:
        service = (
            Service("/usr/bin/chromedriver")
            if os.path.exists("/usr/bin/chromedriver")
            else Service()
        )

    driver = webdriver.Chrome(service=service, options=options)

    # ---------- Helpers ----------
    def texto(el, selector, by=By.CSS_SELECTOR, default="No especificado"):
        try:
            return el.find_element(by, selector).text.strip() or default
        except Exception:
            return default

    def atributo(el, selector, attr, by=By.CSS_SELECTOR, default=""):
        try:
            return el.find_element(by, selector).get_attribute(attr).strip()
        except Exception:
            return default

    def obtener_bloques(driver):
        """
        Indeed envuelve cada oferta en un <li> con class 'css-1ac2h1w' o similar.
        Probamos varios selectores en orden de especificidad.
        """
        selectores = [
            (By.CSS_SELECTOR, "li.css-1ac2h1w"),          # clase típica de tarjeta de empleo
            (By.CSS_SELECTOR, "div.job_seen_beacon"),       # clase alternativa
            (By.CSS_SELECTOR, "div[data-testid='slider_container']"),
            (By.CSS_SELECTOR, "div.resultContent"),
            (By.CSS_SELECTOR, "li[class*='jobsearch-ResultsList']"),
            (By.CSS_SELECTOR, "div.tapItem"),               # vista móvil/compacta
            (By.CSS_SELECTOR, "div[class*='result ']"),
        ]
        for by, sel in selectores:
            bloques = driver.find_elements(by, sel)
            if bloques:
                return bloques
        return []

    def inferir_modalidad(bloque):
        """
        Indeed a veces muestra badges de 'Remoto', 'Híbrido', etc.
        Buscamos en varios selectores posibles.
        """
        selectores_modalidad = [
            "div[data-testid='attribute_snippet_testid']",
            "span.css-k5flys",
            "div.metadata",
            ".remote",
            "[data-testid='remoteLabel']",
        ]
        palabras_remoto = ["remoto", "teletrabajo", "home office", "trabajo desde casa"]
        palabras_hibrido = ["híbrido", "hibrido", "mixto"]

        for sel in selectores_modalidad:
            try:
                elementos = bloque.find_elements(By.CSS_SELECTOR, sel)
                for elem in elementos:
                    txt = elem.text.lower()
                    if any(p in txt for p in palabras_remoto):
                        return "Remoto"
                    if any(p in txt for p in palabras_hibrido):
                        return "Híbrido"
            except Exception:
                continue
        return "Presencial"

    def extraer_registro(bloque, termino):
        # --- Título ---
        titulo = "No especificado"
        for sel in [
            "h2.jobTitle span[title]",
            "h2.jobTitle a span",
            "h2 a span",
            "span[title]",
            "a[data-jk] span",
        ]:
            val = texto(bloque, sel)
            if val != "No especificado":
                titulo = val
                break

        # --- Empresa ---
        empresa = "No especificado"
        for sel in [
            "[data-testid='company-name']",
            "span.css-63koeb",
            "span.company",
            ".companyName",
            "a[data-tn-element='companyName']",
        ]:
            val = texto(bloque, sel)
            if val != "No especificado":
                empresa = val
                break

        # --- Modalidad ---
        modalidad = inferir_modalidad(bloque)

        # --- Fecha ---
        fecha = "No especificado"
        for sel in ["span[data-testid='myJobsStateDate']", "span.date", ".date"]:
            val = texto(bloque, sel, default="")
            if val:
                fecha = val
                break
        if fecha == "No especificado":
            fecha = time.strftime("%d/%m/%Y")

        return {
            "Titulo del cargo": titulo,
            "País": "Chile",
            "Modalidad de trabajo": modalidad,
            "Fecha": fecha,
            "Tipo de moneda": "CLP",
            "Categoría de empleo": termino.replace("-", " ").title(),
            "Empresa": empresa,
            "Integrante": NOMBRE_INTEGRANTE,
        }

    # ---------- Loop principal ----------
    try:
        print(f"{'='*55}")
        print(f"  Extracción Indeed Chile: {NOMBRE_INTEGRANTE}")
        print(f"  Meta: {META_DATOS} registros únicos")
        print(f"{'='*55}\n")

        for termino, ubicacion in generar_busquedas():
            if len(datos_finales) >= META_DATOS:
                break

            for pagina in range(0, MAX_PAGINAS_POR_BUSQUEDA):
                if len(datos_finales) >= META_DATOS:
                    break

                # Indeed pagina con el parámetro 'start' (múltiplos de 10/15)
                start = pagina * RESULTADOS_POR_PAGINA

                # Construcción de la URL
                # q  = término de búsqueda
                # l  = ubicación
                # start = offset de paginación
                q_encoded = termino.replace(" ", "+")
                base_url = f"https://cl.indeed.com/jobs?q={q_encoded}&lang=es"
                if ubicacion:
                    l_encoded = ubicacion.replace(" ", "+")
                    base_url += f"&l={l_encoded}"
                url = base_url if start == 0 else f"{base_url}&start={start}"

                label_loc = f" | {ubicacion}" if ubicacion else ""
                print(
                    f"[{len(datos_finales):>3}/{META_DATOS}] "
                    f"{termino}{label_loc} | pág {pagina + 1}"
                )

                driver.get(url)
                time.sleep(random.uniform(4, 7))  # Indeed es sensible al scraping

                # Esperamos que aparezca al menos un resultado
                try:
                    WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located(
                            (By.CSS_SELECTOR, "h2.jobTitle, div.job_seen_beacon")
                        )
                    )
                except Exception:
                    pass

                bloques = obtener_bloques(driver)
                if not bloques:
                    print("       -> Sin resultados, pasando al siguiente término")
                    break

                nuevos_pagina = 0
                for bloque in bloques:
                    if len(datos_finales) >= META_DATOS:
                        break
                    try:
                        registro = extraer_registro(bloque, termino)
                        titulo = registro["Titulo del cargo"]
                        empresa = registro["Empresa"]
                        huella = f"{titulo}|{empresa}".lower().strip()

                        if titulo == "No especificado" or len(titulo) < 3:
                            continue
                        if huella in empleos_vistos:
                            continue

                        datos_finales.append(registro)
                        empleos_vistos.add(huella)
                        nuevos_pagina += 1
                    except Exception:
                        continue

                print(f"       -> +{nuevos_pagina} nuevos | Total: {len(datos_finales)}")

                if nuevos_pagina == 0:
                    break

                # Pausa entre páginas para evitar bloqueos
                time.sleep(random.uniform(2, 4))

    finally:
        driver.quit()

    print(f"\n{'='*55}")
    print(f"  TOTAL REGISTROS ÚNICOS: {len(datos_finales)}")
    print(f"{'='*55}\n")

    # ---------- Guardar en MongoDB Atlas ----------
    if datos_finales:
        uri = "mongodb+srv://BenjaminRamirez:fim5S0MTo17YVRw0@cluster0.kek1o3u.mongodb.net/?retryWrites=true&w=majority"
        try:
            client = MongoClient(uri, tlsCAFile=certifi.where())
            db = client["TiendaBigData"]
            coleccion = db["Indeed_Denis"]  # Colección renombrada para Indeed

            print("Limpiando registros previos en Atlas...")
            coleccion.delete_many({"Integrante": NOMBRE_INTEGRANTE})

            resultado = coleccion.insert_many(datos_finales)
            print(f"¡LOGRADO! {len(resultado.inserted_ids)} registros guardados en Atlas.")
        except Exception as e:
            print(f"Error al conectar con Atlas: {e}")
    else:
        print("No se obtuvieron datos. Verifica los selectores CSS del sitio.")

    return datos_finales


if __name__ == "__main__":
    datos = ejecutar_extraccion()
    print(f"\nRegistros finales: {len(datos)}")
    if datos:
        print("\nMuestra del primer registro:")
        for k, v in datos[0].items():
            print(f"  {k}: {v}")
        print(f"\nCategorías encontradas: {set(d['Categoría de empleo'] for d in datos)}")
