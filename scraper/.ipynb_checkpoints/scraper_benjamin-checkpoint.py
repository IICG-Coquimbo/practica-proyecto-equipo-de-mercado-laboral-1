import time
import certifi
import os
from pymongo import MongoClient
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.core.os_manager import ChromeType

def ejecutar_extraccion():
    # --- CONFIGURACION ---
    NOMBRE_INTEGRANTE = "Benjamin-Ramirez" 
    META_DATOS = 500 
    datos_finales = []
    empleos_vistos = set() 
    
    # Lista de categorías para obtener 500 datos rápidos sin usar paginación
    categorias = [
        "informatica", "administracion", "ventas", "comercial", "bodega", 
        "logistica", "secretaria", "recepcion", "contabilidad", "finanzas",
        "recursos-humanos", "marketing", "salud", "educacion", "ingenieria",
        "construccion", "transporte", "conductor", "seguridad", "limpieza"
    ]
    
    options = Options()
    options.binary_location = "/usr/bin/brave-browser" 
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1920,1080")
    
    try:
        path = ChromeDriverManager(chrome_type=ChromeType.BRAVE).install()
        service = Service(path)
    except Exception:
        service = Service("/usr/bin/chromedriver") if os.path.exists("/usr/bin/chromedriver") else Service()

    driver = webdriver.Chrome(service=service, options=options)

    try:
        print(f"Iniciando extracción multi-categoría para {NOMBRE_INTEGRANTE}...")
        
        for rubro in categorias:
            if len(datos_finales) >= META_DATOS:
                break
                
            # Navegamos por categoría en lugar de por página
            url = f"https://www.chiletrabajos.cl/encuentra-un-empleo?2={rubro}"
            print(f"Explorando categoría: {rubro}...")
            driver.get(url)
            time.sleep(6) # Tiempo para carga

            bloques = driver.find_elements(By.CLASS_NAME, "job-item")
            
            for bloque in bloques:
                if len(datos_finales) >= META_DATOS:
                    break
                try:
                    titulo = bloque.find_element(By.TAG_NAME, "h2").text.strip()
                    empresa = bloque.find_element(By.TAG_NAME, "h3").text.strip()
                    
                    # Filtro de duplicados
                    huella = f"{titulo}-{empresa}".lower()

                    if huella not in empleos_vistos:
                        datos_finales.append({
                            "identificador": titulo,
                            "empresa": empresa,
                            "pais": "Chile",
                            "integrante": NOMBRE_INTEGRANTE,
                            "fecha_captura": time.strftime("%Y-%m-%d %H:%M:%S")
                        })
                        empleos_vistos.add(huella)
                except:
                    continue

            print(f"Acumulados: {len(datos_finales)}/500")

    finally:
        driver.quit()

    # --- ENVÍO A MONGODB ATLAS ---
    if datos_finales:
        uri = "mongodb+srv://BenjaminRamirez:fim5S0MTo17YVRw0@cluster0.kek1o3u.mongodb.net/?retryWrites=true&w=majority"
        try:
            client = MongoClient(uri, tlsCAFile=certifi.where())
            db = client["TiendaBigData"]
            coleccion = db["ChileTrabajos_Benjamin"]
            
            print("Limpiando registros previos en Atlas...")
            coleccion.delete_many({"integrante": NOMBRE_INTEGRANTE})
            
            resultado = coleccion.insert_many(datos_finales)
            print(f"¡LOGRADO! Se guardaron {len(resultado.inserted_ids)} registros ÚNICOS en Atlas.")
        except Exception as e:
            print(f"Error al conectar con Atlas: {e}")

    return datos_finales