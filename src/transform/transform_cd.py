import pandas as pd
from datetime import datetime
from src.transform.map_ids import (
    crear_d_fecha,
    crear_mapeo_sexo,
    asignar_id_fecha,
    asignar_id_ubicacion,
    asignar_id_sexo,
    asignar_id_grupo_etario,
    asignar_id_modalidad_fijo,
    asignar_id_dosis_fijo,
    asignar_id_instrumento_fijo,
    agregar_fecha_carga,
    seleccionar_cols_h_mspas,
)


# =============================================================
# IDs fijos para Categoría Desnutrición
# =============================================================
ID_DCIE_CD  = 14411  # CIE fijo para ambas fuentes
ID_DMA_CD   = 2      # Modalidad: No aplica
ID_DSS_CD   = 2      # Dosis: No aplica
ID_ISP_CD   = 2      # Instrumento: No aplica

MAPA_ID_FD = {
    "mda": 1,  # Morbilidad Desnutrición Aguda
    "mrd": 2,  # Morbilidad Retardo Desarrollo
}


# =============================================================
# Transformación Categoría Desnutrición
# =============================================================

def transformar_cd(dfs_cd: dict, cat_ubicacion: pd.DataFrame, cat_ge: pd.DataFrame) -> pd.DataFrame:
    """
    Transforma los datasets de Categoría Desnutrición (mda, mrd)
    y retorna un DataFrame listo para consolidar en h_mspas.

    Parámetros:
        dfs_cd        : dict con keys 'mda' y 'mrd' (DataFrames crudos)
        cat_ubicacion : catálogo de ubicación geográfica
        cat_ge        : catálogo de grupo etario

    Retorna:
        DataFrame con columnas de h_mspas
    """
    d_fecha    = crear_d_fecha()
    mapeo_sexo = crear_mapeo_sexo()

    dfs_transformados = []

    for nombre, df in dfs_cd.items():
        df_t = df.copy()

        # 1. Asignar id_fd
        df_t["id_fd"] = MAPA_ID_FD[nombre]

        # 2. Dimensión FECHA
        df_t = asignar_id_fecha(df_t, col_anio="Año", d_fecha=d_fecha)

        # 3. Dimensión UBICACION GEOGRAFICA
        df_t = asignar_id_ubicacion(
            df_t,
            col_depto="Departamento",
            col_muni="Municipio",
            cat_ubicacion=cat_ubicacion
        )

        # 4. Dimensión CIE (fijo para CD)
        df_t["id_dcie"] = ID_DCIE_CD

        # 5. Dimensión SEXO BIOLOGICO
        df_t = asignar_id_sexo(df_t, col_sexo="sexo", mapeo_sexo=mapeo_sexo)

        # 6. Dimensión GRUPO ETARIO
        df_t = asignar_id_grupo_etario(df_t, col_ge="grupo_etario", cat_ge=cat_ge)

        # 7. Dimensiones fijas
        df_t = asignar_id_modalidad_fijo(df_t, id_dma=ID_DMA_CD)
        df_t = asignar_id_dosis_fijo(df_t, id_dss=ID_DSS_CD)
        df_t = asignar_id_instrumento_fijo(df_t, id_isp=ID_ISP_CD)

        # 8. Renombrar cantidad
        if "cantidad" not in df_t.columns:
            col_cantidad = next(
                (c for c in df_t.columns if c.lower().strip() == "cantidad"), None
            )
            if col_cantidad:
                df_t = df_t.rename(columns={col_cantidad: "cantidad"})

        # 9. Fecha de carga
        df_t = agregar_fecha_carga(df_t)

        # 10. Seleccionar columnas finales
        df_t = seleccionar_cols_h_mspas(df_t)

        print(f"✅ CD - {nombre}: {len(df_t):,} registros | id_fd={MAPA_ID_FD[nombre]}")
        dfs_transformados.append(df_t)

    df_cd_final = pd.concat(dfs_transformados, ignore_index=True)
    print(f"\n══ CD TOTAL: {len(df_cd_final):,} registros ══")
    return df_cd_final