import pandas as pd
from datetime import datetime
from src.transform.map_ids import (
    crear_d_fecha,
    crear_mapeo_sexo,
    asignar_id_fecha,
    asignar_id_ubicacion,
    asignar_id_cie_por_fd,
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
# IDs fijos para ETPV
# =============================================================
ID_DMA_ETPV = 2  # Modalidad: No aplica
ID_DSS_ETPV = 2  # Dosis: No aplica
ID_ISP_ETPV = 2  # Instrumento: No aplica

# CIE fijo por fuente — cada enfermedad tiene su propio CIE
MAPA_ID_DCIE = {
    16: 139,    # Chagas
    17: 2409,   # Chikungunya
    18: 79,     # Dengue grave
    19: 78,     # Dengue
    20: 14391,  # Malaria
    21: 2414,   # Zika
}

MAPA_ID_FD = {
    "df_url_etpv_y12_24_cg": 16,
    "df_url_etpv_y14_24_ck": 17,
    "df_url_etpv_y12_24_dg": 18,
    "df_url_etpv_y12_24_de": 19,
    "df_url_etpv_y12_24_ma": 20,
    "df_url_etpv_y15_24_zk": 21,
}

# Mapa canónico — 3 variantes de grupo etario según la fuente:
# 'Grupo Etario' (cg, de), 'Grupo etario' (ck, dg, ma), 'Grupo_Etario' (zk)
MAPA_CANONICO = {
    "Año":           "anio",
    "Departamento":  "departamento",
    "Municipio":     "municipio",
    "Grupo Etario":  "grupo_etario",
    "Grupo etario":  "grupo_etario",
    "Grupo_Etario":  "grupo_etario",
    "Sexo":          "sexo",
    "Casos":         "cantidad",
}

# ETPV no tiene CIE ni Diagnóstico en el CSV — se asigna CIE fijo por id_fd
COLS_CANONICAS = [
    "anio",
    "departamento",
    "municipio",
    "grupo_etario",
    "sexo",
    "cantidad",
    "id_fd",
]


# =============================================================
# Consolidación de DataFrames ETPV
# =============================================================

def consolidar_etpv(dfs_etpv: dict) -> pd.DataFrame:
    """
    Consolida los 6 DataFrames de Enfermedades Transmitidas por Vectores.

    Parámetros:
        dfs_etpv: dict con keys 'df_url_etpv_y12_24_cg' ... 'df_url_etpv_y15_24_zk'

    Retorna:
        DataFrame consolidado con columnas canónicas
    """
    dfs_normalizados = []

    for nombre, df in dfs_etpv.items():
        df_n = df.copy()

        # Renombrar con el mapa exacto
        df_n = df_n.rename(columns=MAPA_CANONICO)

        # Agregar columnas faltantes como None
        for col in COLS_CANONICAS:
            if col not in df_n.columns:
                df_n[col] = None

        # Asignar id_fd
        df_n["id_fd"] = MAPA_ID_FD.get(nombre, None)

        print(f"✅ {nombre}: id_fd={MAPA_ID_FD.get(nombre)}, filas={len(df_n):,}")

        df_n = df_n[COLS_CANONICAS]
        dfs_normalizados.append(df_n)

    df_consolidado = pd.concat(dfs_normalizados, ignore_index=True)
    print(f"\n══ ETPV consolidado: {len(df_consolidado):,} registros ══")
    return df_consolidado


# =============================================================
# Transformación ETPV
# =============================================================

def transformar_etpv(dfs_etpv: dict, cat_ubicacion: pd.DataFrame,
                     cat_ge: pd.DataFrame) -> pd.DataFrame:
    """
    Transforma los 6 datasets de Enfermedades Transmitidas por Vectores
    y retorna un DataFrame listo para consolidar en h_mspas.

    Parámetros:
        dfs_etpv      : dict con las 6 fuentes ETPV
        cat_ubicacion : catálogo de ubicación geográfica
        cat_ge        : catálogo de grupo etario

    Retorna:
        DataFrame con columnas de h_mspas
    """
    d_fecha    = crear_d_fecha()
    mapeo_sexo = crear_mapeo_sexo()

    # 1. Consolidar los 6 DataFrames
    df = consolidar_etpv(dfs_etpv)

    # 2. Dimensión FECHA
    df = asignar_id_fecha(df, col_anio="anio", d_fecha=d_fecha)

    # 3. Dimensión UBICACION GEOGRAFICA
    df = asignar_id_ubicacion(
        df,
        col_depto="departamento",
        col_muni="municipio",
        cat_ubicacion=cat_ubicacion
    )

    # 4. Dimensión CIE — fijo por id_fd (ETPV no tiene columna CIE en el CSV)
    df = asignar_id_cie_por_fd(df, mapa_id_dcie=MAPA_ID_DCIE)

    # 5. Dimensión SEXO BIOLOGICO
    df = asignar_id_sexo(df, col_sexo="sexo", mapeo_sexo=mapeo_sexo)

    # 6. Dimensión GRUPO ETARIO
    # Se aplica limpiar_grupo_etario también al catálogo para consistencia
    df["grupo_etario"] = df["grupo_etario"].apply(limpiar_grupo_etario)
    cat_ge = cat_ge.copy()
    cat_ge["nombre_grupo_etario_fuente_origen"] = (
        cat_ge["nombre_grupo_etario_fuente_origen"].apply(limpiar_grupo_etario)
    )
    df = asignar_id_grupo_etario(df, col_ge="grupo_etario", cat_ge=cat_ge)

    # Verificación de nulos en grupo etario
    nulls = df["id_dge"].isna().sum()
    if nulls > 0:
        print(f"⚠️ Registros sin id_dge: {nulls}")
    else:
        print("✅ Todos los registros tienen id_dge resuelto")

    # 7. Dimensiones fijas
    df = asignar_id_modalidad_fijo(df, id_dma=ID_DMA_ETPV)
    df = asignar_id_dosis_fijo(df, id_dss=ID_DSS_ETPV)
    df = asignar_id_instrumento_fijo(df, id_isp=ID_ISP_ETPV)

    # 8. Fecha de carga
    df = agregar_fecha_carga(df)

    # 9. Seleccionar columnas finales
    df = seleccionar_cols_h_mspas(df)

    print(f"\n══ ETPV TOTAL: {len(df):,} registros ══")
    return df