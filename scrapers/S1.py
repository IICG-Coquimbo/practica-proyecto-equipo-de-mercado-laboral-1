import time

def scraper_tiendanimal(driver, By, paginas=1):
    datos_tienda = []
    base_url = "https://www.tiendanimal.es/perros/dietas-veterinarias/"
    
    for p in range(1, paginas + 1):
        url = f"{base_url}?page={p}" if p > 1 else base_url
        driver.get(url)
        time.sleep(4) 

        script_js = """
        let cards = document.querySelectorAll('.isk-product-card');

return Array.from(cards).map(p => {
    // 1. RESCATE DE IDENTIDAD (Basado en imagen_5.png)
    // Extraemos el JSON que tiene el nombre y el ID real para que no salga "Sin nombre"
    let rawData = p.getAttribute('data-product-card-data');
    let jsonData = rawData ? JSON.parse(rawData) : {};
    
    // Usamos el ID del JSON como SKU y el nombre del JSON para el formato
    let nombre_real = jsonData.name || "Sin nombre";
    let sku_real = jsonData.id || "Sin ID";
    let marca_real = jsonData.brand || p.querySelector('.isk-product-card__headline-brand')?.innerText.trim() || "S/M";

    // 2. TUS SELECTORES (Los que confirmaste que sí funcionan)
    let rating = p.querySelector('.isk-reviews, [data-rating]')?.getAttribute('data-rating') || "0";
    let opiniones = p.querySelector('.isk-product-card__reviews-total')?.innerText.replace(/[()]/g, "").trim() || "0";

    // 3. PRECIO Y FORMATO
    // Extraemos el precio del atributo para evitar el "0.0"
    let precio = p.querySelector('.isk-product-card__price')?.getAttribute('data-min-price') || "0.0";
    let opciones = p.querySelector('.isk-product-card__options')?.innerText.trim() || "";

    return {
        sku_id: sku_real,
        marca: marca_real,
        precio_raw: precio,
        formato_raw: nombre_real + " " + opciones,
        rating: rating,
        opiniones: opiniones,
        moneda: "EUR"
    };
});
        """
        
        items = driver.execute_script(script_js)
        for item in items:
            datos_tienda.append({**item, "tienda": "Tiendanimal", "fecha_captura": time.strftime("%Y-%m-%d %H:%M:%S")})
            
    return datos_tienda