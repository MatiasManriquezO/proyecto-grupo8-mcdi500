"""
contingencia.py — Núcleo algorítmico de la Fase 3.

Construye la tabla de contingencia entre la frecuencia de uso de redes
sociales (q80) y el estado de salud mental autopercibido (q84) del
conjunto YRBS 2023 ya procesado en la Fase 2.

Se implementan cuatro versiones del mismo conteo, todas O(n) en teoría,
para medir la constante por fila —que es donde está la diferencia
práctica— y adoptar la más eficiente.

Grupo 8 · MCDI500 · Universidad Andrés Bello
"""

from __future__ import annotations

import numpy as np
import pandas as pd

# Códigos válidos según el codebook del YRBS 2023 (CDC, 2024).
# q80: 1 = no usa redes ... 8 = seis o más horas al día
# q84: 1 = Never ... 5 = Always
MAX_X = 8
MAX_Y = 5


def preparar_pares(df: pd.DataFrame, x: str, y: str) -> pd.DataFrame:
    """Descarta los pares incompletos y ajusta el tipo a int16.

    Un par incompleto no pertenece a ninguna celda de la tabla, de modo
    que no se imputa: los faltantes de estas variables no son aleatorios
    (véase bitácora de decisiones, F2). Los códigos se usan como índices
    de conteo, así que int16 basta y reduce la memoria.

    Parámetros
    ----------
    df : DataFrame del conjunto procesado en la Fase 2.
    x, y : nombres de las dos columnas a cruzar.

    Retorna
    -------
    DataFrame con dos columnas int16 y sin valores ausentes.

    Lanza
    -----
    KeyError : si alguna de las columnas no existe en el DataFrame.
    """
    faltantes = [c for c in (x, y) if c not in df.columns]
    if faltantes:
        raise KeyError(f"Columnas ausentes en el conjunto: {faltantes}")

    pares = df[[x, y]].dropna()
    return pares.astype("int16")


def contar_iterrows(pares: pd.DataFrame, x: str, y: str) -> dict:
    """Implementación A: recorre fila por fila con iterrows.

    Es la versión más directa de leer y la más lenta: iterrows construye
    una Serie de pandas por cada fila. Se incluye como línea base de la
    comparación, no como opción a adoptar.

    Complejidad: O(n) en tiempo, con una constante por fila muy alta.
    """
    tabla: dict[tuple[int, int], int] = {}
    for _, fila in pares.iterrows():
        clave = (int(fila[x]), int(fila[y]))
        tabla[clave] = tabla.get(clave, 0) + 1
    return tabla


def contar_zip(pares: pd.DataFrame, x: str, y: str) -> dict:
    """Implementación B: recorre con zip sobre los arreglos de NumPy.

    Mismo algoritmo que A, pero sin construir un objeto de pandas por
    fila. El cambio es de una línea y el efecto se mide en dos órdenes
    de magnitud.

    Complejidad: O(n) en tiempo, constante por fila baja.
    """
    tabla: dict[tuple[int, int], int] = {}
    for a, b in zip(pares[x].to_numpy(), pares[y].to_numpy()):
        clave = (int(a), int(b))
        tabla[clave] = tabla.get(clave, 0) + 1
    return tabla


def contar_crosstab(pares: pd.DataFrame, x: str, y: str) -> dict:
    """Implementación C: delega en pd.crosstab.

    Es la opción idiomática de pandas y la que se propuso en el foro
    técnico como alternativa eficiente. La medición mostró que no lo es
    para este caso: crosstab es general y paga el costo de construir un
    DataFrame intermedio con índices.

    Complejidad: O(n) en tiempo, con sobrecarga de construcción.
    """
    cruce = pd.crosstab(pares[x], pares[y])
    return {
        (int(i), int(j)): int(cruce.loc[i, j])
        for i in cruce.index
        for j in cruce.columns
        if cruce.loc[i, j] > 0
    }


def contar_bincount(
    pares: pd.DataFrame,
    x: str,
    y: str,
    max_x: int = MAX_X,
    max_y: int = MAX_Y,
) -> dict:
    """Implementación D: codifica el par en un entero y usa np.bincount.

    Cada par (a, b) se convierte en un único índice lineal
    (a - 1) * max_y + (b - 1), y np.bincount cuenta todas las
    ocurrencias en una sola pasada de código compilado.

    Es la versión adoptada: mismo resultado, sin bucle en Python.

    Complejidad: O(n) en tiempo, O(max_x * max_y) en espacio.
    """
    a = pares[x].to_numpy(dtype=np.int64)
    b = pares[y].to_numpy(dtype=np.int64)

    indices = (a - 1) * max_y + (b - 1)
    conteos = np.bincount(indices, minlength=max_x * max_y)

    tabla = {}
    for pos, n in enumerate(conteos):
        if n:
            tabla[(pos // max_y + 1, pos % max_y + 1)] = int(n)
    return tabla


def proporcion_por_fila(tabla: dict, codigos_positivos: list[int]) -> pd.DataFrame:
    """Deriva el indicador de interés por cada nivel de la variable x.

    Para cada nivel de uso de redes sociales, calcula qué porcentaje de
    las respuestas cae en los códigos considerados positivos —en este
    proyecto, salud mental no buena la mayor parte del tiempo o siempre
    (códigos 4 y 5 de q84).

    Parámetros
    ----------
    tabla : diccionario {(x, y): n} devuelto por cualquier contar_*.
    codigos_positivos : códigos de y que cuentan como desenlace positivo.

    Retorna
    -------
    DataFrame con columnas: nivel_x, n, positivos, porcentaje.

    Lanza
    -----
    ValueError : si no se entrega ningún código positivo.
    """
    if not codigos_positivos:
        raise ValueError("Debe indicarse al menos un código positivo.")

    niveles = sorted({clave[0] for clave in tabla})
    filas = []
    for nivel in niveles:
        total = sum(n for (a, _), n in tabla.items() if a == nivel)
        positivos = sum(
            n for (a, b), n in tabla.items()
            if a == nivel and b in codigos_positivos
        )
        filas.append({
            "nivel_x": nivel,
            "n": total,
            "positivos": positivos,
            "porcentaje": round(100 * positivos / total, 1) if total else 0.0,
        })
    return pd.DataFrame(filas)
