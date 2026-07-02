import pandas as pd
from datetime import datetime
from src.transform.clean_data import limpiar_col, normalizar_nombre_columna
from src.transform.map_ids import (
    crear_d_fecha,
    asignar_id_fecha,
    asignar_id_ubicacion,
    asignar_id_grupo_etario,
    asignar_id_dosis,
    asignar_id_instrumento,
    asignar_id_modalidad_fijo,
    limpiar_grupo_etario,
    agregar_fecha_carga,
    seleccionar_cols_h_mspas,
)


# =============================================================
# IDs fijos para SNM
# =============================================================
ID_FD_SNM   = 44     # Fuente: Suplementación niños menores 5 años
ID_DCIE_SNM = 14608  # CIE fijo — no aplica CIE clínico
ID_DSB_SNM  = 2      # Sexo: No aplica
ID_DMA_SNM  = 2      # Modalidad: No aplica


# =============================================================
# Transformación SNM
# =============================================================

def transformar_snm(df_snm: pd.DataFrame, cat_ubicacion: pd.DataFrame,
                    cat_ge: pd.DataFrame, cat_dosis: pd.DataFrame,
                    cat_instrumento: pd.DataFrame) -> pd.DataFrame:
    """
    Transforma el dataset de Suplementación en Niños Menores de 5 años
    y retorna un DataFrame listo para consolidar en h_mspas.

    Particularidades:
    - Normalización especial de columnas: limpiar_col + normalizar_nombre_columna
    - Columna año queda como 'ano' (sin tilde) después de normalizar
    - Grupo etario viene como 'rango_de_edad' → se renombra a 'grupo_etario'
    - Cantidad viene como 'total' → se renombra a 'cantidad'
    - Dosis e instrumento se asignan por join (únicos variables en SNM)

    Parámetros:
        df_snm          : DataFrame crudo de SNM
        cat_ubicacion   : catálogo de ubicación geográfica
        cat_ge          : catálogo de grupo etario
        cat_dosis       : catálogo de dosis
        cat_instrumento : catálogo de instrumento de suplementación

    Retorna:
        DataFrame con columnas de h_mspas
    """
    d_fecha = crear_d_fecha()
    df = df_snm.copy()

    # 1. Limpiar columnas — primero quitar espacios múltiples
    df.columns = [limpiar_col(c) for c in df.columns]

    # 2. Normalizar nombres de columna — quitar tildes y caracteres especiales
    # Esto convierte 'Año' → 'ano', 'Municipio' → 'municipio', etc.
    df.columns = [normalizar_nombre_columna(c) for c in df.columns]

    # 3. Dimensión FECHA — columna queda como 'ano' (sin tilde) después de normalizar
    df = asignar_id_fecha(df, col_anio="ano", d_fecha=d_fecha)

    # 4. Dimensión UBICACION GEOGRAFICA
    df = asignar_id_ubicacion(
        df,
        col_depto="departamento",
        col_muni="municipio",
        cat_ubicacion=cat_ubicacion
    )

    # 5. Dimensión CIE — fijo (SNM no tiene CIE clínico)
    df["id_dcie"] = ID_DCIE_SNM

    # 6. Dimensión SEXO BIOLOGICO — fijo (SNM no desagrega por sexo)
    df["id_dsb"] = ID_DSB_SNM

    # 7. Dimensión GRUPO ETARIO
    # SNM tiene columna 'rango_de_edad' → renombrar a 'grupo_etario'
    df = df.rename(columns={"rango_de_edad": "grupo_etario"})
    df["grupo_etario"] = df["grupo_etario"].apply(limpiar_grupo_etario)
    cat_ge = cat_ge.copy()
    cat_ge["nombre_grupo_etario_fuente_origen"] = (
        cat_ge["nombre_grupo_etario_fuente_origen"].apply(limpiar_grupo_etario)
    )
    df = asignar_id_grupo_etario(df, col_ge="grupo_etario", cat_ge=cat_ge)

    # 8. Dimensión MODALIDAD ATENCION — fija (SNM no tiene modalidad)
    df = asignar_id_modalidad_fijo(df, id_dma=ID_DMA_SNM)

    # 9. Dimensión DOSIS — por join desde catálogo (variable en SNM)
    df = asignar_id_dosis(df, col_dosis="dosis", cat_dosis=cat_dosis)

    # 10. Dimensión INSTRUMENTO SUPLEMENTACION — por join desde catálogo (variable en SNM)
    df = asignar_id_instrumento(
        df,
        col_instrumento="instrumento_suplementacion",
        cat_instrumento=cat_instrumento
    )

    # 11. Fuente de datos
    df["id_fd"] = ID_FD_SNM

    # 12. Renombrar cantidad — en SNM viene como 'total'
    df = df.rename(columns={"total": "cantidad"})

    # 13. Fecha de carga
    df = agregar_fecha_carga(df)

    # 14. Seleccionar columnas finales
    df = seleccionar_cols_h_mspas(df)

    print(f"\n══ SNM TOTAL: {len(df):,} registros ══")
    return df