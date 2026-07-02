import pandas as pd
import unicodedata
import re
import os
from datetime import datetime
from src.config.settings import CATALOGOS_DIR


# =============================================================
# Carga de catálogos
# =============================================================

def cargar_catalogo_cie() -> pd.DataFrame:
    return pd.read_csv(os.path.join(CATALOGOS_DIR, "codigos_para_dimension_cie.csv"), sep=",")


def cargar_catalogo_ubicacion() -> pd.DataFrame:
    return pd.read_csv(os.path.join(CATALOGOS_DIR, "codigos_para_dimension_ubicacion_geo.csv"), sep=",")


def cargar_catalogo_grupo_etario() -> pd.DataFrame:
    return pd.read_csv(
        os.path.join(CATALOGOS_DIR, "d_grupo_etario_id_para_asignar.csv"),
        sep=",", keep_default_na=False
    )


def cargar_catalogo_dosis() -> pd.DataFrame:
    return pd.read_csv(
        os.path.join(CATALOGOS_DIR, "d_dosis_asignar.csv"),
        sep=",", keep_default_na=False
    )


def cargar_catalogo_instrumento() -> pd.DataFrame:
    return pd.read_csv(
        os.path.join(CATALOGOS_DIR, "d_instrumento_suplementacion_asignar.csv"),
        sep=",", keep_default_na=False
    )


def cargar_catalogo_modalidad() -> pd.DataFrame:
    return pd.read_csv(
        os.path.join(CATALOGOS_DIR, "d_modalidad_atencion_asignar.csv"),
        sep=",", keep_default_na=False
    )


def cargar_catalogo_fuente() -> pd.DataFrame:
    return pd.read_csv(os.path.join(CATALOGOS_DIR, "d_fuente_datos_para_asignar.csv"), sep=",")


# =============================================================
# Dimensión FECHA (grano anual)
# =============================================================

def crear_d_fecha(anio_inicio: int = 2012, anio_fin: int = 2030) -> pd.DataFrame:
    """
    Genera d_fecha con grano anual.
    id_df = YYYYMMDD como entero (31 dic de cada año = fecha de cierre del período).
    """
    meses_es = {
        1: "Enero", 2: "Febrero", 3: "Marzo", 4: "Abril",
        5: "Mayo", 6: "Junio", 7: "Julio", 8: "Agosto",
        9: "Septiembre", 10: "Octubre", 11: "Noviembre", 12: "Diciembre"
    }
    dias_es = {
        1: "Lunes", 2: "Martes", 3: "Miércoles", 4: "Jueves",
        5: "Viernes", 6: "Sábado", 7: "Domingo"
    }
    registros = []
    for anio in range(anio_inicio, anio_fin + 1):
        fecha = pd.Timestamp(f"{anio}-12-31")
        registros.append({
            "id_df":                  int(fecha.strftime("%Y%m%d")),
            "fecha":                  fecha,
            "anio":                   anio,
            "mes":                    fecha.month,
            "nombre_mes":             meses_es[fecha.month],
            "trimestre":              fecha.quarter,
            "nombre_trimestre":       f"Q{fecha.quarter}",
            "semestre":               2,
            "dia":                    fecha.day,
            "dias_semana":            fecha.dayofweek + 1,
            "nombre_dia_semana":      dias_es[fecha.dayofweek + 1],
            "semana_anio":            fecha.isocalendar()[1],
            "es_fin_semana":          fecha.dayofweek >= 5,
            "periodo_anio_mes":       int(fecha.strftime("%Y%m")),
            "periodo_anio_trimestre": f"{anio}Q{fecha.quarter}",
            "estado":                 "activo",
        })
    return pd.DataFrame(registros)


# =============================================================
# Dimensión SEXO BIOLÓGICO
# =============================================================

NORMALIZACION_SEXO = {
    "F":         ("Femenino",  4),
    "Femenino":  ("Femenino",  4),
    "FEMENINO":  ("Femenino",  4),
    "M":         ("Masculino", 3),
    "Masculino": ("Masculino", 3),
    "MASCULINO": ("Masculino", 3),
}


