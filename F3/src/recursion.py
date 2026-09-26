"""
recursion.py — Casos recursivos evaluados y su alternativa iterativa.

Este módulo agrupa las decisiones del proyecto sobre recursividad. No
todos los casos se adoptaron: dos se descartaron con evidencia y esa
decisión, documentada, vale tanto como implementarla.

Grupo 8 · MCDI500 · Universidad Andrés Bello
"""

from __future__ import annotations

import numpy as np


def aplanar(estructura: dict, prefijo: str = "") -> dict:
    """Convierte un diccionario anidado en pares clave-valor planos.

    Es el caso recursivo legítimo del proyecto: la profundidad de los
    metadatos no se conoce al escribir el código, de modo que un bucle
    exigiría saber de antemano cuántos niveles anidar.

    Caso base    : el valor no es un diccionario, se guarda.
    Caso recursivo: el valor es un diccionario, se desciende un nivel.

    Complejidad: O(k) sobre el número total de hojas.
    """
    plano = {}
    for clave, valor in estructura.items():
        compuesta = f"{prefijo}.{clave}" if prefijo else str(clave)
        if isinstance(valor, dict) and valor:
            plano.update(aplanar(valor, compuesta))
        else:
            plano[compuesta] = valor
    return plano


def contar_recursivo_lineal(valores: np.ndarray, posicion: int = 0) -> int:
    """Cuenta respuestas válidas con una llamada por fila.

    DESCARTADA. Se incluye porque la evidencia de su fallo es el
    argumento del informe: la profundidad crece con n, de modo que
    supera el límite de la pila de Python (cercano a mil llamadas)
    antes de recorrer el 5 % del conjunto.

    Lanza RecursionError sobre aproximadamente mil filas.
    """
    if posicion >= len(valores):
        return 0
    actual = 1 if not np.isnan(valores[posicion]) else 0
    return actual + contar_recursivo_lineal(valores, posicion + 1)


def contar_dyv(valores: np.ndarray, inicio: int = 0, fin: int | None = None) -> int:
    """Cuenta respuestas válidas con divide y vencerás.

    DESCARTADA para producción. Funciona —la profundidad es log2(n),
    quince niveles— pero realiza el mismo trabajo total que el bucle
    más el costo de administrar la pila de llamadas. La medición lo
    confirma: es varias veces más lenta que la versión iterativa.

    Se conserva para documentar que recursión y eficiencia no son lo
    mismo.

    Complejidad: O(n) en tiempo, O(log n) en espacio.
    """
    if fin is None:
        fin = len(valores)

    if fin - inicio <= 0:
        return 0
    if fin - inicio == 1:
        return 0 if np.isnan(valores[inicio]) else 1

    medio = (inicio + fin) // 2
    return contar_dyv(valores, inicio, medio) + contar_dyv(valores, medio, fin)


def contar_iterativo(valores: np.ndarray) -> int:
    """Cuenta respuestas válidas con un recorrido secuencial.

    ADOPTADA. El recorrido es de profundidad fija y conocida, que es
    justamente el criterio para preferir iteración sobre recursión.

    Complejidad: O(n) en tiempo, O(1) en espacio.
    """
    total = 0
    for valor in valores:
        if not np.isnan(valor):
            total += 1
    return total
