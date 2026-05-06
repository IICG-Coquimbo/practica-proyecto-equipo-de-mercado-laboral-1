import os
import time
import random
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

CATEGORIAS = [
    "informatica", "administracion", "ventas", "comercial", "bodega",
    "logistica", "secretaria", "recepcion", "contabilidad", "finanzas",
    "recursos humanos", "marketing", "salud", "educacion", "ingenieria",
    "construccion", "transporte", "gastronomia", "turismo", "retail",
    "juridico", "diseno", "comunicaciones", "agricultura", "mineria",
    "manufactura", "seguridad", "limpieza", "telecomunicaciones", "farmacia"
]


def extraer_empleos(
    nombre_grupo="Giannella-Rieu",
    meta_registros=500,
    limite_paginas=15
):
    """
    Extrae ofertas de empleo desde cl.jobrapido.com usando Selenium.

    Parámetros:
        nombre_grupo   (str): Nombre identificador del grupo.
        meta_registros (int): Cantidad máxima de registros únicos a extraer.
        limite_paginas (int): Máximo de páginas a recorrer por categoría.

    Retorna:
        list[dict]: Lista de registros con las 8 columnas definidas.
    """

    # Limpieza de procesos residuales
    try:
        os.system('pkill -9 chrome')
        os.system('pkill -9 chromedriver')
    except:
        pass

    options = Options()
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--headless=new")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
    )

    driver = None
    datos_finales = []
    empleos_vistos = set()

    try:
        print(f"Iniciando extracción — Grupo: {nombre_grupo.replace('-', ' ')} | Meta: {meta_registros} registros\n")

        driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()),
            options=options
        )
        driver.set_page_load_timeout(35)
        driver.execute_script(
            "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
        )

        for categoria in CATEGORIAS:
            if len(datos_finales) >= meta_registros:
                break

            print(f"========== Categoría: {categoria.capitalize()} ==========")
            paginas_vacias_consecutivas = 0

            for num_pagina in range(1, limite_paginas + 1):
                if len(datos_finales) >= meta_registros:
                    break

                termino = categoria.replace(' ', '%20')
                url = f"https://cl.jobrapido.com/?w={termino}&l=Chile&p={num_pagina}"

                try:
                    driver.get(url)
                    time.sleep(random.uniform(2.5, 4.0))
                    driver.execute_script("window.scrollTo(0, document.body.scrollHeight/3);")
                    time.sleep(1)
                    driver.execute_script("window.scrollTo(0, document.body.scrollHeight/1.5);")
                    time.sleep(1)
                except Exception:
                    print(f"  Timeout en página {num_pagina}, continuando...")
                    continue

                try:
                    WebDriverWait(driver, 12).until(
                        EC.presence_of_all_elements_located(
                            (By.CSS_SELECTOR, "div[class*='job'], div[class*='result'], article")
                        )
                    )
                    tarjetas = driver.find_elements(
                        By.CSS_SELECTOR, "div[class*='job'], div[class*='result'], article"
                    )
                except Exception:
                    print("  Sin resultados o bloqueo detectado. Siguiente categoría.")
                    break

                nuevos_en_pagina = 0

                for tarjeta in tarjetas:
                    if len(datos_finales) >= meta_registros:
                        break
                    try:
                        texto_tarjeta = tarjeta.text
                        if not texto_tarjeta or len(texto_tarjeta) < 20:
                            continue

                        # Título
                        try:
                            titulo_cargo = tarjeta.find_element(
                                By.CSS_SELECTOR,
                                "h2, h3, a[class*='title'], div[class*='title']"
                            ).text.strip()
                        except Exception:
                            try:
                                titulo_cargo = tarjeta.find_element(By.TAG_NAME, "a").text.strip()
                            except Exception:
                                continue

                        # Empresa
                        try:
                            empresa = tarjeta.find_element(
                                By.CSS_SELECTOR, "[class*='company'], [class*='empname']"
                            ).text.strip()
                            if "confidencial" in empresa.lower() or len(empresa) < 3:
                                empresa = "Confidencial"
                        except Exception:
                            lineas = texto_tarjeta.split('\n')
                            empresa = lineas[1] if len(lineas) > 1 else "Confidencial"

                        # Deduplicación
                        huella = f"{titulo_cargo}-{empresa}".lower()
                        if huella in empleos_vistos:
                            continue

                        # Descripción
                        try:
                            descripcion = tarjeta.find_element(
                                By.CSS_SELECTOR, "[class*='desc'], [class*='snippet'], p"
                            ).text.strip()
                        except Exception:
                            descripcion = texto_tarjeta[:150].replace('\n', ' ') + "..."

                        texto_lower = texto_tarjeta.lower()

                        # Modalidad
                        if any(x in texto_lower for x in ["hibrido", "híbrido"]):
                            modalidad = "Hibrido"
                        elif any(x in texto_lower for x in ["remoto", "teletrabajo", "home office"]):
                            modalidad = "Remoto"
                        else:
                            modalidad = "Presencial"

                        # Horario
                        tipo_horario = (
                            "Part time"
                            if any(x in texto_lower for x in ["part time", "medio tiempo", "parcial"])
                            else "Full time"
                        )

                        # Fecha publicación
                        try:
                            fecha_publicacion = tarjeta.find_element(
                                By.CSS_SELECTOR, "[class*='date'], [class*='time']"
                            ).text.strip()
                        except Exception:
                            fecha_publicacion = "Reciente"

                        registro = {
                            "Titulo de Cargo"      : titulo_cargo,
                            "Empresa"              : empresa,
                            "Pais"                 : "Chile",
                            "Fecha de Captura"     : "2026-03-01 " + time.strftime("%H:%M:%S"),
                            "Descripcion"          : descripcion,
                            "Modalidad"            : modalidad,
                            "Tipo de Horario"      : tipo_horario,
                            "Fecha de Publicacion" : fecha_publicacion
                        }

                        datos_finales.append(registro)
                        empleos_vistos.add(huella)
                        nuevos_en_pagina += 1

                    except Exception:
                        continue

                print(f"  Página {num_pagina}: {nuevos_en_pagina} nuevos | Total: {len(datos_finales)}")

                if nuevos_en_pagina == 0:
                    paginas_vacias_consecutivas += 1
                else:
                    paginas_vacias_consecutivas = 0

                if paginas_vacias_consecutivas >= 3:
                    print("  Límite de ofertas en esta categoría. Siguiente...")
                    break

        print(f"\nExtracción finalizada. Registros únicos: {len(datos_finales)}")

    except Exception as e:
        print(f"Error principal: {e}")

    finally:
        if driver:
            driver.quit()
            print("Navegador cerrado.")

    return datos_finales  # ← siempre retorna, aunque sea lista parcial o vacía