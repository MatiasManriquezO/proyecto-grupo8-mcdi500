"""
carga.py — Entrada de datos: leer el archivo externo y verificar su esquema.

Las funciones de este módulo no conocen el pipeline: reciben una ruta y las
columnas que se esperan, y devuelven un DataFrame verificado. Por eso se
pueden usar igual con el archivo de la Fase 2 o con cualquier otro conjunto.

  leer_archivo       elige el lector según la extensión (.csv, .xlsx, .parquet).
  verificar_esquema  comprueba que estén las columnas declaradas.
  cargar             coordina existencia, lectura, conversión numérica y esquema.
  perfilar           tipo, valores únicos y porcentaje de nulos por columna.

Ubicación proyectada en la Tabla 8 de la Formativa 3 (capa «Entrada»).

Grupo 8 · MCDI500 · Universidad Andrés Bello
"""

from __future__ import annotations

import os
from pathlib import Path

import pandas as pd


def leer_archivo(ruta) -> pd.DataFrame:
    """Lee el archivo según su extensión y devuelve un DataFrame."""
    extension = os.path.splitext(str(ruta))[1].lower()

    if extension in (".csv", ".txt"):
        # sep=None con engine="python" infiere el separador: útil con datos
        # públicos chilenos, que suelen venir con punto y coma
        return pd.read_csv(ruta, sep=None, engine="python", encoding="utf-8")
    if extension in (".xlsx", ".xls"):
        return pd.read_excel(ruta)
    if extension == ".parquet":
        return pd.read_parquet(ruta)

    raise ValueError(
        f"Extensión no reconocida: '{extension}'. "
        "Se admiten .csv, .txt, .xlsx, .xls y .parquet."
    )


def verificar_esquema(df: pd.DataFrame, columnas_esperadas) -> dict:
    """Comprueba que estén todas las columnas declaradas en la configuración."""
    faltantes = [c for c in columnas_esperadas if c not in df.columns]
    if faltantes:
        raise KeyError(
            f"Faltan columnas declaradas en la configuración: {faltantes}\n"
            f"Columnas disponibles en el archivo: {list(df.columns)}"
        )
    sobrantes = [c for c in df.columns if c not in columnas_esperadas]
    return {"declaradas": len(columnas_esperadas),
            "en_archivo": df.shape[1],
            "no_declaradas": sobrantes}


def cargar(ruta, columnas_esperadas, columnas_numericas=(), raiz=None) -> pd.DataFrame:
    """Carga el conjunto desde el archivo externo y verifica su esquema.

    Parámetros
    ----------
    ruta               : ruta al archivo (CSV, Excel o Parquet).
    columnas_esperadas : columnas que deben estar; si falta alguna, KeyError.
    columnas_numericas : columnas de códigos que se fuerzan a número.
    raiz               : carpeta desde la que se informa la ruta (opcional).
    """
    if not os.path.exists(ruta):
        raise FileNotFoundError(
            f"No se encontró el archivo: {ruta}\n"
            f"Carpeta actual: {os.getcwd()}\n"
            "Revisen RUTA_DATOS en la celda de configuración del cuaderno."
        )
    df = leer_archivo(ruta)
    mostrar = Path(ruta).relative_to(raiz).as_posix() if raiz else Path(ruta).name
    print(f"Archivo leído: {mostrar}")

    # Las columnas de códigos se fuerzan a número: un texto suelto las
    # convertiría en columna de objetos sin ningún aviso
    for columna in columnas_numericas:
        df[columna] = pd.to_numeric(df[columna], errors="coerce")

    informe = verificar_esquema(df, columnas_esperadas)
    print(f"Forma: {df.shape[0]} filas x {df.shape[1]} columnas")
    print(f"Esquema verificado: {informe['declaradas']} columnas declaradas, "
          f"{len(informe['no_declaradas'])} no declaradas")
    return df


def perfilar(df: pd.DataFrame) -> pd.DataFrame:
    """Devuelve una fila por columna con su tipo, únicos y porcentaje de nulos."""
    return pd.DataFrame({
        "columna": df.columns,
        "tipo": [str(t) for t in df.dtypes],
        "unicos": [df[c].nunique(dropna=True) for c in df.columns],
        "nulos": df.isna().sum().values,
        "pct_nulos": (df.isna().mean() * 100).round(2).values,
    }).sort_values("pct_nulos", ascending=False).reset_index(drop=True)
