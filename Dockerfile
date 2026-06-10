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

#Instalamos streamlit
RUN pip install --no-cache-dir streamlit seaborn openpyxl

# 4. Conectores Spark-MongoDB (conector + todas las dependencias transitivas del driver)
#    - mongo-spark-connector : punto de entrada para Spark
#    - bson                  : contiene org.bson.BsonValue (ClassNotFoundException si falta)
#    - mongodb-driver-core   : clases base del driver (falla sin este)
#    - mongodb-driver-sync   : API sincronica que usa el conector
RUN wget https://repo1.maven.org/maven2/org/mongodb/spark/mongo-spark-connector_2.12/10.3.0/mongo-spark-connector_2.12-10.3.0.jar \
        -P /usr/local/spark/jars/ \
    && wget https://repo1.maven.org/maven2/org/mongodb/bson/4.11.1/bson-4.11.1.jar \
        -P /usr/local/spark/jars/ \
    && wget https://repo1.maven.org/maven2/org/mongodb/mongodb-driver-core/4.11.1/mongodb-driver-core-4.11.1.jar \
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
