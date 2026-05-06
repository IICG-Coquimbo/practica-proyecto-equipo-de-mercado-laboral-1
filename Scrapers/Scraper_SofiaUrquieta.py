import os
import re
import time
import random
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
    # CONFIGURACION
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
    options.add_experimental_option(
        "prefs", {"profile.managed_default_content_settings.images": 2}
    )

    driver        = None
    datos_finales = []
    urls_vistas   = set()

    try:
        service = Service(ChromeDriverManager().install())
        driver  = webdriver.Chrome(service=service, options=options)
        driver.set_page_load_timeout(30)

        pagina = 1
        print(f"Iniciando recoleccion para {NOMBRE_INTEGRANTE}...")

        while len(datos_finales) < META_DATOS:
            url = f"https://firstjob.me/ofertas?page={pagina}"
            print(f"\n========== Pagina {pagina} ==========")
            driver.get(url)

            try:
                WebDriverWait(driver, 15).until(
                    EC.presence_of_element_located(
                        (By.CSS_SELECTOR, "h6.card-job-top--info-heading")
                    )
                )
            except Exception:
                print("  Sin resultados en esta pagina, finalizando.")
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

                    try:
                        titulo_cargo = h6.text.strip()
                        if not titulo_cargo:
                            raise ValueError
                    except Exception:
                        titulo_cargo = "No especificado"

                    try:
                        empresa = contenedor_a.find_element(
                            By.CSS_SELECTOR, "span[class*='company']"
                        ).text.strip()
                        if not empresa:
                            raise ValueError
                    except Exception:
                        empresa = "No especificada"

                    try:
                        modalidad = contenedor_a.find_element(
                            By.CSS_SELECTOR, "span[class*='background-blue-light']"
                        ).text.strip()
                        if not modalidad:
                            raise ValueError
                    except Exception:
                        modalidad = "No especificada"

                    try:
                        ciudad = contenedor_a.find_element(
                            By.CSS_SELECTOR, "span[class*='location']"
                        ).text.strip()
                        if not ciudad:
                            raise ValueError
                    except Exception:
                        ciudad = "No especificada"

                    try:
                        desc_el = contenedor_a.find_element(
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

            print(f"Progreso: {len(datos_finales)} registros capturados.")

            if len(datos_finales) >= META_DATOS:
                break

            pagina += 1
            time.sleep(random.uniform(2, 3))

        print(f"\nExtraccion finalizada. Total: {len(datos_finales)} registros")

    except Exception as e:
        print(f"Error: {e}")

    finally:
        if driver:
            driver.quit()
            print("Navegador cerrado.")

    return datos_finales


if __name__ == "__main__":
    ejecutar_scraping_firstjob()
