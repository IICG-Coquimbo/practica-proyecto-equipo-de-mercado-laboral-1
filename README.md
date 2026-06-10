# Proyecto Big Data 2026 — Mercado Laboral TI
**Grupo 4 | Universidad Católica del Norte | Ingeniería en Información y Control de Gestión**

Análisis del mercado laboral en Chile mediante scraping, procesamiento con PySpark y aprendizaje no supervisado sobre datos reales de ofertas de empleo.

---

## Integrantes y Propiedad de Módulo

| Integrante | Rama | Módulo |
|---|---|---|
| Benjamin Ramirez | `feature/benja-ramirez` | Gestión de Infraestructura Cloud (Atlas, .env, docker-compose) |
| Giannella Rieu | `feature/GIANNELLA-RIEU` | Ingeniería de Datos y Pipeline — Procesamiento |
| Diego Castillo | `feature/diegoCastillo` | Ingeniería de Datos y Pipeline — Infraestructura Contenedor B |
| Denis Báez | `feature/denis-baez` | Análisis Descriptivo — EDA Multivariado (`eda_parte_A.ipynb`) |
| Lizette San Martín | `feature/liz-sanmartin` | Análisis Descriptivo — EDA Hipótesis (`eda_parte_B.ipynb`) |
| Nicolás Jorgensen | `feature/jorgensen-nico` | Modelado No Supervisado — Clustering (`NoModelado.ipynb`) |
| Sofia Urquieta | `feature/SofiaUrquieta` | Documentación y Calidad (Informe PDF) |

---

## Estructura del Proyecto


*Se deberan agregar los archivos start-vnc y supervisor.conf*
```
proyecto-big-data-2026/
│
├── Dockerfile                        # Contenedor A — Jupyter + PySpark + Selenium + Chrome
├── docker-compose.yml                # Orquestación de servicios
├── start-vnc.sh                      # Script de inicio VNC (requerido por Dockerfile)
├── supervisord.conf                  # Configuración supervisor (requerido por Dockerfile)
├── .env                              # Variables de entorno (NO subir a Git)
├── .gitignore                        # Archivos excluidos de Git
├── main.ipynb                        # Punto de entrada: ejecuta todos los scrapers
├── run_pipeline.ipynb                # Pipeline ejecutable por etapas desde Jupyter
│
├── jars/                             # JARs MongoDB para Spark (descargados localmente)
│   ├── mongo-spark-connector_2.12-10.3.0.jar
│   ├── bson-4.11.1.jar
│   ├── mongodb-driver-core-4.11.1.jar
│   └── mongodb-driver-sync-4.11.1.jar
│
├── Scrapers/                         # Contenedor A — Scraping
│   ├── Scraper_Diego.py              # getonbrd.com
│   ├── Scraper_SofiaUrquieta.py      # firstjob.me
│   ├── scraper_benja.py              # chiletrabajos.cl
│   ├── scraper_giannella.py          # cl.jobrapido.com
│   ├── scraper_denis_baez.py         # trabajando.cl
│   ├── scraper_lizette.py            # trabajos.com
│   ├── scraper_nicolas.py            # computrabajo.cl
│   └── utils.py                      # Configuración compartida del driver Selenium
│
├── src/                              # Contenedor B — Procesamiento
│   ├── Dockerfile                    # Imagen liviana: PySpark + pymongo (sin Chrome)
│   ├── validar_atlas.ipynb           # Verifica conexión a MongoDB Atlas
│   └── processor/
│       ├── processor.ipynb           # Limpieza + feature engineering → processed_data
│       │                             # (lee/escribe con PyMongo, procesa con PySpark)
│       ├── outliers.ipynb            # Función corregir_outliers() (IQR sobre títulos)
│       └── verificar_separacion.ipynb # Valida separación raw_data / processed_data
│
├── notebooks/                        # Análisis
│   ├── eda_parte_A.ipynb             # EDA multivariado: modalidad, seniority, heatmap
│   ├── eda_parte_B.ipynb             # Hipótesis H3 y H4, validación pregunta de negocio
│   └── NoModelado.ipynb              # K-Means (codo k=2-10), DBSCAN, PCA — sklearn
│
└── outputs/                          # Gráficos generados automáticamente
    └── plot_*.png
```

