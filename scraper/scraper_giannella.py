import requests
from bs4 import BeautifulSoup
import time
import random
import certifi
from pymongo import MongoClient
import datetime

# 1. DEFINICIÓN DE LA FUNCIÓN
def ejecutar_extraccion_final_giannella_rieu():
    # --- CONFIGURACIÓN ---
    NOMBRE_INTEGRANTE = "Giannella-Rieu"
    META_DATOS = 500
    datos_finales = []
    empleos_vistos = set()
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        "Referer": "https://www.google.com/"
    }

    print(f"🚀 Iniciando extracción SEGURA: {NOMBRE_INTEGRANTE} en LinkedIn...")
    
    start = 0
    while len(datos_finales) < META_DATOS:
        url = f"https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search?keywords=trabajo&location=Chile&start={start}"
        
        try:
            res = requests.get(url, headers=headers, timeout=30, verify=certifi.where())
            
            if res.status_code != 200:
                print(f"⚠️ Status {res.status_code}. Posible bloqueo temporal, intentando saltar...")
                break
            
            soup = BeautifulSoup(res.text, 'html.parser')
            ofertas = soup.find_all('li')

            for oferta in ofertas:
                if len(datos_finales) >= META_DATOS: break
                
                try:
                    titulo_tag = oferta.find(['h3', 'h4'])
                    if not titulo_tag: continue
                    titulo_txt = titulo_tag.get_text(strip=True)
                    
                    empresa_tag = oferta.find('h4', class_=lambda x: x and 'subtitle' in x)
                    empresa = empresa_tag.get_text(strip=True) if empresa_tag else "Confidencial"
                    
                    ciudad_tag = oferta.find('span', class_=lambda x: x and 'location' in x)
                    ciudad = ciudad_tag.get_text(strip=True) if ciudad_tag else "Chile"

                    if len(titulo_txt) > 5:
                        huella = f"{titulo_txt}-{empresa}".lower()
                        if huella not in empleos_vistos:
                            datos_finales.append({
                                "Titulo del cargo": titulo_txt,
                                "País": "Chile",
                                "Modalidad de trabajo": "Presencial",
                                "Fecha": time.strftime("%d/%m/%Y"),
                                "Tipo de moneda": "CLP",
                                "Categoría de empleo": "General",
                                "Tipo de horario (Extra)": "Jornada Completa",
                                "Empresa": empresa,
                                "Integrante": NOMBRE_INTEGRANTE,
                                "Ciudad": ciudad
                            })
                            empleos_vistos.add(huella)
                except:
                    continue
            
            print(f"📊 Progreso: {len(datos_finales)}/500")
            
            if not ofertas or start > 1000: break
            
            start += 25 
            time.sleep(random.uniform(4, 7)) # Pausa para evitar que LinkedIn nos bloquee
            
        except Exception as e:
            print(f"❌ Error: {e}")
            break

    # ENVÍO AL ATLAS (Base de datos de Benjamín)
    if datos_finales:
        uri = "mongodb+srv://BenjaminRamirez:fim5S0MTo17YVRw0@cluster0.kek1o3u.mongodb.net/?retryWrites=true&w=majority"
        try:
            client = MongoClient(uri, tlsCAFile=certifi.where())
            db = client["TiendaBigData"]
            coleccion = db["LinkedIn_GiannellaRieu"]
            
            coleccion.delete_many({"Integrante": NOMBRE_INTEGRANTE})
            coleccion.insert_many(datos_finales)
            print(f"\n✅ --- ¡ÉXITO! Se cargaron {len(datos_finales)} registros ---")
        except Exception as e:
            print(f"❌ Error Mongo: {e}")

    return datos_finales

# 2. EJECUCIÓN DEL CÓDIGO
print(f"🔔 Proceso iniciado a las: {datetime.datetime.now().strftime('%H:%M:%S')}")

# Aquí es donde se "llama" a la función definida arriba
mis_datos = ejecutar_extraccion_final_giannella_rieu()

print(f"🔔 Proceso finalizado a las: {datetime.datetime.now().strftime('%H:%M:%S')}")