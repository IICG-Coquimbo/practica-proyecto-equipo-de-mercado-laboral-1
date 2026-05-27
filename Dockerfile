FROM jupyter/pyspark-notebook:latest

USER root

# =========================================================
# 1. Herramientas del sistema + entorno gráfico
# =========================================================
RUN apt-get update && apt-get install -y \
    ca-certificates \
    openssl \
    curl \
    gnupg \
    wget \
    xvfb \
    fluxbox \
    x11vnc \
    supervisor \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# =========================================================
# 2. Instalar Google Chrome
# =========================================================
RUN curl -fsSL https://dl.google.com/linux/linux_signing_key.pub | gpg --dearmor -o /usr/share/keyrings/google-chrome.gpg \
    && echo "deb [arch=amd64 signed-by=/usr/share/keyrings/google-chrome.gpg] http://dl.google.com/linux/chrome/deb/ stable main" \
       > /etc/apt/sources.list.d/google-chrome.list \
    && apt-get update \
    && apt-get install -y google-chrome-stable \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# =========================================================
# 3. Librerías Python
# =========================================================
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

# =========================================================
# 4. Limpiar jars MongoDB viejos/conflictivos
# =========================================================
RUN rm -f /usr/local/spark/jars/*mongo* \
    && rm -f /usr/local/spark/jars/*bson* \
    && rm -f /usr/local/spark/jars/*mongodb*

# =========================================================
# 5. Conector MongoDB para Spark 3.5 / Scala 2.12
# =========================================================
RUN wget https://repo1.maven.org/maven2/org/mongodb/spark/mongo-spark-connector_2.12/10.3.0/mongo-spark-connector_2.12-10.3.0.jar \
        -P /usr/local/spark/jars/ \
    && wget https://repo1.maven.org/maven2/org/mongodb/bson/5.1.0/bson-5.1.0.jar \
        -P /usr/local/spark/jars/ \
    && wget https://repo1.maven.org/maven2/org/mongodb/mongodb-driver-core/5.1.0/mongodb-driver-core-5.1.0.jar \
        -P /usr/local/spark/jars/ \
    && wget https://repo1.maven.org/maven2/org/mongodb/mongodb-driver-sync/5.1.0/mongodb-driver-sync-5.1.0.jar \
        -P /usr/local/spark/jars/

# =========================================================
# 6. Verificación de jars instalados
# =========================================================
RUN ls -lh /usr/local/spark/jars | grep mongo || true

# =========================================================
# 7. Configuración VNC
# =========================================================
COPY start-vnc.sh /usr/local/bin/start-vnc.sh
COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf

# =========================================================
# 8. Permisos y corrección CRLF -> LF
# =========================================================
RUN sed -i 's/\r$//' /usr/local/bin/start-vnc.sh \
    && chmod +x /usr/local/bin/start-vnc.sh \
    && chown -R jovyan:users /home/jovyan/work

# =========================================================
# 9. Variables de entorno
# =========================================================
ENV DISPLAY=:99

# =========================================================
# 10. Usuario por defecto
# =========================================================
USER ${NB_UID}

# =========================================================
# 11. Inicio del contenedor
# =========================================================
CMD ["/usr/bin/supervisord", "-c", "/etc/supervisor/conf.d/supervisord.conf"]