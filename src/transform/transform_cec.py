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
    agregar_fecha_carga,
    seleccionar_cols_h_mspas,
)


# =============================================================
# IDs fijos para Enfermedades Crónicas
# =============================================================
ID_DMA_CEC = 2  # Modalidad: No aplica
ID_DSS_CEC = 2  # Dosis: No aplica
ID_ISP_CEC = 2  # Instrumento: No aplica

# Mapeo de nombre de DataFrame → id_fd
MAPA_ID_FD = {
    "y12":  3,
    "y13":  4,
    "y14":  5,
    "y15":  6,
    "y16":  7,
    "y17":  8,
    "y18":  9,
    "y19": 10,
    "y20": 11,
    "y21": 12,
    "y22": 13,
    "y23": 14,
    "y24": 15,
}

# Mapa canónico de columnas — basado en repr() exactos de los DataFrames
# Casos especiales:
#   y13 y y24 → columnas con saltos de línea (\n)
#   y13       → tiene 'Cantidad ' (con espacio) además de 'Casos' — se elimina
#   y19       → CIE viene como 'CIE 10' en vez de 'CIE-10'
#   y20       → grupo etario viene como 'GrupoEtario' sin espacio
MAPA_CANONICO = {
    "Año":              "anio",
    "Año \n":           "anio",
    "Departamento":     "departamento",
    "Departamento \n":  "departamento",
    "Municipio":        "municipio",
    "Municipio\n":      "municipio",
    "CIE-10":           "cie10",
    "CIE-10\n":         "cie10",
    "CIE 10":           "cie10",
    "Diagnóstico":      "diagnostico",
    "Diagnóstico\n":    "diagnostico",
    "Grupo Etario":     "grupo_etario",
    "GrupoEtario":      "grupo_etario",
    "Sexo":             "sexo",
    "Casos":            "cantidad",
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
# Consolidación de DataFrames CEC
# =============================================================

def consolidar_cec(dfs_cec: dict) -> pd.DataFrame:
    """
    Consolida los 13 DataFrames de Enfermedades Crónicas en uno solo.
    Maneja los casos especiales de columnas con variantes por año.

    Parámetros:
        dfs_cec: dict con keys 'df_url_cec_y12' ... 'df_url_cec_y24'

    Retorna:
        DataFrame consolidado con columnas canónicas
    """
    dfs_normalizados = []

    for nombre, df in dfs_cec.items():
        df_n = df.copy()

        # y13 tiene 'Cantidad ' (con espacio) además de 'Casos'
        # Se elimina antes del rename para evitar conflicto de columnas duplicadas
        if "Cantidad " in df_n.columns:
            df_n = df_n.drop(columns=["Cantidad "])
            print(f"  ℹ️  {nombre}: 'Cantidad ' eliminada — se usa 'Casos' como cantidad")

        # Renombrar con el mapa exacto
        df_n = df_n.rename(columns=MAPA_CANONICO)

        # Agregar columnas faltantes como None
        for col in COLS_CANONICAS:
            if col not in df_n.columns:
                df_n[col] = None

        # Asignar id_fd
        df_n["id_fd"] = MAPA_ID_FD.get(nombre, None)

        print(f"✅ {nombre}: id_fd={MAPA_ID_FD.get(nombre)}, filas={len(df_n):,}")

        # Solo columnas canónicas en orden fijo
        df_n = df_n[COLS_CANONICAS]
        dfs_normalizados.append(df_n)

    df_consolidado = pd.concat(dfs_normalizados, ignore_index=True)
    print(f"\n══ CEC consolidado: {len(df_consolidado):,} registros ══")
    return df_consolidado


# =============================================================
# Transformación Enfermedades Crónicas
# =============================================================

def transformar_cec(dfs_cec: dict, cat_ubicacion: pd.DataFrame,
                    cat_cie: pd.DataFrame, cat_ge: pd.DataFrame) -> pd.DataFrame:
    """
    Transforma los 13 datasets de Enfermedades Crónicas (2012-2024)
    y retorna un DataFrame listo para consolidar en h_mspas.

    Parámetros:
        dfs_cec       : dict con keys 'df_url_cec_y12' ... 'df_url_cec_y24'
        cat_ubicacion : catálogo de ubicación geográfica
        cat_cie       : catálogo CIE
        cat_ge        : catálogo de grupo etario

    Retorna:
        DataFrame con columnas de h_mspas
    """
    d_fecha    = crear_d_fecha()
    mapeo_sexo = crear_mapeo_sexo()

    # 1. Consolidar los 13 DataFrames en uno
    df = consolidar_cec(dfs_cec)

    # 2. Dimensión FECHA
    # Nota: después del consolidado la columna se llama 'anio' (minúsculas)
    df = asignar_id_fecha(df, col_anio="anio", d_fecha=d_fecha)

    # 3. Dimensión UBICACION GEOGRAFICA
    df = asignar_id_ubicacion(
        df,
        col_depto="departamento",
        col_muni="municipio",
        cat_ubicacion=cat_ubicacion
    )

    # 4. Dimensión CIE (por código — CEC sí tiene CIE variable)
    df = asignar_id_cie(df, col_cie="cie10", cat_cie=cat_cie)

    # 5. Dimensión SEXO BIOLOGICO
    df = asignar_id_sexo(df, col_sexo="sexo", mapeo_sexo=mapeo_sexo)

    # 6. Dimensión GRUPO ETARIO
    # Limpieza adicional de espacios antes del merge (requerida en CEC)
    df["grupo_etario"] = df["grupo_etario"].astype(str).str.strip()
    df = asignar_id_grupo_etario(df, col_ge="grupo_etario", cat_ge=cat_ge)

    # 7. Dimensiones fijas
    df = asignar_id_modalidad_fijo(df, id_dma=ID_DMA_CEC)
    df = asignar_id_dosis_fijo(df, id_dss=ID_DSS_CEC)
    df = asignar_id_instrumento_fijo(df, id_isp=ID_ISP_CEC)

    # 8. Fecha de carga
    df = agregar_fecha_carga(df)

    # 9. Seleccionar columnas finales
    df = seleccionar_cols_h_mspas(df)

    print(f"\n══ CEC TOTAL: {len(df):,} registros ══")
    return df