def crear_mapeo_sexo(valores_unicos: list = None) -> pd.DataFrame:
    """
    Crea tabla de mapeo de sexo biológico.
    Si se pasan valores_unicos, solo mapea los valores encontrados en los datos.
    """
    if valores_unicos is None:
        valores_unicos = list(NORMALIZACION_SEXO.keys())

    registros = []
    for valor in valores_unicos:
        canon, id_dsb = NORMALIZACION_SEXO.get(valor, (None, None))
        registros.append({
            "id_sexo_biologico_fuente_origen": valor,
            "sexo_canonico":                   canon,
            "id_dsb":                          id_dsb,
        })

    df = pd.DataFrame(registros)
    sin_mapeo = df[df["id_dsb"].isna()]
    if not sin_mapeo.empty:
        print(f"⚠️ Valores sin mapear: {sin_mapeo['id_sexo_biologico_fuente_origen'].tolist()}")
    else:
        print("✓ Todos los valores de sexo mapeados correctamente")

    return df


# =============================================================
# Limpieza de grupo etario
# =============================================================

def limpiar_grupo_etario(texto) -> str:
    """Colapsa espacios múltiples y quita espacios al inicio/final."""
    if pd.isna(texto):
        return texto
    return re.sub(r"\s+", " ", str(texto).strip())


# =============================================================
# Asignación de IDs - Dimensión FECHA
# =============================================================

def asignar_id_fecha(df: pd.DataFrame, col_anio: str, d_fecha: pd.DataFrame) -> pd.DataFrame:
    """Asigna id_df desde dimensión fecha usando columna de año."""
    df = df.merge(
        d_fecha[["anio", "id_df"]],
        left_on=col_anio,
        right_on="anio",
        how="left"
    ).drop(columns=["anio"])
    return df


# =============================================================
# Asignación de IDs - Dimensión UBICACION GEOGRAFICA
# =============================================================

def asignar_id_ubicacion(df: pd.DataFrame, col_depto: str, col_muni: str, cat_ubicacion: pd.DataFrame) -> pd.DataFrame:
    """Asigna id_dug creando llave DEPARTAMENTO_MUNICIPIO."""
    df["llave_dug"] = (
        df[col_depto].astype(str).str.strip().str.upper()
        + "_" +
        df[col_muni].astype(str).str.strip().str.upper()
    )
    df = df.merge(
        cat_ubicacion[["id_combinado_origen_datos_dataframe", "id_dug"]],
        left_on="llave_dug",
        right_on="id_combinado_origen_datos_dataframe",
        how="left"
    ).drop(columns=["llave_dug", "id_combinado_origen_datos_dataframe"])
    return df


# =============================================================
# Asignación de IDs - Dimensión CIE
# =============================================================

def asignar_id_cie(df: pd.DataFrame, col_cie: str, cat_cie: pd.DataFrame) -> pd.DataFrame:
    """Asigna id_dcie desde catálogo CIE por código."""
    df = df.merge(
        cat_cie[["id_fuente_origen", "id_dcie"]],
        left_on=col_cie,
        right_on="id_fuente_origen",
        how="left"
    ).drop(columns=["id_fuente_origen"])
    return df


def asignar_id_cie_por_fd(df: pd.DataFrame, mapa_id_dcie: dict) -> pd.DataFrame:
    """
    Asigna id_dcie desde un diccionario {id_fd: id_dcie}.
    Usada cuando el CIE es fijo por fuente (ETPV, MIE).
    """
    df["id_dcie"] = df["id_fd"].map(mapa_id_dcie)
    return df


# =============================================================
# Asignación de IDs - Dimensión SEXO BIOLOGICO
# =============================================================

def asignar_id_sexo(df: pd.DataFrame, col_sexo: str, mapeo_sexo: pd.DataFrame) -> pd.DataFrame:
    """Asigna id_dsb desde mapeo de sexo biológico."""
    df = df.merge(
        mapeo_sexo[["id_sexo_biologico_fuente_origen", "id_dsb"]],
        left_on=col_sexo,
        right_on="id_sexo_biologico_fuente_origen",
        how="left"
    ).drop(columns=["id_sexo_biologico_fuente_origen"])
    return df


def asignar_id_sexo_fijo(df: pd.DataFrame, id_dsb: int, condicion=None) -> pd.DataFrame:
    """
    Asigna id_dsb fijo cuando la fuente no tiene columna de sexo
    o cuando hay valores nulos para un id_fd específico.
    condicion: expresión booleana sobre df (opcional)
    """
    if condicion is not None:
        df.loc[condicion & df["id_dsb"].isna(), "id_dsb"] = id_dsb
    else:
        df["id_dsb"] = id_dsb
    return df


