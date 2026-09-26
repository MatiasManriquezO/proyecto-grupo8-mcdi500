"""
busqueda.py — Recuperación de registros por identificador.

Compara tres estrategias para recuperar un registro concreto del
conjunto a partir de su id_registro, operación necesaria para auditar
casos individuales. Las tres devuelven la misma posición; lo que cambia
es el costo.

Grupo 8 · MCDI500 · Universidad Andrés Bello
"""

from __future__ import annotations

import numpy as np


def buscar_lineal(ids: np.ndarray, objetivo: int) -> int:
    """Recorre el arreglo desde el inicio hasta encontrar el objetivo.

    No exige ningún orden previo, pero en el peor caso mira todos los
    elementos. Es la línea base de la comparación.

    Complejidad: O(n) en tiempo, O(1) en espacio.

    Retorna la posición, o -1 si el identificador no existe.
    """
    for posicion, valor in enumerate(ids):
        if valor == objetivo:
            return posicion
    return -1


def buscar_binaria_rec(
    ids: np.ndarray,
    objetivo: int,
    inicio: int = 0,
    fin: int | None = None,
) -> int:
    """Búsqueda binaria recursiva sobre un arreglo ordenado.

    Es el caso de recursión legítimo del proyecto: en cada llamada
    descarta la mitad del espacio de búsqueda, de modo que la
    profundidad es log2(n) —quince niveles para nuestras 20.103 filas—
    y nunca se acerca al límite de la pila de Python.

    Caso base    : el intervalo queda vacío (inicio > fin).
    Caso recursivo: se repite sobre la mitad que puede contener el valor.

    Requiere que ids esté ordenado de forma creciente.

    Complejidad: O(log n) en tiempo, O(log n) en espacio por la pila.
    """
    if fin is None:
        fin = len(ids) - 1

    if inicio > fin:
        return -1

    medio = (inicio + fin) // 2
    if ids[medio] == objetivo:
        return medio
    if ids[medio] < objetivo:
        return buscar_binaria_rec(ids, objetivo, medio + 1, fin)
    return buscar_binaria_rec(ids, objetivo, inicio, medio - 1)


def construir_indice(ids: np.ndarray) -> dict:
    """Construye un diccionario {identificador: posición}.

    Cambia tiempo por espacio: la construcción cuesta una pasada
    completa, pero después cada consulta es prácticamente instantánea.
    Conviene cuando se harán muchas búsquedas sobre el mismo conjunto.

    Complejidad: O(n) al construir, O(1) por consulta, O(n) en espacio.
    """
    return {int(valor): posicion for posicion, valor in enumerate(ids)}


def buscar_en_indice(indice: dict, objetivo: int) -> int:
    """Consulta el diccionario construido por construir_indice."""
    return indice.get(int(objetivo), -1)
