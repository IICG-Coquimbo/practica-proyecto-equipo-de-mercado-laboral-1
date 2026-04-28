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
    NOMBRE_INTEGRANTE = "Benjamin-Ramirez"
    META_DATOS = 500
    MAX_PAGINAS_POR_URL = 8
    datos_finales = []
    empleos_vistos = set()

    categorias = [
        "informatica", "administracion", "ventas", "comercial", "bodega",
        "logistica", "secretaria", "recepcion", "contabilidad", "finanzas",
        "recursos-humanos", "marketing", "salud", "educacion", "ingenieria",
        "construccion", "transporte", "gastronomia", "turismo", "retail",
        "juridico", "diseno", "comunicaciones", "agricultura", "mineria",
        "manufactura", "seguridad", "limpieza", "telecomunicaciones", "farmacia"
    ]

    regiones = [
        "region-metropolitana", "valparaiso", "biobio", "araucania",
        "maule", "ohiggins", "los-lagos", "antofagasta", "coquimbo", "atacama"
    ]

    def generar_urls():
        urls = []
        for cat in categorias:
            urls.append((cat, None))
        cats_prioritarias = ["administracion", "ventas", "informatica", "salud",
                             "educacion", "logistica", "contabilidad", "construccion",
                             "retail", "manufactura"]
        for cat in cats_prioritarias:
            for reg in regiones:
                urls.append((cat, reg))
        return urls

    options = Options()
    if os.path.exists("/usr/bin/brave-browser"):
        options.binary_location = "/usr/bin/brave-browser"
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])

    try:
        path = ChromeDriverManager(chrome_type=ChromeType.BRAVE).install()
        service = Service(path)
    except Exception:
        service = Service("/usr/bin/chromedriver") if os.path.exists("/usr/bin/chromedriver") else Service()

    driver = webdriver.Chrome(service=service, options=options)

    def texto(el, selector, by=By.CSS_SELECTOR, default="No especificado"):
        try:
            return el.find_element(by, selector).text.strip() or default
        except:
            return default

    def atributo(el, selector, attr, by=By.CSS_SELECTOR, default=""):
        try:
            return el.find_element(by, selector).get_attribute(attr).strip()
        except:
            return default

    def obtener_bloques(driver):
        selectores = [
            (By.CLASS_NAME, "job-item"),
            (By.CSS_SELECTOR, ".job-listing"),
            (By.CSS_SELECTOR, ".oferta"),
            (By.CSS_SELECTOR, "article.job"),
            (By.CSS_SELECTOR, "div[class*='job-']"),
            (By.CSS_SELECTOR, "li[class*='job']"),
            (By.CSS_SELECTOR, ".empleo"),
        ]
        for by, sel in selectores:
            bloques = driver.find_elements(by, sel)
            if bloques:
                return bloques
        return []

    def extraer_registro(bloque, categoria):
        titulo = texto(bloque, "h2", by=By.TAG_NAME)
        if titulo == "No especificado":
            titulo = texto(bloque, ".job-title")
        if titulo == "No especificado":
            titulo = texto(bloque, "a", by=By.TAG_NAME)

        empresa = texto(bloque, "h3", by=By.TAG_NAME)
        if empresa == titulo or empresa == "No especificado":
            empresa = texto(bloque, ".company, .empresa, .employer, .company-name")

        modal_raw = texto(bloque, ".modalidad, .work-mode, .remote, .tipo-trabajo", default="")
        palabras_remoto = ["remoto", "teletrabajo", "home office", "híbrido", "hibrido"]
        if any(p in modal_raw.lower() for p in palabras_remoto):
            modalidad = "Remoto" if "remoto" in modal_raw.lower() or "teletrabajo" in modal_raw.lower() else "Híbrido"
        else:
            modalidad = "Presencial"

        fecha_raw = texto(bloque, ".date, .fecha, .published, time", default="")
        if not fecha_raw:
            fecha_raw = atributo(bloque, "time", "datetime")
        fecha = fecha_raw if fecha_raw else time.strftime("%d/%m/%Y")

        return {
            "Titulo del cargo": titulo,
            "País": "Chile",
            "Modalidad de trabajo": modalidad,
            "Fecha": fecha,
            "Tipo de moneda": "CLP",
            "Categoría de empleo": categoria.replace("-", " ").title(),
            "Empresa": empresa,
            "Integrante": NOMBRE_INTEGRANTE
        }

    try:
        print(f"{'='*55}")
        print(f"  Extracción: {NOMBRE_INTEGRANTE} | Meta: {META_DATOS} únicos")
        print(f"{'='*55}\n")

        for categoria, region in generar_urls():
            if len(datos_finales) >= META_DATOS:
                break

            for pagina in range(1, MAX_PAGINAS_POR_URL + 1):
                if len(datos_finales) >= META_DATOS:
                    break

                if region:
                    base = f"https://www.chiletrabajos.cl/encuentra-un-empleo?2={categoria}&region={region}"
                else:
                    base = f"https://www.chiletrabajos.cl/encuentra-un-empleo?2={categoria}"

                url = base if pagina == 1 else f"{base}&page={pagina}"

                print(f"[{len(datos_finales):>3}/{META_DATOS}] {categoria}" +
                      (f" | {region}" if region else "") +
                      f" | pág {pagina}")

                driver.get(url)
                time.sleep(random.uniform(3, 5))

                try:
                    WebDriverWait(driver, 8).until(
                        EC.presence_of_element_located((By.TAG_NAME, "h2"))
                    )
                except:
                    pass

                bloques = obtener_bloques(driver)
                if not bloques:
                    break

                nuevos_pagina = 0
                for bloque in bloques:
                    if len(datos_finales) >= META_DATOS:
                        break
                    try:
                        registro = extraer_registro(bloque, categoria)
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
                    except:
                        continue

                print(f"       -> +{nuevos_pagina} nuevos | Total: {len(datos_finales)}")

                if nuevos_pagina == 0:
                    break

                time.sleep(random.uniform(1.5, 3))

    finally:
        driver.quit()

    print(f"\n{'='*55}")
    print(f"  TOTAL REGISTROS UNICOS: {len(datos_finales)}")
    print(f"{'='*55}\n")

    if datos_finales:
        uri = "mongodb+srv://BenjaminRamirez:fim5S0MTo17YVRw0@cluster0.kek1o3u.mongodb.net/?retryWrites=true&w=majority"
        try:
            client = MongoClient(uri, tlsCAFile=certifi.where())
            db = client["TiendaBigData"]
            coleccion = db["ChileTrabajos_Benjamin"]

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
        print(f"\nCategorias encontradas: {set(d['Categoría de empleo'] for d in datos)}")