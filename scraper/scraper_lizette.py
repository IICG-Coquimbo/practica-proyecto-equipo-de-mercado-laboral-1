import requests
from bs4 import BeautifulSoup
import time
import random
import certifi
from pymongo import MongoClient

def ejecutar_extraccion_final_lizette():
    NOMBRE_INTEGRANTE = "Lizette-Sanmartin"
    META_DATOS = 500
    datos_finales = []
    empleos_vistos = set()
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        "Referer": "https://www.google.com/"
    }

    print(f"Iniciando extracción SEGURA: {NOMBRE_INTEGRANTE}...")
    
    pagina = 1
    while len(datos_finales) < META_DATOS:
        # URL de Computrabajo ajustada para ser fácil de leer
        url = f"https://www.computrabajo.cl/ofertas-de-trabajo/?p={pagina}"
        
        try:
            res = requests.get(url, headers=headers, timeout=30, verify=certifi.where())
            
            if res.status_code != 200:
                print(f"Status {res.status_code}. Cambia a los datos de tu celular ahora.")
                break
            
            soup = BeautifulSoup(res.text, 'html.parser')
            # Buscamos los artículos de ofertas
            ofertas = soup.find_all('article', class_='box_offer')

            if not ofertas: break

            for oferta in ofertas:
                if len(datos_finales) >= META_DATOS: break
                
                try:
                    titulo = oferta.find('h1') or oferta.find('h2')
                    titulo_txt = titulo.get_text(strip=True)
                    
                    # Empresa y Ciudad
                    empresa = "Confidencial"
                    emp_tag = oferta.find('a', class_='fc_base')
                    if emp_tag: empresa = emp_tag.get_text(strip=True)
                    
                    ciudad = "Chile"
                    ciu_tag = oferta.find('span', class_='mr10')
                    if ciu_tag: ciudad = ciu_tag.get_text(strip=True)

                    huella = f"{titulo_txt}-{empresa}".lower()
                    if huella not in empleos_vistos:
                        datos_finales.append({
                            "Titulo del cargo": titulo_txt,
                            "País": "Chile",
                            "Modalidad de trabajo": "Presencial",
                            "Fecha": time.strftime("%d/%m/%Y"),
                            "Tipo de moneda": "CLP",
                            "Categoría de empleo": "Varios",
                            "Tipo de horario (Extra)": "Jornada Completa",
                            "Empresa": empresa,
                            "Integrante": NOMBRE_INTEGRANTE,
                            "Ciudad": ciudad
                        })
                        empleos_vistos.add(huella)
                except: continue
            
            print(f"Progreso: {len(datos_finales)}/500")
            pagina += 1
            time.sleep(random.uniform(2, 4))
            
        except: break

    if datos_finales:
        uri = "mongodb+srv://BenjaminRamirez:fim5S0MTo17YVRw0@cluster0.kek1o3u.mongodb.net/?retryWrites=true&w=majority"
        try:
            client = MongoClient(uri, tlsCAFile=certifi.where())
            db = client["TiendaBigData"]
            coleccion = db["Computrabajo_Lizette"]
            coleccion.delete_many({"Integrante": NOMBRE_INTEGRANTE})
            coleccion.insert_many(datos_finales)
            print(f"¡LOGRADO! {len(datos_finales)} registros en tu Atlas.")
        except Exception as e:
            print(f"Error Mongo: {e}")

    return datos_finales