---

## Requisitos Previos

- Docker Desktop instalado y corriendo
- Archivo `.env` en la raíz del proyecto (ver sección siguiente)

---

## Configuración del Entorno (.env)

Crea un archivo `.env` en la raíz con el siguiente contenido:

```env
MONGO_URI=mongodb+srv://USUARIO:PASSWORD@cluster.mongodb.net/?retryWrites=true&w=majority
DB_NAME=Proyecto_Bigdata
```

> **Importante:** nunca subas el `.env` a GitHub. Está incluido en `.gitignore`.

---

## Levantar el Entorno

```bash
docker-compose up
```

Accede a Jupyter Lab en: [http://localhost:8888](http://localhost:8888)
Token: `bigdata`

Puertos disponibles:
- `8888` — Jupyter Lab
- `6080` — VNC (visualización del scraping)
- `4040` — Spark UI
- `8081` — Mongo Express (visualizador de Atlas)
- `8082` — FileBrowser

---

## Ejecución del Pipeline

Abre `run_pipeline.ipynb` en Jupyter Lab y ejecuta las celdas según lo que necesites:

| Celda | Qué ejecuta | Requisito |
|---|---|---|
| **Utilidades** | Carga funciones compartidas | Ejecutar **siempre primero** |
| **Solo Scraping** | `main.ipynb` → inserta en `Registros_Scraping` | Ninguno |
| **Solo Limpieza** | `processor.ipynb` → limpia y guarda en `processed_data` | Scraping previo |
| **Solo Análisis** | EDA + Clustering | Limpieza previa |
| **Pipeline Completo** | Todo en orden | Ninguno |

> **Nota:** `processor.ipynb` usa PyMongo para leer y escribir en Atlas, y PySpark solo para el procesamiento intermedio. No requiere el conector Spark-MongoDB.

---

## Flujo de Datos

```
[Scrapers]                    [Contenedor A]
  Scraper_Diego.py
  Scraper_SofiaUrquieta.py
  scraper_benja.py       ──→  main.ipynb  ──→  MongoDB Atlas
  scraper_giannella.py                          Registros_Scraping
  scraper_denis_baez.py                         (raw_data)
  scraper_lizette.py
  scraper_nicolas.py
                                                      │
                                                      ▼
                              [Contenedor B]   src/processor/
                              processor.ipynb  ──→  MongoDB Atlas
                              - Limpieza             processed_data
                              - Outliers
                              - Feature engineering
                              (es_ti, es_remoto, nivel_seniority,
                               largo_descripcion, categoria_horario_modalidad)
                                                      │
                                                      ▼
                              [Análisis]       notebooks/
                              eda_parte_A.ipynb      → outputs/plot_*.png
                              eda_parte_B.ipynb      → outputs/plot_*.png
                              NoModelado.ipynb       → K-Means k=3, DBSCAN, PCA
                              (sklearn — sin conector Spark)
```

---

## Esquema de Datos

Todos los scrapers producen documentos con el siguiente esquema unificado:

| Campo | Tipo | Descripción |
|---|---|---|
| `titulo_cargo` | string | Nombre del cargo ofertado |
| `empresa` | string | Empresa que publica la oferta |
| `pais` | string | País de la oferta |
| `fecha_captura` | string | Fecha y hora de scraping (`YYYY-MM-DD HH:MM:SS`) |
| `descripcion` | string | Descripción del cargo |
| `modalidad` | string | `Presencial`, `Remoto` o `Híbrido` |
| `tipo_horario` | string | `Full time` o `Part time` |
| `fecha_publicacion` | string | Fecha de publicación de la oferta |
| `grupo` | string | Identificador del integrante que scrapeó |

Columnas derivadas generadas por `processor.ipynb`:

| Campo | Tipo | Descripción |
|---|---|---|
| `es_ti` | bool | Oferta pertenece al sector TI |
| `es_remoto` | bool | Modalidad remota o híbrida |
| `nivel_seniority` | string | `Junior`, `Semi-Senior`, `Senior`, `No especificado` |
| `largo_descripcion` | int | Número de caracteres de la descripción |
| `categoria_horario_modalidad` | string | Combinación modalidad × horario |

---

## Hallazgos del Análisis

**Hipótesis validadas en EDA:**

- **H1 — Confirmada:** El sector TI exhibe un 31.3% de vacantes remotas frente a un 4.9% en No-TI (+26.4 pp). La modalidad es el predictor más relevante (r=0.27 con `es_ti`).
- **H2 — Confirmada:** El nivel Senior concentra el 85.7% de las ofertas TI vs 77.3% en No-TI (+8.4 pp). El mercado TI prioriza perfiles con experiencia comprobada.
- **H3 — No Confirmada:** La mediana del largo de descripción en TI fue 112 caracteres vs 130 en No-TI. El resultado se atribuye a un sesgo en la extracción: varios scrapers no capturaron descripciones completas.
- **H4 — Parcialmente Confirmada:** Full-time domina en ambos grupos (92.3% TI vs 87.4% No-TI), pero TI concentra mayor proporción de Freelance como modalidad secundaria.

**Segmentación K-Means (k=3):**

- **Clúster 0 — Empleos No-TI Presenciales:** mayoría del dataset, cargos de ventas, administración, logística y salud con modalidad presencial.
- **Clúster 1 — Empleos TI con Alta Demanda:** sector tecnológico con mayor especificidad técnica en descripciones y alta proporción de trabajo remoto e híbrido.
- **Clúster 2 — Empleos Remotos No-TI:** minoría con modalidad remota/híbrida fuera del sector TI (ejecutivos comerciales, atención al cliente online).

---

## Variable Dependiente Y — Hito 3

**Variable Y:** `es_ti` (booleano)

Toma valor `1` si la vacante pertenece al ecosistema TI y `0` en caso contrario. Construida mediante minería de texto y expresiones regulares sobre el título del cargo.

- **Distribución:** 5.2% clase positiva (195 registros TI) vs 94.8% clase negativa (3.582 No-TI)
- **Señal estadística:** brechas conductuales confirmadas por EDA (modalidad r=0.27, seniority +8.4 pp)
- **Tratamiento de desbalance:** se aplicarán técnicas SMOTE o class_weight en Hito 3
- **Algoritmos propuestos:** Regresión Logística y Random Forest (clasificación binaria)

---

## Verificación de Datos en Atlas

```javascript
// Contar documentos en raw_data
db.Registros_Scraping.countDocuments()

// Contar documentos en processed_data
db.processed_data.countDocuments()

// Contar por integrante
db.Registros_Scraping.aggregate([
  { $group: { _id: "$grupo", total: { $sum: 1 } } },
  { $sort: { total: -1 } }
])
```

---

## Notas Técnicas

**Conector Spark-MongoDB:** Los JARs están disponibles en la carpeta `jars/` del proyecto, mapeada como `/home/jovyan/work/jars/` dentro del contenedor. `processor.ipynb` usa PyMongo para leer y escribir en Atlas para evitar dependencias del conector en tiempo de ejecución.

**Reconstruir el contenedor:**
```bash
docker-compose down
docker-compose up --build
```
Requiere que `start-vnc.sh` y `supervisord.conf` estén en la raíz del proyecto.

---

## Seguridad

- Las credenciales de Atlas se gestionan exclusivamente via `.env`
- El cluster tiene IP Whitelisting configurado (`0.0.0.0/0`)
- El `.env` está en `.gitignore` y nunca debe commitearse
