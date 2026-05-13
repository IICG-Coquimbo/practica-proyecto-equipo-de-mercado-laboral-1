import os
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

# Limpieza absoluta de memoria
os.system('pkill -9 chrome')
os.system('pkill -9 chromedriver')
os.environ['DISPLAY'] = ':99'

# ================================================
# CONFIGURACIÓN
# ================================================
NOMBRE_GRUPO   = "Benjamin-Ramirez"
META_REGISTROS = 500  
LIMITE_PAGINAS = 15   

# Lista de categorías para buscar orgánicamente
CATEGORIAS = [
    "informatica", "administracion", "ventas", "comercial", "bodega",
    "logistica", "secretaria", "recepcion", "contabilidad", "finanzas",
    "recursos humanos", "marketing", "salud", "educacion", "ingenieria",
    "construccion", "transporte", "gastronomia", "turismo", "retail",
    "juridico", "diseno", "comunicaciones", "agricultura", "mineria",
    "manufactura", "seguridad", "limpieza", "telecomunicaciones", "farmacia"
]
# ================================================

def ejecutar_extraccion():
    options = Options()
    options.binary_location = "/usr/bin/google-chrome"
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--headless=new") 
    options.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    )

    driver = None
    datos_finales = []
    empleos_vistos = set() 

    try:
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
        driver.set_page_load_timeout(30)

        for categoria in CATEGORIAS:
            if len(datos_finales) >= META_REGISTROS: break
                
            print(f"\n========== Explorando Categoría: {categoria.capitalize()} ==========")
            
            paginas_vacias_consecutivas = 0 # Contador para atravesar los destacados

            # Iteramos usando el parámetro 2= (Búsqueda por Cargo/Palabra clave)
            for num_pagina in range(1, LIMITE_PAGINAS + 1):
                if len(datos_finales) >= META_REGISTROS: break

                url_paginada = f"https://www.chiletrabajos.cl/encuentra-un-empleo?2={categoria.replace(' ', '+')}&f={num_pagina}"
                
                try:
                    driver.get(url_paginada)
                    time.sleep(2) 
                except Exception as e:
                    print(f"  Timeout en página {num_pagina}, forzando la siguiente...")
                    continue

                try:
                    WebDriverWait(driver, 10).until(
                        EC.presence_of_all_elements_located((By.CLASS_NAME, "job-item"))
                    )
                    tarjetas = driver.find_elements(By.CLASS_NAME, "job-item")
                except:
                    print("  Fin de resultados orgánicos en esta categoría.")
                    break 

                nuevos_en_pagina = 0

                for tarjeta in tarjetas:
                    if len(datos_finales) >= META_REGISTROS: break

                    try:
                        titulo_cargo = tarjeta.find_element(By.TAG_NAME, "h2").text.strip()
                        empresa = tarjeta.find_element(By.TAG_NAME, "h3").text.strip()

                        # HUELLA ESTRICTA PARA IGNORAR DUPLICADOS
                        huella = f"{titulo_cargo}-{empresa}".lower()
                        if huella in empleos_vistos: continue 

                        try:
                            descripcion = tarjeta.find_element(By.TAG_NAME, "p").text.strip()
                        except:
                            descripcion = "No especificado"

                        texto_tarjeta = tarjeta.text.lower()
                        modalidad = "Remoto" if "remoto" in texto_tarjeta else "Presencial"
                        tipo_horario = "Part time" if "part time" in texto_tarjeta else "Full time"

                        try:
                            fecha_publicacion = tarjeta.find_element(By.CLASS_NAME, "fechap").text.strip()
                        except:
                            fecha_publicacion = "Reciente"

                        # SE AGREGA LA ETIQUETA "grupo" REQUERIDA POR EL CAPÍTULO 8
                        registro = {
                            "Titulo de Cargo"      : titulo_cargo,
                            "Empresa"              : empresa,
                            "Pais"                 : "Chile",
                            "Fecha de Captura"     : time.strftime("%Y-%m-%d %H:%M:%S"),
                            "Descripcion"          : descripcion,
                            "Modalidad"            : modalidad,
                            "Tipo de Horario"      : tipo_horario,
                            "Fecha de Publicacion" : fecha_publicacion,
                            "grupo"                : NOMBRE_GRUPO 
                        }
                        
                        datos_finales.append(registro)
                        empleos_vistos.add(huella) 
                        nuevos_en_pagina += 1

                    except Exception as e:
                        continue
                
                print(f"  --- Página {num_pagina}: {nuevos_en_pagina} nuevos | Total acumulado: {len(datos_finales)} ---")
                
                # --- LÓGICA DE SALTO ---
                if nuevos_en_pagina == 0:
                    paginas_vacias_consecutivas += 1
                else:
                    paginas_vacias_consecutivas = 0

                # Solo saltamos de categoría si llevamos 5 PÁGINAS SEGUIDAS leyendo puros duplicados
                if paginas_vacias_consecutivas >= 5:
                    print("  Demasiadas páginas seguidas de Anuncios Destacados repetidos. Pasando a la siguiente categoría...")
                    break

        print(f"\n¡EXTRACCIÓN FINALIZADA! Total registros únicos listos en memoria: {len(datos_finales)}")

    except Exception as e:
        print(f"Error principal: {e}")

    finally:
        if driver:
            driver.quit()
            print("\nNavegador cerrado.")
            
    # RETORNO DE DATOS OBLIGATORIO PARA QUE SPARK PUEDA CONSTRUIR EL DATAFRAME
    return datos_finales

# Si deseas probar el código localmente de forma independiente antes de subirlo, puedes usar esto:
if __name__ == "__main__":
    mis_datos = ejecutar_extraccion()
    # print(mis_datos)