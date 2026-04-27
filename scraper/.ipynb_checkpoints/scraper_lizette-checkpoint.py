import requests
from bs4 import BeautifulSoup
import time
import random
import certifi
from pymongo import MongoClient

def ejecutar_extraccion_final_lizette():
    # --- CONFIGURACIÓN IDÉNTICA A COMPUTRABAJO ---
    NOMBRE_INTEGRANTE = "Lizette-Sanmartin"
    META_DATOS = 500
    datos_finales = []
    empleos_vistos = set()
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        "Referer": "https://www.google.com/"
    }

    print(f"Iniciando extracción SEGURA: {NOMBRE_INTEGRANTE} en LinkedIn...")
    
    # LinkedIn usa 'start' para paginar (0, 25, 50...)
    start = 0
    while len(datos_finales) < META_DATOS:
        # URL de búsqueda de LinkedIn Chile
        url = f"https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search?keywords=trabajo&location=Chile&start={start}"
        
        try:
            res = requests.get(url, headers=headers, timeout=30, verify=certifi.where())
            
            if res.status_code != 200:
                print(f"Status {res.status_code}. Intentando saltar...")
                break
            
            soup = BeautifulSoup(res.text, 'html.parser')
            
            # --- CAPTURA DE BLOQUES ---
            # LinkedIn usa etiquetas 'li' para cada trabajo
            ofertas = soup.find_all('li')

            for oferta in ofertas:
                if len(datos_finales) >= META_DATOS: break
                
                try:
                    # Título del cargo (clase base-search-card__title)
                    titulo_tag = oferta.find(['h3', 'h4'])
                    if not titulo_tag: continue
                    titulo_txt = titulo_tag.get_text(strip=True)
                    
                    # Empresa y Ciudad
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
            
            print(f"Progreso: {len(datos_finales)}/500")
            
            if not ofertas or start > 1000: break
            
            start += 25 # LinkedIn avanza de 25 en 25
            time.sleep(random.uniform(3, 6)) # Pausa humana
            
        except Exception as e:
            print(f"Error: {e}")
            break

    # ENVÍO AL ATLAS
    if datos_finales:
        uri = "mongodb+srv://BenjaminRamirez:fim5S0MTo17YVRw0@cluster0.kek1o3u.mongodb.net/?retryWrites=true&w=majority"
        try:
            client = MongoClient(uri, tlsCAFile=certifi.where())
            db = client["TiendaBigData"]
            coleccion = db["LinkedIn_Lizette"]
            coleccion.delete_many({"Integrante": NOMBRE_INTEGRANTE})
            coleccion.insert_many(datos_finales)
            print(f"--- ¡ÉXITO! Se cargaron {len(datos_finales)} registros ---")
        except Exception as e:
            print(f"Error Mongo: {e}")

    return datos_finales