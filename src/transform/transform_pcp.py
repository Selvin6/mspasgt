import re
import pandas as pd
from datetime import datetime
from src.transform.clean_data import limpiar_col
from src.transform.map_ids import (
    crear_d_fecha,
    asignar_id_fecha,
    asignar_id_ubicacion,
    asignar_id_modalidad,
    asignar_id_dosis_fijo,
    asignar_id_instrumento_fijo,
    agregar_fecha_carga,
    seleccionar_cols_h_mspas,
)


# =============================================================
# IDs fijos para PCP
# =============================================================
ID_FD_PCP   = 43     # Fuente: Producción de consultas y pacientes nuevos
ID_DCIE_PCP = 14608  # CIE fijo — no aplica CIE clínico
ID_DSB_PCP  = 2      # Sexo: No aplica
ID_DGE_PCP  = 2      # Grupo etario: No aplica
ID_DSS_PCP  = 2      # Dosis: No aplica
ID_ISP_PCP  = 2      # Instrumento: No aplica

# Columnas que se convierten de columnas a filas con melt
VALUE_VARS = [
    "Paciente Nuevo",
    "Primera Consulta",
    "Reconsulta",
    "Emergencia",
    "Inter consulta",
]


# =============================================================
# Transformación PCP
# =============================================================

def transformar_pcp(df_pcp: pd.DataFrame, cat_ubicacion: pd.DataFrame,
                    cat_modalidad: pd.DataFrame) -> pd.DataFrame:
    """
    Transforma el dataset de Producción de Consultas y Pacientes Nuevos
    y retorna un DataFrame listo para consolidar en h_mspas.

    Particularidades:
    - Requiere melt: convierte tipos de consulta de columnas a filas
    - Modalidad de atención se asigna por join desde tipo_consulta
    - CIE, sexo y grupo etario son fijos (no aplican para esta fuente)

    Parámetros:
        df_pcp        : DataFrame crudo de PCP
        cat_ubicacion : catálogo de ubicación geográfica
        cat_modalidad : catálogo de modalidad de atención

    Retorna:
        DataFrame con columnas de h_mspas
    """
    d_fecha = crear_d_fecha()
    df = df_pcp.copy()

    # 1. Limpiar nombres de columnas (espacios múltiples, inicio/final)
    df.columns = [limpiar_col(c) for c in df.columns]

    # 2. Melt — convertir tipos de consulta de columnas a filas
    df = pd.melt(
        df,
        id_vars=["Año", "Departamento", "Municipio"],
        value_vars=VALUE_VARS,
        var_name="tipo_consulta",
        value_name="cantidad"
    )

    # 3. Renombrar columnas de identidad al canónico
    df = df.rename(columns={
        "Año":          "anio",
        "Departamento": "departamento",
        "Municipio":    "municipio",
    })

    print(f"Filas después del melt: {len(df):,}")

    # 4. Limpiar cantidad — quitar comas y convertir a int64
    df["cantidad"] = (
        df["cantidad"]
        .astype(str)
        .str.strip()
        .str.replace(",", "", regex=False)
        .astype("int64")
    )

    # 5. Dimensión FECHA
    df = asignar_id_fecha(df, col_anio="anio", d_fecha=d_fecha)

    # 6. Dimensión UBICACION GEOGRAFICA
    df = asignar_id_ubicacion(
        df,
        col_depto="departamento",
        col_muni="municipio",
        cat_ubicacion=cat_ubicacion
    )

    # 7. Dimensión CIE — fijo (PCP no tiene CIE clínico)
    df["id_dcie"] = ID_DCIE_PCP

    # 8. Dimensión SEXO BIOLOGICO — fijo (PCP no desagrega por sexo)
    df["id_dsb"] = ID_DSB_PCP

    # 9. Dimensión GRUPO ETARIO — fijo (PCP no desagrega por grupo etario)
    df["id_dge"] = ID_DGE_PCP

    # 10. Dimensión MODALIDAD ATENCION — por join desde tipo_consulta
    # Es la única fuente donde la modalidad viene del dato (no es fija)
    df = asignar_id_modalidad(
        df,
        col_modalidad="tipo_consulta",
        cat_modalidad=cat_modalidad
    )

    # 11. Dosis e instrumento — fijos
    df = asignar_id_dosis_fijo(df, id_dss=ID_DSS_PCP)
    df = asignar_id_instrumento_fijo(df, id_isp=ID_ISP_PCP)

    # 12. Fuente de datos
    df["id_fd"] = ID_FD_PCP

    # 13. Fecha de carga
    df = agregar_fecha_carga(df)

    # 14. Seleccionar columnas finales
    df = seleccionar_cols_h_mspas(df)

    print(f"\n══ PCP TOTAL: {len(df):,} registros ══")
    return df