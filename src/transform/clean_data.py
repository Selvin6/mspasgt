import pandas as pd
import unicodedata
import re


# =============================================================
# Normalización de nombres de columnas
# =============================================================

def normalizar_columna(col) -> str:
    """
    Normaliza nombres de columnas para compararlas:
    - Convierte a minúsculas
    - Reemplaza guiones bajos por espacios
    - Quita espacios al inicio y final
    - Reduce espacios múltiples
    """
    return " ".join(
        str(col)
        .lower()
        .replace("_", " ")
        .strip()
        .split()
    )


def limpiar_col(col: str) -> str:
    """
    Quita espacios al inicio/final y colapsa espacios múltiples internos.
    Usada para limpiar nombres de columnas antes de renombrar.
    """
    col = col.strip()
    col = re.sub(r"\s+", " ", col)
    return col


def normalizar_nombre_columna(col) -> str:
    """
    Normalización completa de nombres de columna:
    - Quita tildes
    - Reemplaza caracteres especiales por guión bajo
    - Convierte a minúsculas
    - Quita guiones bajos al inicio/final
    Usada en datasets como SNM que tienen columnas con paréntesis.
    """
    col = str(col).strip().lower()
    col = "".join(
        c for c in unicodedata.normalize("NFKD", col)
        if not unicodedata.combining(c)
    )
    col = re.sub(r"[^a-z0-9]+", "_", col)
    col = col.strip("_")
    return col


def limpiar_columnas(df: pd.DataFrame) -> pd.DataFrame:
    """
    Estandariza los nombres de columnas:
    minúsculas, sin espacios ni caracteres especiales.
    """
    df.columns = (
        df.columns
        .str.strip()
        .str.lower()
        .str.replace(" ", "_")
        .str.replace("á", "a").str.replace("é", "e")
        .str.replace("í", "i").str.replace("ó", "o")
        .str.replace("ú", "u").str.replace("ñ", "n")
        .str.replace(r"[^a-z0-9_]", "", regex=True)
    )
    return df


# =============================================================
# Normalización de texto
# =============================================================

def normalizar_texto(texto) -> str:
    """
    Normaliza texto para comparar nombres de columnas:
    - Convierte a string
    - Quita saltos de línea
    - Quita espacios iniciales/finales
    - Estandariza espacios internos
    - Convierte a mayúsculas
    - Quita tildes
    """
    texto = str(texto)
    texto = texto.replace("\n", " ").replace("\r", " ")
    texto = texto.strip()
    texto = " ".join(texto.split())
    texto = texto.upper()
    texto = unicodedata.normalize("NFKD", texto)
    return "".join(c for c in texto if not unicodedata.combining(c))


def limpiar_texto(df: pd.DataFrame, columnas: list) -> pd.DataFrame:
    """Limpia columnas de texto: strip, uppercase y elimina dobles espacios."""
    for col in columnas:
        if col in df.columns:
            df[col] = (
                df[col]
                .astype(str)
                .str.strip()
                .str.upper()
                .str.replace(r"\s+", " ", regex=True)
            )
    return df


# =============================================================
# Búsqueda flexible de columnas
# =============================================================

def encontrar_columna(df: pd.DataFrame, posibles_nombres: list):
    """
    Busca una columna dentro del DataFrame según posibles nombres.
    La comparación tolera espacios, saltos de línea,
    mayúsculas/minúsculas y tildes.
    Retorna el nombre original de la columna o None si no la encuentra.
    """
    posibles_normalizados = [normalizar_texto(nombre) for nombre in posibles_nombres]
    for col in df.columns:
        if normalizar_texto(col) in posibles_normalizados:
            return col
    return None


VARIANTES_GRUPO_ETARIO = {
    "rango de edad",
    "rango_de_edad",
    "grupo etario",
    "grupo_etario",
    "grupoetario",
}


def detectar_col_grupo_etario(df: pd.DataFrame):
    """
    Detecta la columna de grupo etario sin importar
    mayúsculas, tildes ni separadores.
    Retorna el nombre original o None.
    """
    for c in df.columns:
        c_norm = (
            c.lower().strip()
            .replace("á", "a").replace("é", "e").replace("í", "i")
            .replace("ó", "o").replace("ú", "u").replace("ñ", "n")
            .replace(" ", "_")
        )
        if c_norm in VARIANTES_GRUPO_ETARIO:
            return c
    return None


# =============================================================
# Limpieza de valores
# =============================================================

def limpiar_valor_texto(serie: pd.Series) -> pd.Series:
    """
    Limpia una columna textual:
    - Convierte a string
    - Quita saltos de línea
    - Quita espacios
    - Reemplaza valores vacíos por pd.NA
    """
    VACIOS = {"", "nan", "NaN", "NAN", "None", "NONE", "null", "NULL"}
    serie_limpia = (
        serie
        .astype(str)
        .str.replace("\n", " ", regex=False)
        .str.replace("\r", " ", regex=False)
        .str.strip()
    )
    return serie_limpia.replace({v: pd.NA for v in VACIOS})


def limpiar_codigo_cie(serie: pd.Series) -> pd.Series:
    """
    Limpia código CIE:
    - Convierte a string
    - Quita espacios
    - Convierte a mayúsculas
    - Reemplaza vacíos por pd.NA
    """
    VACIOS = {"", "nan", "NaN", "NAN", "None", "NONE", "null", "NULL"}
    serie_limpia = serie.astype(str).str.strip().str.upper()
    return serie_limpia.replace({v: pd.NA for v in VACIOS})


def limpiar_medida_numerica(serie: pd.Series) -> pd.DataFrame:
    """
    Limpia y convierte la columna de medida (cantidad/Casos/Conteo).
    Retorna un DataFrame auxiliar con columnas de auditoría:
    - valor_medida_original
    - valor_medida_limpio
    - valor_medida
    - medida_vacia
    - medida_no_numerica
    - valor_medida_para_suma
    """
    VACIOS = {"", "nan", "NaN", "NAN", "None", "NONE", "null", "NULL"}
    resultado = pd.DataFrame()
    resultado["valor_medida_original"] = serie

    resultado["valor_medida_limpio"] = (
        serie
        .astype(str)
        .str.replace("\n", " ", regex=False)
        .str.replace("\r", " ", regex=False)
        .str.strip()
        .replace({v: pd.NA for v in VACIOS})
    )

    resultado["valor_medida"] = pd.to_numeric(
        resultado["valor_medida_limpio"], errors="coerce"
    )

    resultado["medida_vacia"] = resultado["valor_medida_limpio"].isna()

    resultado["medida_no_numerica"] = (
        resultado["valor_medida_limpio"].notna()
        & resultado["valor_medida"].isna()
    )

    resultado["valor_medida_para_suma"] = resultado["valor_medida"].fillna(0)

    return resultado


def eliminar_nulos(df: pd.DataFrame, columnas: list) -> pd.DataFrame:
    """Elimina filas donde las columnas clave sean nulas."""
    return df.dropna(subset=columnas).reset_index(drop=True)


def limpiar_cantidad(df: pd.DataFrame, col: str = "cantidad") -> pd.DataFrame:
    """Convierte la columna cantidad a entero, reemplazando nulos por 0."""
    if col in df.columns:
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0).astype(int)
    return df


def estandarizar_anio(df: pd.DataFrame, col: str = "ao") -> pd.DataFrame:
    """Convierte la columna año a entero."""
    if col in df.columns:
        df[col] = pd.to_numeric(df[col], errors="coerce").astype("Int64")
    return df