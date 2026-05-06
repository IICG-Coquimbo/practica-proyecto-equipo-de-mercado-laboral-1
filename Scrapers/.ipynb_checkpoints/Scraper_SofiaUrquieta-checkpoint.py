import os
import re
import time
import certifi
import random
from pymongo import MongoClient
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager


def ejecutar_scraping_firstjob():
    os.system('pkill -9 chrome')
    os.system('pkill -9 chromedriver')
    os.environ['DISPLAY'] = ':99'

    # ================================================
    # CONFIGURACIÓN
    # ================================================
    NOMBRE_INTEGRANTE = "Sofia-Urquieta"
    META_DATOS        = 500
    # ================================================

    options = Options()
    options.binary_location = "/usr/bin/google-chrome"
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1366,768")
    options.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    )
    # Desactivar carga de imágenes para mayor velocidad
    options.add_experimental_option(
        "prefs", {"profile.managed_default_content_settings.images": 2}
    )

    driver      = None
    datos_finales = []
    urls_vistas   = set()

    try:
        service = Service(ChromeDriverManager().install())
        driver  = webdriver.Chrome(service=service, options=options)
        driver.set_page_load_timeout(30)

        pagina = 1
        print(f"🚀 Iniciando recolección para {NOMBRE_INTEGRANTE}...")

        while len(datos_finales) < META_DATOS:
            url = f"https://firstjob.me/ofertas?page={pagina}"
            print(f"\n========== Página {pagina} ==========")
            driver.get(url)

            # Esperar a que carguen las tarjetas
            try:
                WebDriverWait(driver, 15).until(
                    EC.presence_of_element_located(
                        (By.CSS_SELECTOR, "h6.card-job-top--info-heading")
                    )
                )
            except Exception:
                print("  Sin resultados en esta página, finalizando.")
                break

            titulos_h6 = driver.find_elements(By.CSS_SELECTOR, "h6.card-job-top--info-heading")
            if not titulos_h6:
                print("  No se encontraron tarjetas.")
                break

            print(f"  Ofertas encontradas: {len(titulos_h6)}")

            for h6 in titulos_h6:
                if len(datos_finales) >= META_DATOS:
                    break
                try:
                    contenedor_a = h6.find_element(By.XPATH, "./ancestor::a")
                    link = contenedor_a.get_attribute("href").split("?")[0]

                    if link in urls_vistas:
                        continue

                    # --- TÍTULO DEL CARGO ---
                    try:
                        titulo_cargo = h6.text.strip()
                        if not titulo_cargo:
                            raise ValueError
                    except Exception:
                        titulo_cargo = "No especificado"

                    # --- EMPRESA ---
                    try:
                        empresa = contenedor_a.find_element(
                            By.CSS_SELECTOR, "span[class*='company']"
                        ).text.strip()
                        if not empresa:
                            raise ValueError
                    except Exception:
                        empresa = "No especificada"

                    # --- MODALIDAD ---
                    try:
                        modalidad = contenedor_a.find_element(
                            By.CSS_SELECTOR, "span[class*='background-blue-light']"
                        ).text.strip()
                        if not modalidad:
                            raise ValueError
                    except Exception:
                        modalidad = "No especificada"

                    # --- CIUDAD ---
                    try:
                        ciudad = contenedor_a.find_element(
                            By.CSS_SELECTOR, "span[class*='location']"
                        ).text.strip()
                        if not ciudad:
                            raise ValueError
                    except Exception:
                        ciudad = "No especificada"

                    # --- DESCRIPCIÓN ---
                    try:
                        desc_el    = contenedor_a.find_element(
                            By.CSS_SELECTOR, "div[class*='card-job-description']"
                        )
                        descripcion = desc_el.get_attribute("innerText").strip()
                        if not descripcion:
                            raise ValueError
                    except Exception:
                        descripcion = "No disponible en listado"

                    registro = {
                        "Titulo de Cargo"      : titulo_cargo,
                        "Empresa"              : empresa,
                        "Pais"                 : "Chile",
                        "Fecha de Captura"     : time.strftime("%d/%m/%Y"),
                        "Descripcion"          : descripcion,
                        "Modalidad"            : modalidad,
                        "Tipo de Horario"      : "Jornada Completa",
                        "Fecha de Publicacion" : time.strftime("%d/%m/%Y"),
                        "Ciudad"               : ciudad,
                        "Integrante"           : NOMBRE_INTEGRANTE,
                        "URL_Oferta"           : link,
                    }

                    datos_finales.append(registro)
                    urls_vistas.add(link)

                except Exception as e:
                    print(f"  Advertencia en tarjeta: {e}")
                    continue

            print(f"📊 Progreso: {len(datos_finales)} registros capturados.")

            if len(datos_finales) >= META_DATOS:
                break

            pagina += 1
            time.sleep(random.uniform(2, 3))

        print(f"\nExtracción finalizada. Total: {len(datos_finales)} registros")

    except Exception as e:
        print(f"Error: {e}")

    finally:
        if driver:
            driver.quit()
            print("Navegador cerrado.")

    # ================================================
    # CONEXIÓN A MONGODB ATLAS
    # ================================================
    MONGO_URI = "mongodb+srv://BenjaminRamirez:fim5S0MTo17YVRw0@cluster0.kek1o3u.mongodb.net/?retryWrites=true&w=majority"

    try:
        client    = MongoClient(MONGO_URI, tlsCAFile=certifi.where())
        db        = client["TiendaBigData"]
        coleccion = db["x_SofiaUrquieta"]
        print("CONEXIÓN ESTABLECIDA.")
    except Exception as e:
        print("ERROR DE CONEXIÓN:", e)
        return datos_finales

    exitosos = 0
    fallidos  = 0

    for dato in datos_finales:
        try:
            coleccion.update_one(
                {"URL_Oferta": dato["URL_Oferta"]},
                {"$set": dato},
                upsert=True
            )
            exitosos += 1
        except Exception as e:
            print("ERROR:", e)
            fallidos += 1

    print(f"\nRESUMEN:")
    print(f"  Exitosos : {exitosos}")
    print(f"  Fallidos : {fallidos}")
    print(f"  Total en colección : {coleccion.count_documents({})}")

    return datos_finales


# Ejecución independiente
if __name__ == "__main__":
    ejecutar_scraping_firstjob()
