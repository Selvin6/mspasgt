import pandas as pd
import os
from src.config.settings import OUTPUT_DIR


# =============================================================
# Columnas requeridas en h_mspas (modelo dimensional Kimball)
# =============================================================
COLS_REQUERIDAS = [
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


# =============================================================
# Validación de columnas
# =============================================================

def validar_dataframes(dfs: dict) -> tuple:
    """
    Verifica que cada DataFrame tenga las columnas requeridas por h_mspas.

    Retorna:
        (reporte_ok, reporte_errores) — listas de dicts con el resultado
    """
    reporte_ok      = []
    reporte_errores = []

    for nombre, df in dfs.items():
        cols_df        = set(df.columns)
        cols_faltantes = [c for c in COLS_REQUERIDAS if c not in cols_df]
        cols_extra     = [c for c in cols_df if c not in COLS_REQUERIDAS]

        if cols_faltantes:
            reporte_errores.append({
                "dataframe":          nombre,
                "filas":              len(df),
                "columnas_faltantes": cols_faltantes,
                "columnas_extra":     cols_extra,
            })
            print(f"❌ {nombre}: faltan {cols_faltantes}")
        else:
            reporte_ok.append({
                "dataframe": nombre,
                "filas":     len(df),
            })
            print(f"✅ {nombre}: OK — {len(df):,} filas")

    print("\n══ REPORTE DE ERRORES ══")
    if reporte_errores:
        print(pd.DataFrame(reporte_errores).to_string(index=False))
    else:
        print("Sin errores — todos los DataFrames tienen las columnas requeridas")

    print("\n══ REPORTE OK ══")
    print(pd.DataFrame(reporte_ok).to_string(index=False))

    return reporte_ok, reporte_errores


# =============================================================
# Consolidación en h_mspas
# =============================================================

def consolidar_h_mspas(dfs_transformados: dict) -> pd.DataFrame:
    """
    Consolida todos los DataFrames transformados en la tabla de hechos h_mspas.

    Proceso:
        1. Validar que cada DF tiene las columnas requeridas
        2. Concatenar solo los DFs que pasaron validación
        3. Agregar id_hmspas incremental
        4. Exportar a data/output/h_mspas.csv

    Parámetros:
        dfs_transformados: dict con los DataFrames ya transformados de cada fuente

    Retorna:
        DataFrame h_mspas completo
    """
    # Paso 1 — Validación
    reporte_ok, reporte_errores = validar_dataframes(dfs_transformados)

    if reporte_errores:
        print(f"\n⚠️  {len(reporte_errores)} DataFrames con errores — se excluyen del consolidado")

    # Paso 2 — Concat solo los válidos
    nombres_ok = {r["dataframe"] for r in reporte_ok}

    dfs_validos = [
        dfs_transformados[nombre][COLS_REQUERIDAS]
        for nombre in dfs_transformados
        if nombre in nombres_ok
    ]

    if not dfs_validos:
        raise ValueError("⚠️  Ningún DataFrame pasó la validación — h_mspas no se construyó")

    h_mspas = pd.concat(dfs_validos, ignore_index=True)

    # Paso 3 — id_hmspas incremental de 1 en 1
    h_mspas.insert(0, "id_hmspas", range(1, len(h_mspas) + 1))

    print(f"\n══ h_mspas CONSTRUIDA ══")
    print(f"Filas totales : {h_mspas.shape[0]:,}")
    print(f"Columnas      : {list(h_mspas.columns)}")
    print(f"\nFilas por id_fd:")
    print(h_mspas.groupby("id_fd").size().reset_index(name="filas"))

    return h_mspas


# =============================================================
# Exportación
# =============================================================

def exportar_h_mspas(h_mspas: pd.DataFrame, nombre_archivo: str = "h_mspas.csv") -> str:
    """
    Exporta h_mspas a CSV en data/output/.

    Parámetros:
        h_mspas        : DataFrame consolidado
        nombre_archivo : nombre del archivo de salida

    Retorna:
        Ruta completa del archivo exportado
    """
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    ruta = os.path.join(OUTPUT_DIR, nombre_archivo)
    h_mspas.to_csv(ruta, index=False, encoding="utf-8-sig")
    print(f"\n✅ h_mspas exportada: {ruta}")
    print(f"   Filas: {len(h_mspas):,} | Columnas: {len(h_mspas.columns)}")
    return ruta