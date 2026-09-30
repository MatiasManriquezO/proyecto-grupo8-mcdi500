"""
medicion.py — Instrumentos de medición de tiempo y memoria.

El módulo es independiente de qué se mide: recibe cualquier función y
sus argumentos. Esa separación es deliberada, porque las mismas
utilidades se reutilizan en la Fase 4.

Protocolo seguido, según el material de la Semana 2:
  1. Repetir cada medición y conservar el tiempo MÍNIMO, no el promedio.
     Los tiempos altos suelen deberse a que el equipo estaba haciendo
     otra cosa, no al código.
  2. Medir sobre el tamaño real del conjunto.
  3. Comprobar que las versiones comparadas entregan el mismo resultado.

Grupo 8 · MCDI500 · Universidad Andrés Bello
"""

from __future__ import annotations

import time
import tracemalloc

import pandas as pd


def medir_tiempo(funcion, *args, repeticiones: int = 7, **kwargs) -> float:
    """Ejecuta la función varias veces y devuelve el tiempo mínimo en ms.

    Se usa time.perf_counter, que entrega el reloj de mayor resolución
    disponible y no se ve afectado por ajustes de la hora del sistema.

    Lanza ValueError si repeticiones es menor que uno.
    """
    if repeticiones < 1:
        raise ValueError("Se requiere al menos una repetición.")

    tiempos = []
    for _ in range(repeticiones):
        inicio = time.perf_counter()
        funcion(*args, **kwargs)
        tiempos.append((time.perf_counter() - inicio) * 1000)
    return min(tiempos)


def medir_memoria(funcion, *args, **kwargs) -> float:
    """Devuelve la memoria pico en KiB durante una ejecución.

    tracemalloc rastrea las asignaciones del intérprete de Python. No
    contabiliza la memoria reservada por bibliotecas compiladas fuera
    del asignador de Python, de modo que es una cota inferior.
    """
    tracemalloc.start()
    funcion(*args, **kwargs)
    _, pico = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    return pico / 1024


def comparar(implementaciones: dict, *args, repeticiones: int = 7, **kwargs):
    """Mide varias implementaciones del mismo cálculo y las compara.

    Antes de medir verifica que todas devuelvan un resultado idéntico:
    una versión más rápida que entrega otra respuesta no es una
    optimización, es un error.

    Parámetros
    ----------
    implementaciones : dict {nombre: función}.

    Retorna
    -------
    DataFrame ordenado por tiempo, con la razón respecto de la más rápida.

    Lanza
    -----
    ValueError : si las implementaciones no coinciden en su resultado.
    """
    if not implementaciones:
        raise ValueError("No se entregó ninguna implementación.")

    nombres = list(implementaciones)
    referencia = implementaciones[nombres[0]](*args, **kwargs)
    for nombre in nombres[1:]:
        if implementaciones[nombre](*args, **kwargs) != referencia:
            raise ValueError(
                f"'{nombre}' no devuelve el mismo resultado que "
                f"'{nombres[0]}'. No es una optimización."
            )

    filas = []
    for nombre, funcion in implementaciones.items():
        filas.append({
            "implementacion": nombre,
            "tiempo_min_ms": round(
                medir_tiempo(funcion, *args, repeticiones=repeticiones, **kwargs), 3
            ),
            "memoria_pico_kib": round(medir_memoria(funcion, *args, **kwargs), 1),
        })

    tabla = pd.DataFrame(filas).sort_values("tiempo_min_ms").reset_index(drop=True)
    mas_rapida = tabla["tiempo_min_ms"].iloc[0]
    tabla["veces_mas_lenta"] = (tabla["tiempo_min_ms"] / mas_rapida).round(1)
    return tabla


# --- Medicion conjunta usada por el cuaderno de la Sumativa 2 ---
def medir(funcion, *args, **kwargs):
    """Ejecuta la función y devuelve resultado, segundos y memoria pico en MB.

    *args recoge los argumentos posicionales en una tupla y **kwargs los
    argumentos con nombre en un diccionario. El asterisco es lo que hace el
    trabajo; los nombres args y kwargs son solo convención.
    """
    tracemalloc.start()
    inicio = time.perf_counter()
    resultado = funcion(*args, **kwargs)
    transcurrido = time.perf_counter() - inicio
    _, pico = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    return resultado, transcurrido, pico / 1024 / 1024
