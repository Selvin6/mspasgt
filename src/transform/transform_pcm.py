import pandas as pd
from datetime import datetime
from src.transform.map_ids import (
    crear_d_fecha,
    crear_mapeo_sexo,
    asignar_id_fecha,
    asignar_id_ubicacion,
    asignar_id_cie,
    asignar_id_sexo,
    asignar_id_grupo_etario,
    asignar_id_modalidad_fijo,
    asignar_id_dosis_fijo,
    asignar_id_instrumento_fijo,
    limpiar_grupo_etario,
    agregar_fecha_carga,
    seleccionar_cols_h_mspas,
)


# =============================================================
# IDs fijos para PCM
# =============================================================
ID_DMA_PCM = 2  # Modalidad: No aplica
ID_DSS_PCM = 2  # Dosis: No aplica
ID_ISP_PCM = 2  # Instrumento: No aplica

MAPA_ID_FD = {
    "y12": 30,
    "y13": 31,
    "y14": 32,
    "y15": 33,
    "y16": 34,
    "y17": 35,
    "y18": 36,
    "y19": 37,
    "y20": 38,
    "y21": 39,
    "y22": 40,
    "y23": 41,
    "y24": 42,
}

# Mapa canónico — casos especiales:
# y13, y14 → columnas con espacio al final ('Año ', 'Departamento ', etc.)
# y16      → ' Casos' con espacio al INICIO
# y13, y14 → 'Conteo' como medida
# y15      → 'Cantidad' como medida
MAPA_CANONICO = {
    "Año":            "anio",
    "Año ":           "anio",           # y13, y14
    "Departamento":   "departamento",
    "Departamento ":  "departamento",   # y13, y14
    "Municipio":      "municipio",
    "Municipio ":     "municipio",      # y13, y14
    "CIE-10":         "cie10",
    "CIE-10 ":        "cie10",          # y13, y14
    "Diagnóstico":    "diagnostico",
    "Diagnóstico ":   "diagnostico",    # y13, y14
    "Grupo Etario":   "grupo_etario",   # todos — consistente
    "Sexo":           "sexo",           # todos — consistente
    "Casos":          "cantidad",
    " Casos":         "cantidad",       # y16 — espacio al inicio
    "Conteo":         "cantidad",       # y13, y14
    "Cantidad":       "cantidad",       # y15
}

COLS_CANONICAS = [
    "anio",
    "departamento",
    "municipio",
    "cie10",
    "diagnostico",
    "grupo_etario",
    "sexo",
    "cantidad",
    "id_fd",
]


# =============================================================
# Consolidación de DataFrames PCM
# =============================================================

def consolidar_pcm(dfs_pcm: dict) -> pd.DataFrame:
    """
    Consolida los 13 DataFrames de 20 Primeras Causas de Morbilidad.

    Parámetros:
        dfs_pcm: dict con keys 'df_url_pcm_y12' ... 'df_url_pcm_y24'

    Retorna:
        DataFrame consolidado con columnas canónicas
    """
    dfs_normalizados = []

    for nombre, df in dfs_pcm.items():
        df_n = df.copy()

        # Renombrar con el mapa exacto
        df_n = df_n.rename(columns=MAPA_CANONICO)

        # Agregar columnas faltantes como None
        for col in COLS_CANONICAS:
            if col not in df_n.columns:
                df_n[col] = None
                print(f"  ℹ️  {nombre}: '{col}' no existe → se agrega como None")

        # Asignar id_fd
        df_n["id_fd"] = MAPA_ID_FD.get(nombre, None)

        print(f"✅ {nombre}: id_fd={MAPA_ID_FD.get(nombre)}, filas={len(df_n):,}")

        df_n = df_n[COLS_CANONICAS]
        dfs_normalizados.append(df_n)

    df_consolidado = pd.concat(dfs_normalizados, ignore_index=True)
    print(f"\n══ PCM consolidado: {len(df_consolidado):,} registros ══")
    return df_consolidado


# =============================================================
# Transformación PCM
# =============================================================

def transformar_pcm(dfs_pcm: dict, cat_ubicacion: pd.DataFrame,
                    cat_cie: pd.DataFrame, cat_ge: pd.DataFrame) -> pd.DataFrame:
    """
    Transforma los 13 datasets de 20 Primeras Causas de Morbilidad (2012-2024)
    y retorna un DataFrame listo para consolidar en h_mspas.

    Parámetros:
        dfs_pcm       : dict con las 13 fuentes PCM
        cat_ubicacion : catálogo de ubicación geográfica
        cat_cie       : catálogo CIE
        cat_ge        : catálogo de grupo etario

    Retorna:
        DataFrame con columnas de h_mspas
    """
    d_fecha    = crear_d_fecha()
    mapeo_sexo = crear_mapeo_sexo()

    # 1. Consolidar los 13 DataFrames
    df = consolidar_pcm(dfs_pcm)

    # 2. Dimensión FECHA
    df = asignar_id_fecha(df, col_anio="anio", d_fecha=d_fecha)

    # 3. Dimensión UBICACION GEOGRAFICA
    df = asignar_id_ubicacion(
        df,
        col_depto="departamento",
        col_muni="municipio",
        cat_ubicacion=cat_ubicacion
    )

    # 4. Dimensión CIE — por código desde catálogo
    df = asignar_id_cie(df, col_cie="cie10", cat_cie=cat_cie)

    # 5. Dimensión SEXO BIOLOGICO
    df = asignar_id_sexo(df, col_sexo="sexo", mapeo_sexo=mapeo_sexo)

    # 6. Dimensión GRUPO ETARIO
    df["grupo_etario"] = df["grupo_etario"].apply(limpiar_grupo_etario)
    cat_ge = cat_ge.copy()
    cat_ge["nombre_grupo_etario_fuente_origen"] = (
        cat_ge["nombre_grupo_etario_fuente_origen"].apply(limpiar_grupo_etario)
    )
    df = asignar_id_grupo_etario(df, col_ge="grupo_etario", cat_ge=cat_ge)

    # 7. Dimensiones fijas
    df = asignar_id_modalidad_fijo(df, id_dma=ID_DMA_PCM)
    df = asignar_id_dosis_fijo(df, id_dss=ID_DSS_PCM)
    df = asignar_id_instrumento_fijo(df, id_isp=ID_ISP_PCM)

    # 8. Fecha de carga
    df = agregar_fecha_carga(df)

    # 9. Seleccionar columnas finales
    df = seleccionar_cols_h_mspas(df)

    print(f"\n══ PCM TOTAL: {len(df):,} registros ══")
    return df