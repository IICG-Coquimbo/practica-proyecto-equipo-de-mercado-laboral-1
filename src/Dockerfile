FROM jupyter/pyspark-notebook:latest

USER root

# Dependencias para conexion a Atlas y procesamiento
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir \
        "pymongo[srv]" \
        dnspython \
        certifi \
        python-dotenv \
        pandas

# Conectores Spark-MongoDB
RUN wget https://repo1.maven.org/maven2/org/mongodb/spark/mongo-spark-connector_2.12/10.3.0/mongo-spark-connector_2.12-10.3.0.jar \
        -P /usr/local/spark/jars/ \
    && wget https://repo1.maven.org/maven2/org/mongodb/bson/4.11.1/bson-4.11.1.jar \
        -P /usr/local/spark/jars/ \
    && wget https://repo1.maven.org/maven2/org/mongodb/mongodb-driver-core/4.11.1/mongodb-driver-core-4.11.1.jar \
        -P /usr/local/spark/jars/ \
    && wget https://repo1.maven.org/maven2/org/mongodb/mongodb-driver-sync/4.11.1/mongodb-driver-sync-4.11.1.jar \
        -P /usr/local/spark/jars/

RUN chown -R jovyan:users /home/jovyan/work

USER jovyan

WORKDIR /home/jovyan/work
