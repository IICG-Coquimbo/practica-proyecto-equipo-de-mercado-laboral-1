# Imagen base con Jupyter + PySpark
FROM jupyter/pyspark-notebook:latest

USER root

# Instala entorno visual, supervisor y Chrome
RUN apt-get update && apt-get install -y \
    wget \
    curl \
    gnupg \
    ca-certificates \
    openssl \
    xvfb \
    fluxbox \
    x11vnc \
    supervisor \
    python3-websockify \
    novnc \
    libnss3 \
    libgbm1 \
    libasound2 \
    sed \
    && mkdir -p /etc/apt/keyrings \
    && wget -qO- https://dl.google.com/linux/linux_signing_key.pub | gpg --dearmor -o /etc/apt/keyrings/google-chrome.gpg \
    && echo "deb [arch=amd64 signed-by=/etc/apt/keyrings/google-chrome.gpg] http://dl.google.com/linux/chrome/deb/ stable main" > /etc/apt/sources.list.d/google-chrome.list \
    && apt-get update \
    && apt-get install -y google-chrome-stable \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*


# 2. Instalamos Google Chrome (compatible con webdriver-manager automatico)
RUN curl -fsSL https://dl.google.com/linux/linux_signing_key.pub | gpg --dearmor -o /usr/share/keyrings/google-chrome.gpg \
    && echo "deb [arch=amd64 signed-by=/usr/share/keyrings/google-chrome.gpg] http://dl.google.com/linux/chrome/deb/ stable main" \
       > /etc/apt/sources.list.d/google-chrome.list \
    && apt-get update && apt-get install -y google-chrome-stable \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# 3. Librer�as de Python para todo el curso (Scraping + Atlas + Spark)
RUN pip install --no-cache-dir --upgrade pip && \
    #pip install --no-cache-dir "pymongo[srv]" dnspython certifi selenium webdriver-manager pandas
    pip install --no-cache-dir "pymongo[srv]" dnspython selenium webdriver-manager pandas certifi

RUN pip install --no-cache-dir streamlit seaborn openpyxl
        
# 4. Conectores Spark-MongoDB
RUN wget https://repo1.maven.org/maven2/org/mongodb/spark/mongo-spark-connector_2.12/10.4.0/mongo-spark-connector_2.12-10.4.0.jar \
        -P /usr/local/spark/jars/ \
    && wget https://repo1.maven.org/maven2/org/mongodb/mongodb-driver-sync/4.11.1/mongodb-driver-sync-4.11.1.jar \
        -P /usr/local/spark/jars/ \
    && wget https://repo1.maven.org/maven2/org/mongodb/mongodb-driver-core/4.11.1/mongodb-driver-core-4.11.1.jar \
        -P /usr/local/spark/jars/ \
    && wget https://repo1.maven.org/maven2/org/mongodb/bson/4.11.1/bson-4.11.1.jar \
        -P /usr/local/spark/jars/

# Variables del entorno gráfico
ENV DISPLAY=:99
ENV SCREEN_WIDTH=1368
ENV SCREEN_HEIGHT=768
ENV SCREEN_DEPTH=24

# Copia archivos de inicio
COPY start-vnc.sh /usr/local/bin/start-vnc.sh
COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf

# Convierte saltos de línea Windows a Linux y da permisos
RUN sed -i 's/\r$//' /usr/local/bin/start-vnc.sh && chmod +x /usr/local/bin/start-vnc.sh

# Puertos del contenedor
EXPOSE 8888 5900 6080 4040

# Inicia supervisord
# Iniciamos como root para evitar el error de setuid de la sesión anterior
CMD ["/usr/bin/supervisord", "-c", "/etc/supervisor/conf.d/supervisord.conf"]
