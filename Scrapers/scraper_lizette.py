import os
import time
import random
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from Scrapers.utils import obtener_driver

# ================================================
# CONFIGURACIÓN
# ================================================
NOMBRE_GRUPO   = "Lizette-Sanmartin"
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

def ejecutar_extraccion_lizette():
    driver = None
    datos_finales = []
    empleos_vistos = set()

    try:
        driver = obtener_driver()
        driver.set_page_load_timeout(30)

        for categoria in CATEGORIAS:
            if len(datos_finales) >= META_REGISTROS: break
                
            print(f"\n========== Explorando Categoria: {categoria.capitalize()} ==========")
            
            paginas_vacias_consecutivas = 0

            # Iteramos usando el parámetro ?q= (Búsqueda por Cargo/Palabra clave en Computrabajo)
            for num_pagina in range(1, LIMITE_PAGINAS + 1):
                if len(datos_finales) >= META_REGISTROS: break

                termino_busqueda = categoria.replace(' ', '+')
                url_paginada = f"https://cl.computrabajo.com/ofertas-de-trabajo/?q={termino_busqueda}&p={num_pagina}"
                
                try:
                    driver.get(url_paginada)
                    time.sleep(random.uniform(2.5, 4.0)) # Pausa dinámica para simular usuario
                    # Scroll para cargar lazy-loads
                    driver.execute_script("window.scrollTo(0, document.body.scrollHeight/2);")
                    time.sleep(1)
                except Exception as e:
                    print(f"  Timeout en pagina {num_pagina}, forzando la siguiente...")
                    continue

                try:
                    # Computrabajo envuelve sus ofertas en la etiqueta article
                    WebDriverWait(driver, 10).until(
                        EC.presence_of_all_elements_located((By.CSS_SELECTOR, "article.box_offer"))
                    )
                    tarjetas = driver.find_elements(By.CSS_SELECTOR, "article.box_offer")
                except:
                    print("  Fin de resultados organicos o bloqueo temporal superado. Siguiente categoria.")
                    break 

                nuevos_en_pagina = 0

                for tarjeta in tarjetas:
                    if len(datos_finales) >= META_REGISTROS: break

                    try:
                        texto_tarjeta = tarjeta.text
                        if not texto_tarjeta: continue

                        # En Computrabajo el título suele estar en el primer enlace fuerte de la tarjeta
                        enlace_tag = tarjeta.find_element(By.TAG_NAME, "a")
                        titulo_cargo = enlace_tag.text.strip()
                        
                        try:
                            empresa = tarjeta.find_element(By.CSS_SELECTOR, "[class*='fc_base']").text.strip()
                        except:
                            empresa = "Confidencial"

                        # HUELLA ESTRICTA PARA IGNORAR DUPLICADOS
                        huella = f"{titulo_cargo}-{empresa}".lower()
                        if huella in empleos_vistos: continue 

                        try:
                            descripcion = tarjeta.find_element(By.CSS_SELECTOR, "p[class*='sh_m']").text.strip()
                        except:
                            descripcion = texto_tarjeta[:150].replace('\n', ' ') + "..."

                        # Minería del texto para modalidad y horario
                        texto_lower = texto_tarjeta.lower()
                        modalidad = "Remoto" if any(x in texto_lower for x in ["remoto", "teletrabajo"]) else "Presencial"
                        if "híbrido" in texto_lower or "hibrido" in texto_lower: modalidad = "Híbrido"
                        
                        tipo_horario = "Part time" if any(x in texto_lower for x in ["part time", "medio tiempo", "parcial"]) else "Full time"

                        try:
                            fecha_publicacion = tarjeta.find_element(By.CSS_SELECTOR, "p[class*='fc_aux']").text.strip()
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
                
                print(f"  --- Pagina {num_pagina}: {nuevos_en_pagina} nuevos | Total acumulado: {len(datos_finales)} ---")
                
                # --- LÓGICA DE SALTO ---
                if nuevos_en_pagina == 0:
                    paginas_vacias_consecutivas += 1
                else:
                    paginas_vacias_consecutivas = 0

                if paginas_vacias_consecutivas >= 5:
                    print("  Demasiadas paginas seguidas de ofertas repetidas o vacias. Pasando a la siguiente categoria...")
                    break

        print(f"\nEXTRACCION FINALIZADA. Total registros unicos listos en memoria: {len(datos_finales)}")

    except Exception as e:
        print(f"Error principal: {e}")

    finally:
        if driver:
            driver.quit()
            print("Navegador cerrado.")
            
    # RETORNO DE DATOS OBLIGATORIO PARA QUE SPARK PUEDA CONSTRUIR EL DATAFRAME
    return datos_finales

# Si deseas probar el código de Lizette localmente:
if __name__ == "__main__":
    datos_prueba = ejecutar_extraccion_lizette()
    # print(f"Se capturaron {len(datos_prueba)} registros.")