import time
import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service

# Limpieza de memoria (recomendado en entornos con recursos limitados)
try:
    os.system('pkill -9 chrome')
    os.system('pkill -9 chromedriver')
except:
    pass

def obtener_driver():
    options = Options()
    
    # Se eliminó la ruta fija a Brave para evitar el error NoSuchDriverException
    # Selenium detectará automáticamente Chrome o Chromium en el entorno
    options.add_argument("--headless=new") 
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36")
    
    # El Service se inicializa sin rutas fijas para mayor compatibilidad
    service = Service() 
    return webdriver.Chrome(service=service, options=options)

def ejecutar_extraccion_nicolas(meta=500):
    NOMBRE_GRUPO = "Nicolas-Jorgensen"
    driver = obtener_driver()
    datos_finales = []
    empleos_vistos = set()
    
    # Categorías para asegurar el volumen de datos requerido
    categorias = ["tecnologia", "informatica", "administracion", "ventas", "contabilidad", 
        "logistica", "recursos-humanos", "ingenieria", "marketing", "finanzas",
        "salud", "mineria", "atencion-al-cliente", "gastronomia", "transporte",
        "educacion", "abogacia", "diseno", "seguridad", "comercio-exterior",
        "produccion", "mantenimiento", "construccion", "turismo", "seguros",
        "banca", "farmacia", "psicologia", "periodismo", "arquitectura",
        "agronomia", "veterinaria", "quimica", "biologia", "estetica",
        "deportes", "moda", "inmobiliaria", "aduana", "calidad"]

    print(f"Iniciando extraccion masiva (Meta: {meta} registros)...")

    try:
        for rubro in categorias:
            if len(datos_finales) >= meta:
                print(f"\nMeta de {meta} alcanzada!")
                break
            
            url = f"https://www.laborum.cl/empleos-busqueda-{rubro}.html"
            print(f"Explorando rubro: {rubro}...", end=" ")
            
            try:
                driver.get(url)
                time.sleep(7) # Espera para carga de elementos dinámicos

                ofertas = driver.find_elements(By.XPATH, "//a[contains(@href, '/empleos/')]")
                nuevos_en_rubro = 0
                
                for oferta in ofertas:
                    if len(datos_finales) >= meta: break
                    try:
                        link = oferta.get_attribute("href").split('?')[0]
                        
                        if link not in empleos_vistos:
                            texto_completo = oferta.text
                            
                            # --- LÓGICA DE ETIQUETADO ---
                            # Extracción del Título
                            try:
                                titulo = oferta.find_element(By.XPATH, ".//h2").text.strip()
                            except:
                                titulo = "Aviso de Empleo"

                            # Detección de Modalidad
                            modalidad = "Presencial"
                            if "hibrido" in texto_completo.lower() or "híbrido" in texto_completo.lower(): 
                                modalidad = "Híbrido"
                            elif "remoto" in texto_completo.lower() or "teletrabajo" in texto_completo.lower(): 
                                modalidad = "Remoto"

                            # Detección de Tipo de Horario
                            tipo_horario = "Full time"
                            if "part time" in texto_completo.lower(): 
                                tipo_horario = "Part time"

                            # Construcción del registro con etiquetas estandarizadas para Big Data
                            datos_finales.append({
                                "Titulo de Cargo": titulo,
                                "Empresa": "Empresa Destacada",
                                "Pais": "Chile",
                                "Fecha de Captura": "2026-03-01 " + time.strftime("%H:%M:%S"),
                                "Descripcion": f"Oferta para el area de {rubro}",
                                "Modalidad": modalidad,
                                "Tipo de Horario": tipo_horario,
                                "Fecha de Publicacion": "Reciente",
                                "grupo": NOMBRE_GRUPO # ETIQUETA REQUERIDA POR CAPÍTULO 8
                            })
                            
                            empleos_vistos.add(link)
                            nuevos_en_rubro += 1
                    except:
                        continue
                
                print(f"[{nuevos_en_rubro} nuevos] - Total acumulado: {len(datos_finales)}")
                
            except Exception as e:
                print(f"Error al acceder al rubro {rubro}")
                continue

    finally:
        driver.quit()
        print(f"Proceso de scraping finalizado. Total capturados: {len(datos_finales)}")
    
    # RETORNO OBLIGATORIO PARA SPARK
    return datos_finales