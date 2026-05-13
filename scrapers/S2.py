import time
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def scraper_kiwoko(driver, By, paginas=1):
    datos_tienda = []
    base_url = "https://www.kiwoko.com/perros/comida-para-perros/dietas-veterinarias/"
    wait = WebDriverWait(driver, 20)

    for p in range(1, paginas + 1):
        url = f"{base_url}?p={p}" if p > 1 else base_url
        try:
            driver.get(url)
            wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "div.isk-product-card, .product-tile")))

            script_js = """
            let items = document.querySelectorAll('div.isk-product-card, .product-tile');
            return Array.from(items).map(item => ({
                sku_id: item.querySelector('a.isk-product-card__title, .product-name, h3')?.innerText.trim() || "Sin nombre",
                precio_raw: item.querySelector('.isk-product-card__price, .price-value')?.getAttribute('data-min-price') || "0.0",
                marca: item.querySelector('.brand-name, .isk-product-card__brand')?.innerText.trim() || "S/M",
                formato_raw: item.querySelector('.isk-product-card__pum, .product-format')?.innerText.trim() || "",
                rating: item.querySelector('.isk-reviews, [data-rating]')?.getAttribute('data-rating') || "0",
                opiniones: item.querySelector('.isk-product-card__reviews-total')?.innerText.replace(/[()]/g, "").trim() || "0"
            }));
            """
            items = driver.execute_script(script_js)

            for item in items:
                datos_tienda.append({
                    "sku_id": item['sku_id'],
                    "marca": item['marca'],
                    "precio_raw": item['precio_raw'],
                    "formato_raw": item['formato_raw'] if item['formato_raw'] else item['sku_id'],
                    "rating": item['rating'],
                    "opiniones": item['opiniones'],
                    "tienda": "Kiwoko",
                    "fecha_captura": time.strftime("%Y-%m-%d %H:%M:%S")
                })
        except Exception as e:
            print(f"⚠️ Error Kiwoko P{p}: {e}")
            continue
            
    return datos_tienda