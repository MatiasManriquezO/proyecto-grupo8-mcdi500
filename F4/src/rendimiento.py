"""
rendimiento.py — Mediciones formales de eficiencia con timeit.

La Fase 3 midió con time.perf_counter y tracemalloc (F3/src/medicion.py).
La Fase 4 agrega el instrumento formal que pide la rúbrica, timeit, y un
paso más de análisis: estimar el ORDEN EMPÍRICO de crecimiento de cada
implementación, en vez de solo comparar tiempos a un tamaño fijo.

Protocolo (se mantiene el de F3 y se formaliza):
  1. Verificar que todas las implementaciones den el mismo resultado.
  2. timeit.Timer.autorange() elige cuántas ejecuciones caben en ~0,2 s;
     repeat() repite esa medición y se conserva el MÍNIMO por ejecución
     (el ruido del sistema solo puede sumar tiempo, nunca restarlo).
  3. Medir a varios tamaños n y ajustar log(t) = a + b·log(n): la pendiente
     b es el orden empírico (b ≈ 1 lineal; b ≈ 0 constante o logarítmico).

Grupo 8 · MCDI500 · Universidad Andrés Bello
"""

from __future__ import annotations

import timeit
import tracemalloc

import numpy as np
import pandas as pd


def _iguales(a, b) -> bool:
    """Compara resultados de distinto tipo (escalar, arreglo, dict, DataFrame)."""
    if isinstance(a, pd.DataFrame):
        try:
            pd.testing.assert_frame_equal(a, b, check_dtype=False)
            return True
        except AssertionError:
            return False
    if isinstance(a, (float, np.floating, np.ndarray)):
        return bool(np.allclose(a, b, rtol=1e-9, atol=1e-12))
    return a == b


def medir_timeit(implementaciones: dict, *args, repeticiones: int = 5, **kwargs) -> pd.DataFrame:
    """Mide cada implementación con timeit y memoria pico con tracemalloc.

    Parámetros
    ----------
    implementaciones : dict {nombre: función}; todas reciben *args, **kwargs.
    repeticiones     : cuántas veces se repite la medición (mínimo 3).

    Retorna un DataFrame con: ejecuciones por repetición, tiempo mínimo y
    mediano por ejecución (ms), memoria pico (KiB) y razón frente a la más
    rápida. Lanza ValueError si los resultados no coinciden.
    """
    if not implementaciones:
        raise ValueError("No se entregó ninguna implementación.")
    if repeticiones < 3:
        raise ValueError("Use al menos 3 repeticiones para descartar ruido.")

    nombres = list(implementaciones)
    referencia = implementaciones[nombres[0]](*args, **kwargs)
    for nombre in nombres[1:]:
        if not _iguales(referencia, implementaciones[nombre](*args, **kwargs)):
            raise ValueError(f"'{nombre}' no coincide con '{nombres[0]}': no es una optimización.")

    filas = []
    for nombre, funcion in implementaciones.items():
        temporizador = timeit.Timer(lambda f=funcion: f(*args, **kwargs))
        ejecuciones, _ = temporizador.autorange()               # ≥ 0,2 s por repetición
        tiempos = np.array(temporizador.repeat(repeat=repeticiones, number=ejecuciones))
        por_ejecucion = tiempos / ejecuciones * 1000
        tracemalloc.start()
        funcion(*args, **kwargs)
        _, pico = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        filas.append({"implementacion": nombre, "ejecuciones": ejecuciones,
                      "repeticiones": repeticiones,
                      "tiempo_min_ms": por_ejecucion.min(),
                      "tiempo_mediana_ms": float(np.median(por_ejecucion)),
                      "memoria_pico_kib": pico / 1024})
    tabla = pd.DataFrame(filas).sort_values("tiempo_min_ms").reset_index(drop=True)
    tabla["veces_mas_lenta"] = tabla["tiempo_min_ms"] / tabla["tiempo_min_ms"].iloc[0]
    return tabla.round({"tiempo_min_ms": 4, "tiempo_mediana_ms": 4,
                        "memoria_pico_kib": 1, "veces_mas_lenta": 1})


def curva_crecimiento(implementaciones: dict, generar_entrada, tamanos,
                      repeticiones: int = 5) -> pd.DataFrame:
    """Mide todas las implementaciones a varios tamaños.

    generar_entrada(n) debe devolver la tupla de argumentos para ese tamaño.
    Retorna formato largo: n, implementacion, tiempo_min_ms.
    """
    filas = []
    for n in tamanos:
        argumentos = generar_entrada(n)
        tabla = medir_timeit(implementaciones, *argumentos, repeticiones=repeticiones)
        for fila in tabla.itertuples():
            filas.append({"n": n, "implementacion": fila.implementacion,
                          "tiempo_min_ms": fila.tiempo_min_ms})
    return pd.DataFrame(filas)


def orden_empirico(curva: pd.DataFrame, ultimos: int = 3) -> pd.DataFrame:
    """Pendiente de log(tiempo) contra log(n) por implementación.

    Es la versión medida de la notación O: si el tiempo se duplica al
    duplicar n, la pendiente es 1 (lineal). Se informan dos pendientes:
    con todos los tamaños y solo con los `ultimos` más grandes. En las
    versiones vectorizadas, a n pequeño domina el costo fijo de cada
    llamada y la pendiente sale menor que 1; la pendiente asintótica
    (tamaños grandes) es la que se compara con la notación O.
    """
    filas = []
    for nombre, grupo in curva.groupby("implementacion", sort=False):
        if grupo["n"].nunique() < 2:
            raise ValueError("Se necesitan al menos dos tamaños para estimar el orden.")
        grupo = grupo.sort_values("n")
        x, y = np.log(grupo["n"]), np.log(grupo["tiempo_min_ms"])
        total, _ = np.polyfit(x, y, 1)
        cola, _ = np.polyfit(x[-ultimos:], y[-ultimos:], 1) if len(grupo) >= max(ultimos, 2) \
            else (total, None)
        filas.append({"implementacion": nombre, "pendiente_loglog": round(total, 2),
                      "pendiente_asintotica": round(cola, 2)})
    return pd.DataFrame(filas)


def punto_de_cruce(curva: pd.DataFrame, rapida_en_grande: str, rapida_en_pequeno: str):
    """Tamaño n desde el cual `rapida_en_grande` supera a `rapida_en_pequeno`.

    Las versiones vectorizadas tienen un costo fijo de preparación: con pocos
    datos pueden ser más lentas que un bucle. Se busca el primer par de
    tamaños consecutivos donde la razón de tiempos cambia de signo y se
    interpola en escala log-log. Retorna None si no hay cruce en el rango
    medido (una de las dos gana en todos los tamaños).
    """
    tabla = curva.pivot_table(index="n", columns="implementacion", values="tiempo_min_ms")
    for nombre in (rapida_en_grande, rapida_en_pequeno):
        if nombre not in tabla.columns:
            raise KeyError(f"'{nombre}' no está en la curva.")
    razon = np.log(tabla[rapida_en_grande] / tabla[rapida_en_pequeno])   # < 0: gana la primera
    ns = razon.index.to_numpy(dtype=float)
    valores = razon.to_numpy()
    for i in range(len(ns) - 1):
        if valores[i] >= 0 > valores[i + 1] or valores[i] > 0 >= valores[i + 1]:
            fraccion = valores[i] / (valores[i] - valores[i + 1])
            return float(np.exp(np.log(ns[i]) + fraccion * (np.log(ns[i + 1]) - np.log(ns[i]))))
    return None
