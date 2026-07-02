# ETL MSPAS Guatemala

Pipeline de extracción, transformación y carga de datos de salud pública del **Ministerio de Salud Pública y Asistencia Social de Guatemala (MSPAS)**.

## Descripción

Este proyecto consolida **8 fuentes de datos abiertos** del portal [datosabiertos.mspas.gob.gt](https://datosabiertos.mspas.gob.gt) en una única tabla de hechos (`h_mspas`) siguiendo el modelo dimensional **Kimball (Constelación)**, lista para ser consumida por Power BI.

## Fuentes de datos

| Clave | Descripción | Período |
| --- | --- | --- |
| CD | Morbilidad por Desnutrición (Aguda y Retardo) | 2012–2024 |
| CEC | Enfermedades Crónicas | 2012–2024 |
| ETPV | Enfermedades Transmitidas por Vectores | 2012–2024 |
| MGM | Morbilidad Grupo Materno Infantil | 2012–2024 |
| MIE | Morbilidad IRAS y ETAS | 2012–2024 |
| PCM | 20 Primeras Causas de Morbilidad | 2012–2024 |
| PCP | Producción de Consultas y Pacientes Nuevos | 2012–2024 |
| SNM | Suplementación Niños Menores 5 Años | 2013–2024 |

## Modelo dimensional

Arquitectura **Kimball (Constelación)** con:

- `h_mspas` — Tabla de hechos principal con 4,935,288 registros
- 8 dimensiones: `d_fecha`, `d_ubicacion_geografica`, `d_cie`, `d_sexo_biologico`, `d_grupo_etario`, `d_modalidad_atencion`, `d_dosis`, `d_instrumento_suplementacion`

## Estructura del proyecto

```text
mspasgt/
├── data/
│   ├── input/
│   │   ├── catalogos/        # Catálogos de mapeo para asignar IDs
│   │   └── raw/              # CSVs descargados en tiempo de ejecución
│   └── output/               # h_mspas.csv (generado por el ETL)
├── src/
│   ├── config/
│   │   └── settings.py       # URLs de fuentes y rutas del proyecto
│   ├── extract/
│   │   └── fetch_data.py     # Descarga de CSVs desde el portal MSPAS
│   ├── transform/
│   │   ├── clean_data.py     # Funciones de limpieza y normalización
│   │   ├── map_ids.py        # Asignación de IDs de dimensiones
│   │   ├── transform_cd.py   # Transformación Desnutrición
│   │   ├── transform_cec.py  # Transformación Enfermedades Crónicas
│   │   ├── transform_etpv.py # Transformación Vectores
│   │   ├── transform_mgm.py  # Transformación Materno Infantil
│   │   ├── transform_mie.py  # Transformación IRAS y ETAS
│   │   ├── transform_pcm.py  # Transformación 20 Primeras Causas
│   │   ├── transform_pcp.py  # Transformación Consultas y Pacientes
│   │   ├── transform_snm.py  # Transformación Suplementación
│   │   └── consolidar.py     # Consolidación en h_mspas
│   └── main.py               # Punto de entrada del ETL
├── requirements/
│   ├── base.txt              # Dependencias de producción
│   ├── dev.txt               # Dependencias de desarrollo
│   └── prod.txt              # Dependencias mínimas de producción
├── .env                      # Variables de entorno (no versionado)
├── .gitignore
└── README.md
```

## Requisitos

- Python 3.10+
- Conexión a internet (descarga CSVs en tiempo de ejecución)

## Instalación

### macOS (Apple Silicon M1/M2/M3/M4)

```bash
# Clonar el repositorio
git clone git@github.com:Selvin6/mspasgt.git
cd mspasgt

# Crear entorno virtual
python3 -m venv .venv
source .venv/bin/activate

# Instalar dependencias
pip install -r requirements/base.txt
```

### Windows

```bash
# Clonar el repositorio
git clone git@github.com:Selvin6/mspasgt.git
cd mspasgt

# Crear entorno virtual
python -m venv .venv
.venv\Scripts\activate

# Instalar dependencias
pip install -r requirements/base.txt
```

> **Nota Windows:** Si al activar el entorno virtual aparece el error
> `execution of scripts is disabled`, ejecuta primero en PowerShell como administrador:
>
> ```powershell
> Set-ExecutionPolicy RemoteSigned
> ```

## Ejecución

### macOS

```bash
source .venv/bin/activate
python -m src.main
```

### Windows

```bash
.venv\Scripts\activate
python -m src.main
```

El ETL descarga automáticamente todos los CSVs desde el portal del MSPAS, los transforma y genera el archivo `data/output/h_mspas.csv`.

## Output

El archivo `h_mspas.csv` contiene las siguientes columnas:

| Columna | Descripción |
| --- | --- |
| `id_hmspas` | Llave primaria incremental |
| `id_df` | FK → Dimensión Fecha |
| `id_dug` | FK → Dimensión Ubicación Geográfica |
| `id_dcie` | FK → Dimensión CIE |
| `id_dsb` | FK → Dimensión Sexo Biológico |
| `id_dge` | FK → Dimensión Grupo Etario |
| `id_dma` | FK → Dimensión Modalidad Atención |
| `id_dss` | FK → Dimensión Dosis |
| `id_isp` | FK → Dimensión Instrumento Suplementación |
| `id_fd` | FK → Dimensión Fuente de Dataset |
| `cantidad` | Medida principal |
| `fecha_carga` | Timestamp de ejecución del ETL |

## Fuente de datos

Todos los datos provienen del portal de datos abiertos del MSPAS:
[https://datosabiertos.mspas.gob.gt](https://datosabiertos.mspas.gob.gt)

44 conjuntos de datos | Período 2012–2024
