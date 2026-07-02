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
# IDs fijos para MGM
# =============================================================
ID_DMA_MGM = 2  # Modalidad: No aplica
ID_DSS_MGM = 2  # Dosis: No aplica
ID_ISP_MGM = 2  # Instrumento: No aplica

# id_fd=23 (materna) no tiene columna sexo → se asigna id_dsb=2
ID_FD_SIN_SEXO = 23
ID_DSB_DEFAULT = 2

MAPA_ID_FD = {
    "neonatal":       22,  # Neonatal
    "materna":        23,  # Materna
    "infantil_12_15": 24,  # Infantil 2012-2015
    "infantil_16_19": 25,  # Infantil 2016-2019
    "infantil_20_23": 26,  # Infantil 2020-2023
    "infantil_24":    27,  # Infantil 2024
}

# Mapa canónico — casos especiales:
# nn → 'Diagnóstico ' con espacio, 'grupo etario' minúsculas,
#       'sexo' minúsculas, 'cantidad' minúsculas
# mt → no tiene sexo
# if → 'Sexo' Title Case, 'Casos' en vez de 'cantidad'
MAPA_CANONICO = {
    "Año":           "anio",
    "Departamento":  "departamento",
    "Municipio":     "municipio",
    "CIE-10":        "cie10",
    "Diagnóstico ":  "diagnostico",   # nn — espacio al final
    "Diagnóstico":   "diagnostico",   # mt, if
    "grupo etario":  "grupo_etario",  # nn — minúsculas
    "Grupo Etario":  "grupo_etario",  # mt, if
    "sexo":          "sexo",          # nn — minúsculas
    "Sexo":          "sexo",          # if
    "cantidad":      "cantidad",      # nn — ya canónico
    "Casos":         "cantidad",      # mt, if
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
# Consolidación de DataFrames MGM
# =============================================================

def consolidar_mgm(dfs_mgm: dict) -> pd.DataFrame:
    """
    Consolida los 6 DataFrames de Morbilidad Grupo Materno Infantil.

    Parámetros:
        dfs_mgm: dict con keys 'df_url_mgm_y12_24_nn' ... 'df_url_mgm_y24_if'

    Retorna:
        DataFrame consolidado con columnas canónicas
    """
    dfs_normalizados = []

    for nombre, df in dfs_mgm.items():
        df_n = df.copy()

        # Renombrar con el mapa exacto
        df_n = df_n.rename(columns=MAPA_CANONICO)

        # Agregar columnas faltantes como None
        # nn y mt no tienen 'sexo'
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
    print(f"\n══ MGM consolidado: {len(df_consolidado):,} registros ══")
    return df_consolidado


# =============================================================
# Transformación MGM
# =============================================================

def transformar_mgm(dfs_mgm: dict, cat_ubicacion: pd.DataFrame,
                    cat_cie: pd.DataFrame, cat_ge: pd.DataFrame) -> pd.DataFrame:
    """
    Transforma los 6 datasets de Morbilidad Grupo Materno Infantil
    y retorna un DataFrame listo para consolidar en h_mspas.

    Parámetros:
        dfs_mgm       : dict con las 6 fuentes MGM
        cat_ubicacion : catálogo de ubicación geográfica
        cat_cie       : catálogo CIE
        cat_ge        : catálogo de grupo etario

    Retorna:
        DataFrame con columnas de h_mspas
    """
    d_fecha    = crear_d_fecha()
    mapeo_sexo = crear_mapeo_sexo()

    # 1. Consolidar los 6 DataFrames
    df = consolidar_mgm(dfs_mgm)

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

    # Caso especial: id_fd=23 (materna) no tiene sexo → asignar id_dsb=2
    df.loc[
        (df["id_fd"] == ID_FD_SIN_SEXO) & (df["id_dsb"].isna()),
        "id_dsb"
    ] = ID_DSB_DEFAULT

    # Convertir a entero
    df["id_dsb"] = df["id_dsb"].astype("int64")

    # 6. Dimensión GRUPO ETARIO
    df["grupo_etario"] = df["grupo_etario"].apply(limpiar_grupo_etario)
    cat_ge = cat_ge.copy()
    cat_ge["nombre_grupo_etario_fuente_origen"] = (
        cat_ge["nombre_grupo_etario_fuente_origen"].apply(limpiar_grupo_etario)
    )
    df = asignar_id_grupo_etario(df, col_ge="grupo_etario", cat_ge=cat_ge)

    # 7. Dimensiones fijas
    df = asignar_id_modalidad_fijo(df, id_dma=ID_DMA_MGM)
    df = asignar_id_dosis_fijo(df, id_dss=ID_DSS_MGM)
    df = asignar_id_instrumento_fijo(df, id_isp=ID_ISP_MGM)

    # 8. Fecha de carga
    df = agregar_fecha_carga(df)

    # 9. Seleccionar columnas finales
    df = seleccionar_cols_h_mspas(df)

    print(f"\n══ MGM TOTAL: {len(df):,} registros ══")
    return df