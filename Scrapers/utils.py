"""
Scrapers/utils.py
Utilidades compartidas para todos los scrapers del proyecto.
"""

import os
import glob
import shutil
import subprocess
import urllib.request
import zipfile

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service


def _obtener_chromedriver_path():
    """
    Obtiene la ruta al chromedriver sin depender de googlechromelabs.github.io:
    1. Cache local (~/.chromedriver/)  — sin red
    2. Cache de webdriver_manager (~/.wdm/)  — sin red
    3. Descarga directa desde storage.googleapis.com  — distinto a GitHub
    """

    # ── 1. Cache propio del proyecto ────────────────────────────
    result = subprocess.run(
        ["google-chrome", "--version"], capture_output=True, text=True
    )
    chrome_version = result.stdout.strip().split()[-1]

    driver_dir  = os.path.expanduser(f"~/.chromedriver/{chrome_version}")
    driver_path = os.path.join(driver_dir, "chromedriver")

    if os.path.isfile(driver_path) and os.access(driver_path, os.X_OK):
        return driver_path

    # ── 2. Cache de webdriver_manager (~/.wdm/) ─────────────────
    wdm_patterns = [
        os.path.expanduser("~/.wdm/drivers/chromedriver/*/*/chromedriver-linux64/chromedriver"),
        os.path.expanduser("~/.wdm/drivers/chromedriver/*/chromedriver"),
        os.path.expanduser("~/.wdm/drivers/chromedriver/*/*/chromedriver"),
    ]
    candidatos = []
    for pattern in wdm_patterns:
        candidatos.extend(glob.glob(pattern))
    for path in sorted(candidatos, reverse=True):
        if os.path.isfile(path) and os.access(path, os.X_OK) and os.path.getsize(path) > 5_000_000:
            return path

    # ── 3. Descargar desde storage.googleapis.com ───────────────
    os.makedirs(driver_dir, exist_ok=True)
    url      = (
        f"https://storage.googleapis.com/chrome-for-testing-public"
        f"/{chrome_version}/linux64/chromedriver-linux64.zip"
    )
    zip_path = os.path.join(driver_dir, "chromedriver-linux64.zip")

    print(f"Descargando chromedriver {chrome_version} desde storage.googleapis.com...")
    urllib.request.urlretrieve(url, zip_path)

    with zipfile.ZipFile(zip_path, "r") as z:
        z.extractall(driver_dir)

    extracted = os.path.join(driver_dir, "chromedriver-linux64", "chromedriver")
    if os.path.isfile(extracted):
        shutil.move(extracted, driver_path)

    os.chmod(driver_path, 0o755)
    os.remove(zip_path)
    print(f"chromedriver listo: {driver_path}")
    return driver_path


def obtener_driver(headless=True, deshabilitar_imagenes=True):
    """
    Crea y retorna un WebDriver de Chrome listo para usar.
    Todos los scrapers del proyecto deben llamar esta función.

    Parámetros:
        headless (bool): True para modo sin ventana (recomendado en Docker).
        deshabilitar_imagenes (bool): True para mayor velocidad.
    """
    os.system("pkill -9 chrome")
    os.system("pkill -9 chromedriver")
    os.environ["DISPLAY"] = ":99"

    options = Options()
    options.binary_location = "/usr/bin/google-chrome"
    if headless:
        options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")
    options.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
    )
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)
    options.add_argument("--disable-blink-features=AutomationControlled")

    if deshabilitar_imagenes:
        options.add_experimental_option(
            "prefs", {"profile.managed_default_content_settings.images": 2}
        )

    driver_path = _obtener_chromedriver_path()
    driver = webdriver.Chrome(service=Service(driver_path), options=options)
    driver.execute_script(
        "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
    )
    return driver
