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
# IDs fijos para MIE
# =============================================================
ID_DMA_MIE = 2  # Modalidad: No aplica
ID_DSS_MIE = 2  # Dosis: No aplica
ID_ISP_MIE = 2  # Instrumento: No aplica

# CIE fijo por fuente — MIE no tiene columna CIE en el CSV
MAPA_ID_DCIE = {
    28: 14376,  # ETAS
    29: 14607,  # IRAS
}

# Caso especial: id_fd=28 (etas) tiene nulos en grupo etario → id_dge=1
ID_FD_GE_NULO = 28
ID_DGE_DEFAULT = 1

MAPA_ID_FD = {
    "df_url_mie_y12_24_et": 28,  # ETAS
    "df_url_mie_y12_24_ir": 29,  # IRAS
}

# Mapa canónico — casos especiales:
# etas → 'Grupo Etario' con espacio, 'Cantidad' como medida
# iras → 'GrupoEtario' sin espacio, 'Casos' como medida
MAPA_CANONICO = {
    "Año":           "anio",
    "Departamento":  "departamento",
    "Municipio":     "municipio",
    "Grupo Etario":  "grupo_etario",  # etas
    "GrupoEtario":   "grupo_etario",  # iras
    "Sexo":          "sexo",
    "Cantidad":      "cantidad",      # etas
    "Casos":         "cantidad",      # iras
}

# MIE no tiene CIE ni Diagnóstico en el CSV
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
# Consolidación de DataFrames MIE
# =============================================================

def consolidar_mie(dfs_mie: dict) -> pd.DataFrame:
    """
    Consolida los 2 DataFrames de Morbilidad IRAS y ETAS.

    Parámetros:
        dfs_mie: dict con keys 'df_url_mie_y12_24_et' y 'df_url_mie_y12_24_ir'

    Retorna:
        DataFrame consolidado con columnas canónicas
    """
    dfs_normalizados = []

    for nombre, df in dfs_mie.items():
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
    print(f"\n══ MIE consolidado: {len(df_consolidado):,} registros ══")
    return df_consolidado


# =============================================================
# Transformación MIE
# =============================================================

def transformar_mie(dfs_mie: dict, cat_ubicacion: pd.DataFrame,
                    cat_ge: pd.DataFrame) -> pd.DataFrame:
    """
    Transforma los 2 datasets de Morbilidad IRAS y ETAS
    y retorna un DataFrame listo para consolidar en h_mspas.

    Parámetros:
        dfs_mie       : dict con las 2 fuentes MIE
        cat_ubicacion : catálogo de ubicación geográfica
        cat_ge        : catálogo de grupo etario

    Retorna:
        DataFrame con columnas de h_mspas
    """
    d_fecha    = crear_d_fecha()
    mapeo_sexo = crear_mapeo_sexo()

    # 1. Consolidar los 2 DataFrames
    df = consolidar_mie(dfs_mie)

    # 2. Dimensión FECHA
    df = asignar_id_fecha(df, col_anio="anio", d_fecha=d_fecha)

    # 3. Dimensión UBICACION GEOGRAFICA
    df = asignar_id_ubicacion(
        df,
        col_depto="departamento",
        col_muni="municipio",
        cat_ubicacion=cat_ubicacion
    )

    # 4. Dimensión CIE — fijo por id_fd (MIE no tiene columna CIE en el CSV)
    df = asignar_id_cie_por_fd(df, mapa_id_dcie=MAPA_ID_DCIE)

    # 5. Dimensión SEXO BIOLOGICO
    df = asignar_id_sexo(df, col_sexo="sexo", mapeo_sexo=mapeo_sexo)

    # 6. Dimensión GRUPO ETARIO
    df["grupo_etario"] = df["grupo_etario"].apply(limpiar_grupo_etario)
    cat_ge = cat_ge.copy()
    cat_ge["nombre_grupo_etario_fuente_origen"] = (
        cat_ge["nombre_grupo_etario_fuente_origen"].apply(limpiar_grupo_etario)
    )
    df = asignar_id_grupo_etario(df, col_ge="grupo_etario", cat_ge=cat_ge)

    # Caso especial: id_fd=28 (etas) tiene nulos en grupo etario → id_dge=1
    df.loc[
        (df["id_fd"] == ID_FD_GE_NULO) & (df["id_dge"].isna()),
        "id_dge"
    ] = ID_DGE_DEFAULT
    df["id_dge"] = df["id_dge"].astype("int64")

    # 7. Dimensiones fijas
    df = asignar_id_modalidad_fijo(df, id_dma=ID_DMA_MIE)
    df = asignar_id_dosis_fijo(df, id_dss=ID_DSS_MIE)
    df = asignar_id_instrumento_fijo(df, id_isp=ID_ISP_MIE)

    # 8. Fecha de carga
    df = agregar_fecha_carga(df)

    # 9. Seleccionar columnas finales
    df = seleccionar_cols_h_mspas(df)

    print(f"\n══ MIE TOTAL: {len(df):,} registros ══")
    return df