"""
procesamiento.py — Módulo de preprocesamiento YRBS 2023
═══════════════════════════════════════════════════════
Proyecto : Salud Mental y Tiempo de Pantalla en Adolescentes
Dataset  : Youth Risk Behavior Survey (YRBS), CDC, 2023
Fuente   : https://www.cdc.gov/yrbs/data/index.html
Grupo    : 8 — MCDI500
"""

from pathlib import Path
import pandas as pd

# ══════════════════════════════════════════════════════════════
# CONSTANTES
# ══════════════════════════════════════════════════════════════

# Columnas seleccionadas del archivo original → nombre descriptivo
# Fuente: 2023_Data_Users_Guide_codebook.pdf, pág. 21–55
COLUMNAS_ANALISIS = {
    "record":   "id_registro",          # ID único de registro
    "weight":   "peso_muestral",        # Factor de expansión CDC
    "stratum":  "estrato",              # Estrato de diseño muestral
    "psu":      "psu",                  # Unidad primaria de muestreo
    "q1":       "edad_cod",             # Edad (1 = ≤12 años … 7 = ≥18 años)
    "q2":       "sexo_cod",             # Sexo (1 = Femenino, 2 = Masculino)
    "raceeth":  "raceeth_cod",          # Raza/etnicidad (8 categorías)
    "q84":      "salud_mental_cod",     # Salud mental percibida (1 = Never … 5 = Always)
    "q80":      "redes_sociales_cod",   # Horas/día en dispositivos electrónicos (1 = no usa … 8 = ≥6 h)
    "q85":      "sueno_cod",            # Horas de sueño (1 = ≤4 h … 7 = ≥10 h)
    "q76":      "actividad_fisica_cod", # Días activo ≥60 min (1 = 0 días … 8 = 7 días)
}

# Variables sin dependencia de pregunta anterior
# Verificado en Apéndice C del codebook oficial 2023.
# Sus nulos son "no responde genuino", NO "no aplica por salto de pregunta".
# Imputar un faltante estructural = inventar datos: aquí NO aplica.
COLUMNAS_SIN_DEPENDENCIA = [
    "q1", "q2", "raceeth", "q76", "q80", "q84", "q85"
]

# Escalas ordinales: valores válidos ordenados de menor a mayor
# ⚠️  NO tratar como numéricas continuas (ver sección 5 del notebook).
ESCALAS_ORDINALES = {
    "edad_cod":              [1, 2, 3, 4, 5, 6, 7],
    # 1 = ≤12 años, 2 = 13, 3 = 14, 4 = 15, 5 = 16, 6 = 17, 7 = ≥18 años

    "redes_sociales_cod":    [1, 2, 3, 4, 5, 6, 7, 8],
    # 1 = no usa, 2 = <1 h, 3 = 1 h, 4 = 2 h, 5 = 3 h, 6 = 4 h, 7 = 5 h, 8 = ≥6 h diarias

    "salud_mental_cod":      [1, 2, 3, 4, 5],
    # 1 = Never, 2 = Rarely, 3 = Sometimes, 4 = Most of the time, 5 = Always

    "sueno_cod":             [1, 2, 3, 4, 5, 6, 7],
    # 1 = ≤4 h, 2 = 5 h, 3 = 6 h, 4 = 7 h, 5 = 8 h, 6 = 9 h, 7 = ≥10 h por noche

    "actividad_fisica_cod":  [1, 2, 3, 4, 5, 6, 7, 8],
    # 1 = 0 días, 2 = 1 día, …, 8 = 7 días (última semana)
}


# ══════════════════════════════════════════════════════════════
# FUNCIONES
# ══════════════════════════════════════════════════════════════

def cargar_datos(ruta: str) -> pd.DataFrame:
    """
    Carga el CSV del YRBS 2023 tal como viene del CDC, con una única
    corrección de tipo documentada.

    Corrección aplicada (bitácora 2.2):
      dtype={'q6orig': 'string'} — resuelve el DtypeWarning causado por
      la mezcla de texto ("N N") y códigos numéricos en q6orig.
      La columna NO se descarta: la mezcla es un hallazgo de calidad
      real del archivo original y se documenta como tal.

    Nota: `orig_rec` se conserva en la carga para permitir su diagnóstico
    explícito en el notebook (bitácora 2.1). Su eliminación es una decisión
    del pipeline, no de la lectura del archivo.

    Args:
        ruta: ruta al CSV original (relativa al directorio de trabajo).

    Returns:
        DataFrame con 20.103 filas y 117 columnas.
    """
    return pd.read_csv(
        ruta,
        dtype={"q6orig": "string"},
        low_memory=False,
    )


def seleccionar_columnas(df: pd.DataFrame) -> pd.DataFrame:
    """
    Selecciona y renombra las columnas definidas en COLUMNAS_ANALISIS.

    La selección se hace por código desde el archivo original —
    nunca a mano — para garantizar reproducibilidad y trazabilidad.

    Args:
        df: DataFrame completo (116 columnas).

    Returns:
        DataFrame con 11 columnas renombradas.
    """
    cols_presentes = [c for c in COLUMNAS_ANALISIS if c in df.columns]
    return df[cols_presentes].rename(columns=COLUMNAS_ANALISIS)


def diagnosticar_datos(df: pd.DataFrame) -> dict:
    """
    Diagnóstico de calidad: nulos, duplicados y tipos de dato.

    Args:
        df: DataFrame a diagnosticar.

    Returns:
        dict con n_filas, n_columnas, pct_nulos_por_columna,
        duplicados_totales y tipos_de_dato.
    """
    pct_nulos = {
        col: round(df[col].isna().mean() * 100, 1)
        for col in df.columns
    }
    return {
        "n_filas":               len(df),
        "n_columnas":            df.shape[1],
        "pct_nulos_por_columna": pct_nulos,
        "duplicados_totales":    int(df.duplicated().sum()),
        "tipos_de_dato":         {col: str(dtype) for col, dtype in df.dtypes.items()},
    }


