import pandas as pd
import requests
from io import StringIO
from src.config.settings import (
    URLS_CD, URLS_CEC, URLS_ETPV,
    URLS_MGM, URLS_MIE, URLS_PCM,
    URLS_PCP, URLS_SNM
)
import warnings
warnings.filterwarnings("ignore", message="Unverified HTTPS request")



def descargar_csv(url: str, sep: str = ";") -> pd.DataFrame:
    """Descarga un CSV desde una URL y retorna un DataFrame."""
    respuesta = requests.get(url, timeout=60, verify=False)
    respuesta.raise_for_status()
    respuesta.encoding = "utf-8-sig"
    return pd.read_csv(
        StringIO(respuesta.text),
        sep=sep,
        on_bad_lines="skip",
        engine="python"
    )


# =============================================================
# 1. Desnutrición
# =============================================================
def extraer_cd() -> dict:
    """Extrae datasets de categoría desnutrición."""
    return {
        "mda": descargar_csv(URLS_CD["mda"]),
        "mrd": descargar_csv(URLS_CD["mrd"]),
    }


# =============================================================
# 2. Enfermedades crónicas
# =============================================================
def extraer_cec() -> dict:
    """Extrae datasets de enfermedades crónicas — un dict por año."""
    return {
        f"y{str(anio)[2:]}": descargar_csv(url)
        for anio, url in URLS_CEC.items()
    }


# =============================================================
# 3. Enfermedades transmitidas por vectores
# =============================================================
def extraer_etpv() -> dict:
    """Extrae datasets de enfermedades transmitidas por vectores."""
    return {
        enfermedad: descargar_csv(url)
        for enfermedad, url in URLS_ETPV.items()
    }


# =============================================================
# 4. Morbilidad Grupo Materno Infantil
# =============================================================
def extraer_mgm() -> dict:
    """Extrae datasets de morbilidad grupo materno infantil."""
    return {
        grupo: descargar_csv(url)
        for grupo, url in URLS_MGM.items()
    }


# =============================================================
# 5. Morbilidad IRAS y ETAS
# =============================================================
def extraer_mie() -> dict:
    """Extrae datasets de morbilidad IRAS y ETAS."""
    return {
        tipo: descargar_csv(url)
        for tipo, url in URLS_MIE.items()
    }


# =============================================================
# 6. 20 primeras causas de morbilidad
# =============================================================
def extraer_pcm() -> dict:
    """Extrae datasets de 20 primeras causas de morbilidad — un dict por año."""
    return {
        f"y{str(anio)[2:]}": descargar_csv(url)
        for anio, url in URLS_PCM.items()
    }


# =============================================================
# 7. Producción de consultas y pacientes nuevos
# =============================================================
def extraer_pcp() -> pd.DataFrame:
    """Extrae dataset de producción de consultas y pacientes nuevos."""
    return descargar_csv(URLS_PCP["consultas"])


# =============================================================
# 8. Suplementación niños menores 5 años
# =============================================================
def extraer_snm() -> pd.DataFrame:
    """Extrae dataset de suplementación en niños menores de 5 años."""
    return descargar_csv(URLS_SNM["suplementacion"])


# =============================================================
# Extracción completa
# =============================================================
def extraer_todo() -> dict:
    """Ejecuta la extracción de todas las fuentes y retorna un diccionario."""
    print("Extrayendo desnutrición...")
    cd = extraer_cd()

    print("Extrayendo enfermedades crónicas...")
    cec = extraer_cec()

    print("Extrayendo enfermedades transmitidas por vectores...")
    etpv = extraer_etpv()

    print("Extrayendo morbilidad grupo materno infantil...")
    mgm = extraer_mgm()

    print("Extrayendo morbilidad IRAS y ETAS...")
    mie = extraer_mie()

    print("Extrayendo 20 primeras causas de morbilidad...")
    pcm = extraer_pcm()

    print("Extrayendo producción de consultas y pacientes nuevos...")
    pcp = extraer_pcp()

    print("Extrayendo suplementación niños menores 5 años...")
    snm = extraer_snm()

    print("Extracción completa.")

    return {
        "cd":   cd,
        "cec":  cec,
        "etpv": etpv,
        "mgm":  mgm,
        "mie":  mie,
        "pcm":  pcm,
        "pcp":  pcp,
        "snm":  snm,
    }