# =============================================================
# Asignación de IDs - Dimensión GRUPO ETARIO
# =============================================================

def asignar_id_grupo_etario(df: pd.DataFrame, col_ge: str, cat_ge: pd.DataFrame) -> pd.DataFrame:
    """Asigna id_dge desde catálogo grupo etario."""
    df[col_ge] = df[col_ge].apply(limpiar_grupo_etario)
    cat_ge = cat_ge.copy()
    cat_ge["nombre_grupo_etario_fuente_origen"] = cat_ge["nombre_grupo_etario_fuente_origen"].apply(limpiar_grupo_etario)

    df = df.merge(
        cat_ge[["nombre_grupo_etario_fuente_origen", "id_dge"]],
        left_on=col_ge,
        right_on="nombre_grupo_etario_fuente_origen",
        how="left"
    ).drop(columns=["nombre_grupo_etario_fuente_origen"])
    return df


# =============================================================
# Asignación de IDs - Dimensión MODALIDAD ATENCION
# =============================================================

def asignar_id_modalidad(df: pd.DataFrame, col_modalidad: str, cat_modalidad: pd.DataFrame) -> pd.DataFrame:
    """Asigna id_dma desde catálogo modalidad de atención."""
    df = df.merge(
        cat_modalidad[["id_dma", "modalida_atencion"]],
        left_on=col_modalidad,
        right_on="modalida_atencion",
        how="left"
    ).drop(columns=["modalida_atencion"])
    return df


def asignar_id_modalidad_fijo(df: pd.DataFrame, id_dma: int) -> pd.DataFrame:
    """Asigna id_dma fijo cuando la fuente no tiene columna de modalidad."""
    df["id_dma"] = id_dma
    return df


# =============================================================
# Asignación de IDs - Dimensión DOSIS
# =============================================================

def asignar_id_dosis(df: pd.DataFrame, col_dosis: str, cat_dosis: pd.DataFrame) -> pd.DataFrame:
    """Asigna id_dss desde catálogo dosis."""
    df = df.merge(
        cat_dosis[["id_dss", "dosis"]],
        left_on=col_dosis,
        right_on="dosis",
        how="left"
    )
    return df


def asignar_id_dosis_fijo(df: pd.DataFrame, id_dss: int) -> pd.DataFrame:
    """Asigna id_dss fijo cuando la fuente no tiene columna de dosis."""
    df["id_dss"] = id_dss
    return df


# =============================================================
# Asignación de IDs - Dimensión INSTRUMENTO SUPLEMENTACION
# =============================================================

def asignar_id_instrumento(df: pd.DataFrame, col_instrumento: str, cat_instrumento: pd.DataFrame) -> pd.DataFrame:
    """Asigna id_isp desde catálogo instrumento suplementación."""
    df = df.merge(
        cat_instrumento[["id_isp", "instrumento_suplementacion"]],
        left_on=col_instrumento,
        right_on="instrumento_suplementacion",
        how="left"
    )
    return df


def asignar_id_instrumento_fijo(df: pd.DataFrame, id_isp: int) -> pd.DataFrame:
    """Asigna id_isp fijo cuando la fuente no tiene columna de instrumento."""
    df["id_isp"] = id_isp
    return df


# =============================================================
# Agregar fecha de carga
# =============================================================

def agregar_fecha_carga(df: pd.DataFrame) -> pd.DataFrame:
    """Agrega columna fecha_carga con fecha y hora actual."""
    df["fecha_carga"] = datetime.now()
    return df


# =============================================================
# Columnas finales de h_mspas
# =============================================================

COLS_H_MSPAS = [
    "id_df",
    "id_dug",
    "id_dcie",
    "id_dsb",
    "id_dge",
    "id_dma",
    "id_dss",
    "id_isp",
    "id_fd",
    "cantidad",
    "fecha_carga",
]


def seleccionar_cols_h_mspas(df: pd.DataFrame) -> pd.DataFrame:
    """Selecciona y ordena las columnas finales de h_mspas."""
    cols_disponibles = [c for c in COLS_H_MSPAS if c in df.columns]
    cols_faltantes = [c for c in COLS_H_MSPAS if c not in df.columns]
    if cols_faltantes:
        print(f"⚠️ Columnas faltantes en h_mspas: {cols_faltantes}")
    return df[cols_disponibles]