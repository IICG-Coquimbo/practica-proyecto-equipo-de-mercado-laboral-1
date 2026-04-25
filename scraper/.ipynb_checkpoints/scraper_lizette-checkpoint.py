import requests
from bs4 import BeautifulSoup
import time
import certifi
from pymongo import MongoClient

def ejecutar_extraccion_final_lizette():
    NOMBRE_INTEGRANTE = "Lizette-Sanmartin"
    META_DATOS = 500
    datos_finales = []
    empleos_vistos = set()
    
    # Headers mucho más completos para parecer un navegador real
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
        "Accept-Language": "es-ES,es;q=0.9",
        "Referer": "https://www.google.com/"
    }

    print(f"Iniciando extracción: {NOMBRE_INTEGRANTE} (Camuflaje activado)...")
    
    # Usamos una sesión para mantener las cookies y parecer más "humanos"
    session = requests.Session()
    
    pagina = 1
    while len(datos_finales) < META_DATOS:
        # Probamos con la URL directa de búsqueda por fecha para que refresque datos
        url = f"https://acciontrabajo.cl/buscar-empleos-en-chile?page={pagina}&sort=date"
        
        try:
            response = session.get(url, headers=headers, timeout=25, verify=certifi.where())
            
            if response.status_code != 200:
                print(f"Bloqueo detectado (Código {response.status_code}). Reintentando con pausa...")
                time.sleep(10)
                continue
                
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Buscador omnívoro de ofertas
            ofertas = soup.find_all(['div', 'article'], class_=lambda x: x and any(c in x.lower() for c in ['job', 'item', 'card']))
            
            if not ofertas:
                # Si no hay clases, buscamos todos los h2 con links
                ofertas = soup.find_all('h2')

            for oferta in ofertas:
                if len(datos_finales) >= META_DATOS: break
                
                try:
                    # Buscamos el link y el texto del título
                    tag_a = oferta.find('a') if oferta.name != 'h2' else oferta.find('a')
                    if not tag_a: continue
                    
                    titulo = tag_a.get_text(strip=True)
                    if len(titulo) < 5: continue

                    # Empresa y Ciudad (Buscamos etiquetas strong o mark)
                    empresa = "Empresa Confidencial"
                    emp_tag = oferta.find_next(['mark', 'strong', 'b'])
                    if emp_tag: empresa = emp_tag.get_text(strip=True)
                    
                    ciudad = "Chile"
                    ciu_tag = oferta.find_next('span', string=lambda x: x and any(r in x.lower() for r in ['región', 'santiago', 'chile']))
                    if ciu_tag: ciudad = ciu_tag.get_text(strip=True)

                    huella = f"{titulo}-{empresa}".lower()
                    if huella not in empleos_vistos:
                        datos_finales.append({
                            "Titulo del cargo": titulo,
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
            
            print(f"Página {pagina}: {len(datos_finales)}/500")
            
            if len(ofertas) == 0: break
            
            pagina += 1
            time.sleep(3) # Pausa más larga para no levantar sospechas
            
        except Exception as e:
            print(f"Error de conexión: {e}")
            time.sleep(5)
            break

    # ENVÍO AL CLUSTER DE BENJAMÍN
    if datos_finales:
        uri = "mongodb+srv://BenjaminRamirez:fim5S0MTo17YVRw0@cluster0.kek1o3u.mongodb.net/?retryWrites=true&w=majority"
        try:
            client = MongoClient(uri, tlsCAFile=certifi.where())
            db = client["TiendaBigData"]
            coleccion = db["AccionTrabajo_Lizette"]
            coleccion.delete_many({"Integrante": NOMBRE_INTEGRANTE})
            coleccion.insert_many(datos_finales)
            print(f"¡LOGRADO! {len(datos_finales)} registros en tu Atlas.")
        except Exception as e:
            print(f"Error Mongo: {e}")

    return datos_finales