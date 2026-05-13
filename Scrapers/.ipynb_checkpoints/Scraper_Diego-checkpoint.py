import os
import re
import time
import certifi
from pymongo import MongoClient
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

def ejecutar_extraccionD():
    os.system('pkill -9 chrome')
    os.system('pkill -9 chromedriver')
    os.environ['DISPLAY'] = ':99'

    # ================================================
    # CONFIGURACIÓN
    # ================================================
    NOMBRE_GRUPO   = "diegoCastillo"
    LIMITE_PAGINAS = 3  # páginas por categoría

    CATEGORIAS = {
        "Programación"          : "https://www.getonbrd.com/empleos-programacion",
        "Diseño"                : "https://www.getonbrd.com/empleos-diseno",
        "Marketing"             : "https://www.getonbrd.com/empleos-marketing",
        "Data"                  : "https://www.getonbrd.com/empleos-data-business-intelligence",
        "Soporte y QA"          : "https://www.getonbrd.com/empleos-soporte-qa",
        "Ventas"                : "https://www.getonbrd.com/empleos-ventas",
        "Gestión y Negocios"    : "https://www.getonbrd.com/empleos-gestion-negocios",
        "Producto"              : "https://www.getonbrd.com/empleos-producto",
        "Customer Success"      : "https://www.getonbrd.com/empleos-customer-success",
        "Recursos Humanos"      : "https://www.getonbrd.com/empleos-recursos-humanos",
        "Finanzas"              : "https://www.getonbrd.com/empleos-finanzas-administracion",
        "Operaciones"           : "https://www.getonbrd.com/empleos-operaciones",
    }
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

    driver = None
    datos_finales = []

    try:
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)

        for categoria_nombre, url_categoria in CATEGORIAS.items():
            print(f"\n========== Categoría: {categoria_nombre} ==========")
            driver.get(url_categoria)
            time.sleep(5)

            for num_pagina in range(1, LIMITE_PAGINAS + 1):
                print(f"  --- Página {num_pagina} ---")

                try:
                    WebDriverWait(driver, 15).until(
                        EC.presence_of_all_elements_located(
                            (By.CSS_SELECTOR, "a.gb-results-list__item")
                        )
                    )
                except Exception:
                    print("  Sin resultados en esta pagina, saltando categoria.")
                    break

                tarjetas = driver.find_elements(By.CSS_SELECTOR, "a.gb-results-list__item")
                print(f"  Ofertas encontradas: {len(tarjetas)}")

                for tarjeta in tarjetas:
                    try:
                        # --- TÍTULO DEL CARGO ---
                        try:
                            titulo_cargo = tarjeta.find_element(
                                By.CSS_SELECTOR, "h2.gb-results-list__title strong"
                            ).text.strip()
                        except:
                            titulo_cargo = "No especificado"

                        # --- EMPRESA ---
                        try:
                            empresa = tarjeta.find_element(
                                By.CSS_SELECTOR, "p.gb-results-list__company"
                            ).text.strip()
                            if not empresa:
                                raise ValueError
                        except:
                            try:
                                empresa = tarjeta.find_element(
                                    By.CSS_SELECTOR, ".gb-results-list__secondary p"
                                ).text.strip()
                            except:
                                empresa = "No especificada"

                        # --- TIPO DE HORARIO ---
                        try:
                            tipo_horario = tarjeta.find_element(
                                By.CSS_SELECTOR, "h2.gb-results-list__title span.opacity-half"
                            ).text.strip()
                        except:
                            tipo_horario = "No especificado"

                        # --- MODALIDAD Y PAÍS ---
                        try:
                            location_text = tarjeta.find_element(
                                By.CSS_SELECTOR, "span.location"
                            ).text.strip()
                            if "Remote" in location_text or "Remoto" in location_text:
                                modalidad = "Remoto"
                            elif "Hybrid" in location_text or "Híbrido" in location_text:
                                modalidad = "Híbrido"
                            else:
                                modalidad = "Presencial"
                            match = re.search(r'\(([^)]+)\)', location_text)
                            pais = match.group(1) if match else location_text
                        except:
                            modalidad = "No especificada"
                            pais = "No especificado"

                        # --- FECHA DE PUBLICACIÓN ---
                        try:
                            fecha_publicacion = tarjeta.find_element(
                                By.CSS_SELECTOR,
                                ".gb-results-list__secondary .opacity-half.size0"
                            ).text.strip()
                        except:
                            fecha_publicacion = "No especificada"

                        # --- DESCRIPCIÓN ---
                        try:
                            descripcion = tarjeta.find_element(
                                By.CSS_SELECTOR, "p.gb-results-list__description"
                            ).text.strip()
                            if not descripcion:
                                raise ValueError
                        except:
                            try:
                                descripcion = tarjeta.find_element(
                                    By.CSS_SELECTOR, ".gb-results-list__body p"
                                ).text.strip()
                            except:
                                descripcion = "No disponible en listado"

                        registro = {
                            "titulo_cargo"      : titulo_cargo,
                            "empresa"           : empresa,
                            "pais"              : pais,
                            "modalidad"         : modalidad,
                            "tipo_horario"      : tipo_horario,
                            "fecha_publicacion" : fecha_publicacion,
                            "fecha_captura"     : time.strftime("%Y-%m-%d %H:%M:%S"),
                            "descripcion"       : descripcion,
                            "categoria"         : categoria_nombre,
                            "grupo"             : NOMBRE_GRUPO
                        }
                        datos_finales.append(registro)

                    except Exception as e:
                        print(f"  Advertencia en tarjeta: {e}")
                        continue

                if num_pagina < LIMITE_PAGINAS:
                    try:
                        siguiente = driver.find_element(By.CSS_SELECTOR, "a[rel='next']")
                        siguiente.click()
                        time.sleep(3)
                    except:
                        print("  No hay más páginas en esta categoría.")
                        break

        print(f"\nExtracción finalizada. Total: {len(datos_finales)} registros")

    except Exception as e:
        print(f"Error: {e}")

    finally:
        if driver:
            driver.quit()
            print("\nNavegador cerrado.")

    # ================================================
    # CONEXIÓN A MONGODB
    # ================================================
    MONGO_URI ="mongodb+srv://BenjaminRamirez:fim5S0MTo17YVRw0@cluster0.kek1o3u.mongodb.net/?retryWrites=true&w=majority"

    try:
        client = MongoClient(MONGO_URI, tlsCAFile=certifi.where())
        db = client['Proyecto_Bigdata']
        coleccion = db['Registros_Scraping']
        print("CONEXIÓN ESTABLECIDA.")
    except Exception as e:
        print("ERROR DE CONEXIÓN:", e)
        return datos_finales

    exitosos = 0
    fallidos  = 0

    for dato in datos_finales:
        try:
            coleccion.insert_one(dato)
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
    mis_datos = ejecutar_extraccion()
    # print(mis_datos)