def clasificar_variables(df: pd.DataFrame) -> dict:
    """
    Clasifica cada variable según su rol metodológico (codebook 2023).

    ⚠️  El validador automático del curso clasifica las ordinales como
    "discretas" porque sus valores son enteros 1–8. Esa clasificación
    es incorrecta: son escalas de frecuencia/intensidad ordenadas.
    Tratarlas como numéricas asumiría equidistancia entre categorías,
    lo cual el diseño de la escala no garantiza.

    Args:
        df: DataFrame con columnas renombradas.

    Returns:
        dict: columna → {'rol_equipo': str, 'nota': str}
    """
    mapa = {
        "id_registro":           {"rol_equipo": "identificador",      "nota": "ID único del encuestado"},
        "peso_muestral":         {"rol_equipo": "muestral (weight)",  "nota": "factor de expansión CDC"},
        "estrato":               {"rol_equipo": "muestral (stratum)", "nota": "estrato de diseño muestral"},
        "psu":                   {"rol_equipo": "muestral (psu)",     "nota": "unidad primaria de muestreo"},
        "sexo_cod":              {"rol_equipo": "nominal",            "nota": "1 = Femenino, 2 = Masculino"},
        "raceeth_cod":           {"rol_equipo": "nominal",            "nota": "raza/etnicidad, 8 categorías"},
        "edad_cod":              {"rol_equipo": "ordinal",            "nota": "1 = ≤12 años … 7 = ≥18 años"},
        "actividad_fisica_cod":  {"rol_equipo": "ordinal",            "nota": "1 = 0 días … 8 = 7 días/semana"},
        "redes_sociales_cod":    {"rol_equipo": "ordinal",            "nota": "1 = no usa … 8 = ≥6 h/día"},
        "salud_mental_cod":      {"rol_equipo": "ordinal",            "nota": "1 = Never … 5 = Always"},
        "sueno_cod":             {"rol_equipo": "ordinal",            "nota": "1 = ≤4 h … 7 = ≥10 h por noche"},
    }
    return {col: info for col, info in mapa.items() if col in df.columns}


def transformar_datos(df: pd.DataFrame) -> pd.DataFrame:
    """
    Convierte variables ordinales a pd.Categorical ordenado.

    Hace explícito el orden y evita que pandas las trate como
    numéricas continuas en operaciones de análisis posteriores.
    Las nominales (sexo_cod, raceeth_cod) se conservan como float64
    hasta la fase de modelado (F4).

    Args:
        df: DataFrame seleccionado y diagnosticado.

    Returns:
        DataFrame con tipos corregidos.
    """
    df_t = df.copy()
    for col, valores in ESCALAS_ORDINALES.items():
        if col in df_t.columns:
            df_t[col] = pd.Categorical(
                df_t[col],
                categories=valores,
                ordered=True,
            )
    return df_t


def validar_datos(df: pd.DataFrame) -> dict:
    """
    Valida condiciones mínimas del DataFrame procesado:
    columnas obligatorias, unicidad de ID, sin duplicados
    y valores dentro del rango del codebook.

    Args:
        df: DataFrame transformado.

    Returns:
        dict con una clave por validación + 'validacion_global'.
    """
    cols_obligatorias = set(COLUMNAS_ANALISIS.values())
    resultado = {
        "columnas_obligatorias_presentes": cols_obligatorias.issubset(set(df.columns)),
        "id_registro_unico": (
            df["id_registro"].nunique() == len(df)
            if "id_registro" in df.columns else False
        ),
        "sin_duplicados": bool(df.duplicated().sum() == 0),
    }
    for col, valores_validos in ESCALAS_ORDINALES.items():
        if col in df.columns:
            vals = pd.to_numeric(df[col], errors="coerce").dropna()
            resultado[f"{col}_en_rango"] = bool(vals.isin(valores_validos).all())

    resultado["validacion_global"] = all(resultado.values())
    return resultado


def guardar_dataset(df: pd.DataFrame, ruta_relativa: str) -> Path:
    """
    Guarda el DataFrame procesado, creando directorios intermedios.

    Args:
        df: DataFrame procesado y validado.
        ruta_relativa: ruta relativa al directorio de trabajo del notebook.

    Returns:
        Path absoluto del archivo guardado.
    """
    ruta = Path(ruta_relativa)
    ruta.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(ruta, index=False)
    return ruta.resolve()


# Q5 admite respuestas múltiples de texto. raceeth combina Q4 y Q5 según CDC.
ESCALAS_NOMINALES = {"sexo_cod": [1, 2], "raceeth_cod": list(range(1, 9))}
ETIQUETAS_REDES = {1:"No usa", 2:"Unas veces al mes", 3:"Una vez a la semana",
    4:"Unas veces a la semana", 5:"Una vez al día", 6:"Varias veces al día",
    7:"Una vez por hora", 8:"Más de una vez por hora"}

def verificar_dominios(df):
    """Detecta códigos inválidos antes de que Categorical los oculte como NA."""
    errores = {}
    for col, permitidos in {**ESCALAS_ORDINALES, **ESCALAS_NOMINALES}.items():
        if col not in df: raise ValueError(f"Falta columna {col}")
        invalidos = df.loc[df[col].notna() & ~df[col].isin(permitidos), col]
        errores[col] = {str(k):int(v) for k,v in invalidos.value_counts().items()}
    return errores