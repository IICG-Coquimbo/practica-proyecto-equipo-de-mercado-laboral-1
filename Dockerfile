FROM jupyter/pyspark-notebook:latest

USER root

# 1. Herramientas de Red, SSL y Entorno Grafico (Xvfb para el scraper)
RUN apt-get update && apt-get install -y \
    ca-certificates \
    openssl \
    curl \
    gnupg \
    xvfb \
    fluxbox \
    x11vnc \
    supervisor \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# 2. Instalamos Google Chrome (compatible con webdriver-manager automatico)
RUN curl -fsSL https://dl.google.com/linux/linux_signing_key.pub | gpg --dearmor -o /usr/share/keyrings/google-chrome.gpg \
    && echo "deb [arch=amd64 signed-by=/usr/share/keyrings/google-chrome.gpg] http://dl.google.com/linux/chrome/deb/ stable main" \
       > /etc/apt/sources.list.d/google-chrome.list \
    && apt-get update && apt-get install -y google-chrome-stable \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# 3. Librerias de Python para todo el curso (Scraping estatico + dinamico + Atlas + Spark)
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir \
        "pymongo[srv]" \
        dnspython \
        certifi \
        selenium \
        webdriver-manager \
        pandas \
        requests \
        beautifulsoup4 \
        lxml

# 4. Conectores Spark-MongoDB
RUN wget https://repo1.maven.org/maven2/org/mongodb/spark/mongo-spark-connector_2.12/10.3.0/mongo-spark-connector_2.12-10.3.0.jar \
        -P /usr/local/spark/jars/ \
    && wget https://repo1.maven.org/maven2/org/mongodb/mongodb-driver-sync/4.11.1/mongodb-driver-sync-4.11.1.jar \
        -P /usr/local/spark/jars/

# 5. Configuracion de visualizacion (VNC para ver el navegador del scraping dinamico)
COPY start-vnc.sh /usr/local/bin/start-vnc.sh
COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf

# 6. Permisos y correccion de formato Windows->Linux (CRLF a LF)
RUN sed -i 's/\r$//' /usr/local/bin/start-vnc.sh \
    && chmod +x /usr/local/bin/start-vnc.sh \
    && chown -R jovyan:users /home/jovyan/work

ENV DISPLAY=:99

# Supervisor lanza Jupyter y el Entorno Grafico al mismo tiempo
CMD ["/usr/bin/supervisord", "-c", "/etc/supervisor/conf.d/supervisord.conf"]
