"""
main.py — Punto de entrada del ETL MSPAS

Orquesta el flujo completo:
    Extract  → Descarga CSVs desde el portal de datos abiertos del MSPAS
    Transform → Limpia, normaliza y asigna IDs de dimensiones
    Load     → Consolida en h_mspas y exporta a CSV para Power BI
"""

from src.extract.fetch_data import extraer_todo
from src.transform.map_ids import (
    cargar_catalogo_cie,
    cargar_catalogo_ubicacion,
    cargar_catalogo_grupo_etario,
    cargar_catalogo_dosis,
    cargar_catalogo_instrumento,
    cargar_catalogo_modalidad,
)
from src.transform.transform_cd  import transformar_cd
from src.transform.transform_cec import transformar_cec
from src.transform.transform_etpv import transformar_etpv
from src.transform.transform_mgm import transformar_mgm
from src.transform.transform_mie import transformar_mie
from src.transform.transform_pcm import transformar_pcm
from src.transform.transform_pcp import transformar_pcp
from src.transform.transform_snm import transformar_snm
from src.transform.consolidar import consolidar_h_mspas, exportar_h_mspas


def main():
    print("=" * 60)
    print("ETL MSPAS — Inicio")
    print("=" * 60)

    # ─────────────────────────────────────────────────────────
    # EXTRACT — Descarga de todas las fuentes
    # ─────────────────────────────────────────────────────────
    print("\n[1/3] EXTRACT")
    datos = extraer_todo()

    # ─────────────────────────────────────────────────────────
    # Carga de catálogos (una sola vez)
    # ─────────────────────────────────────────────────────────
    print("\nCargando catálogos...")
    cat_cie        = cargar_catalogo_cie()
    cat_ubicacion  = cargar_catalogo_ubicacion()
    cat_ge         = cargar_catalogo_grupo_etario()
    cat_dosis      = cargar_catalogo_dosis()
    cat_instrumento = cargar_catalogo_instrumento()
    cat_modalidad  = cargar_catalogo_modalidad()
    print("✅ Catálogos cargados")

    # ─────────────────────────────────────────────────────────
    # TRANSFORM — Transformación por fuente
    # ─────────────────────────────────────────────────────────
    print("\n[2/3] TRANSFORM")

    print("\n→ CD: Desnutrición")
    df_cd = transformar_cd(
        dfs_cd=datos["cd"],
        cat_ubicacion=cat_ubicacion,
        cat_ge=cat_ge
    )

    print("\n→ CEC: Enfermedades Crónicas")
    df_cec = transformar_cec(
        dfs_cec=datos["cec"],
        cat_ubicacion=cat_ubicacion,
        cat_cie=cat_cie,
        cat_ge=cat_ge
    )

    print("\n→ ETPV: Enfermedades Transmitidas por Vectores")
    df_etpv = transformar_etpv(
        dfs_etpv=datos["etpv"],
        cat_ubicacion=cat_ubicacion,
        cat_ge=cat_ge
    )

    print("\n→ MGM: Morbilidad Grupo Materno Infantil")
    df_mgm = transformar_mgm(
        dfs_mgm=datos["mgm"],
        cat_ubicacion=cat_ubicacion,
        cat_cie=cat_cie,
        cat_ge=cat_ge
    )

    print("\n→ MIE: Morbilidad IRAS y ETAS")
    df_mie = transformar_mie(
        dfs_mie=datos["mie"],
        cat_ubicacion=cat_ubicacion,
        cat_ge=cat_ge
    )

    print("\n→ PCM: 20 Primeras Causas de Morbilidad")
    df_pcm = transformar_pcm(
        dfs_pcm=datos["pcm"],
        cat_ubicacion=cat_ubicacion,
        cat_cie=cat_cie,
        cat_ge=cat_ge
    )

    print("\n→ PCP: Producción de Consultas y Pacientes Nuevos")
    df_pcp = transformar_pcp(
        df_pcp=datos["pcp"],
        cat_ubicacion=cat_ubicacion,
        cat_modalidad=cat_modalidad
    )

    print("\n→ SNM: Suplementación Niños Menores 5 Años")
    df_snm = transformar_snm(
        df_snm=datos["snm"],
        cat_ubicacion=cat_ubicacion,
        cat_ge=cat_ge,
        cat_dosis=cat_dosis,
        cat_instrumento=cat_instrumento
    )

    # ─────────────────────────────────────────────────────────
    # LOAD — Consolidación y exportación
    # ─────────────────────────────────────────────────────────
    print("\n[3/3] LOAD")

    dfs_transformados = {
        "cd":   df_cd,
        "cec":  df_cec,
        "etpv": df_etpv,
        "mgm":  df_mgm,
        "mie":  df_mie,
        "pcm":  df_pcm,
        "pcp":  df_pcp,
        "snm":  df_snm,
    }

    h_mspas = consolidar_h_mspas(dfs_transformados)
    exportar_h_mspas(h_mspas)

    print("\n" + "=" * 60)
    print("ETL MSPAS — Completado exitosamente")
    print("=" * 60)


if __name__ == "__main__":
    main()