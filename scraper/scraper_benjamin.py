import os
import time
from pymongo import MongoClient, UpdateOne
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

def ejecutar_extraccion():
    """
    Función estandarizada para el Hito 1 de Big Data.
    Extrae 500 registros de ChileTrabajos y los retorna en una lista.
    """
    # --- CONFIGURACIÓN DE GOBERNANZA ---
    NOMBRE_INTEGRANTE = "Benjamin Ramirez" # Tu identificador para el merge final
    META_DATOS = 500
    datos_finales = []
    
    # --- CONFIGURACIÓN DEL NAVEGADOR ---
    options = Options()
    options.binary_location = "/usr/bin/google-chrome"
    options.add_argument("--headless") # Modo invisible para el servidor
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1920,1080")
    
    # Inicialización del Driver con el Manager (Solución de seguridad)
    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()), 
        options=options
    )

    try:
        driver.get("https://www.chiletrabajos.cl/encuentra-un-empleo?2=informatica")
        
        while len(datos_finales) < META_DATOS:
            time.sleep(8) # Pausa para renderizado dinámico

            # Espera explícita a los bloques de empleo
            WebDriverWait(driver, 20).until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div[class*='job-item']"))
            )
            
            bloques = driver.find_elements(By.CSS_SELECTOR, "div[class*='job-item']")

            for bloque in bloques:
                if len(datos_finales) >= META_DATOS:
                    break
                try:
                    # Extracción de etiquetas según rúbrica (8 campos)
                    titulo = bloque.find_element(By.TAG_NAME, "h2").text.strip()
                    empresa = bloque.find_element(By.TAG_NAME, "h3").text.strip()
                    texto_tarjeta = bloque.text.lower()

                    # Lógica de clasificación
                    modalidad = "Teletrabajo" if "teletrabajo" in texto_tarjeta else "Presencial"
                    horario = "Part-time" if "part time" in texto_tarjeta else "Full-time"
                    moneda = "USD" if "usd" in texto_tarjeta else "CLP"

                    datos_finales.append({
                        "identificador": titulo,           # Campo requerido por el manual
                        "empresa": empresa,
                        "valor": 0.0,                      # Spark lo limpiará después
                        "modalidad": modalidad,
                        "tipo_horario": horario,
                        "moneda": moneda,
                        "pais": "Chile",
                        "integrante": NOMBRE_INTEGRANTE,   # Gobernanza: Quién subió el dato
                        "fecha_captura": time.strftime("%Y-%m-%d %H:%M:%S")
                    })
                except:
                    continue

            # Paginación
            try:
                btn_sig = driver.find_element(By.PARTIAL_LINK_TEXT, "Siguiente")
                driver.execute_script("arguments[0].click();", btn_sig)
            except:
                break # No hay más páginas

    finally:
        driver.quit()

    return datos_finales # Indispensable para que Spark lo reciba [cite: 1472, 1553]

# --- BLOQUE DE EJECUCIÓN (PRUEBA LOCAL) ---
if __name__ == "__main__":
    print("Iniciando extracción individual...")
    resultados = ejecutar_extraccion()
    print(f"Se capturaron {len(resultados)} registros.")
    
    # Aquí puedes agregar tu lógica de conexión a Atlas para guardar el avance individual

    