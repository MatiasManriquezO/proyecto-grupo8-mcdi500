"""
segmentacion.py — Prevalencia de salud mental no buena por segmentos anidados.

Problema del proyecto: describir cómo cambia el porcentaje de estudiantes con
salud mental no buena (q84 = 4-5) al descender por una jerarquía de variables,
por ejemplo frecuencia de uso de redes -> sexo -> edad. Cada segmento solo se
subdivide si tiene al menos `n_minimo` estudiantes; por debajo de ese tamaño
un porcentaje no es interpretable. Por esa poda, la profundidad de cada rama
depende de los datos y no se conoce al escribir el código: es el criterio del
proyecto para usar recursión (bitácora F3.5).

El subconjunto de un segmento se define recursivamente: es el subconjunto de
su segmento padre filtrado por un valor más. Resolverlo sin memoria repite el
trabajo de todos los ancestros en cada nodo (el mismo defecto que Fibonacci
ingenuo); con memoización cada segmento se calcula una sola vez.

Tres implementaciones del mismo resultado:
  ArbolPrevalencia(memoizar=False)  recursiva ingenua      O(nodos · n)
  ArbolPrevalencia(memoizar=True)   recursiva memoizada    O(profundidad · n)
  tabla_por_niveles_groupby         vectorizada por nivel  O(profundidad · n)

Muestral, sin ponderar (bitácora 2.6).

Grupo 8 · MCDI500 · Universidad Andrés Bello
"""

from __future__ import annotations

from functools import lru_cache

import numpy as np
import pandas as pd


class ArbolPrevalencia:
    """Recorre recursivamente una jerarquía de segmentos y calcula su prevalencia.

    Recuerda entre llamadas los subconjuntos ya calculados (si memoizar=True),
    por eso es una clase y no una función.
    """

    def __init__(self, df: pd.DataFrame, jerarquia, desenlace: str,
                 n_minimo: int = 30, memoizar: bool = True):
        faltan = [c for c in [*jerarquia, desenlace] if c not in df.columns]
        if faltan:
            raise KeyError(f"ArbolPrevalencia: no existen las columnas {faltan}.")
        if n_minimo < 1:
            raise ValueError("n_minimo debe ser al menos 1.")
        self.jerarquia = list(jerarquia)
        self.desenlace = desenlace
        self.n_minimo = int(n_minimo)
        self.memoizar = memoizar

        # Solo estudiantes con el desenlace respondido (no se imputa, bitácora 2.5)
        base = df[df[desenlace].notna()]
        self._y = base[desenlace].astype("float64").to_numpy()
        # Arreglos NumPy por variable; los faltantes quedan como NaN y no
        # pertenecen a ningún segmento de esa variable
        self._x = {c: pd.to_numeric(base[c].astype("object"), errors="coerce")
                   .to_numpy(dtype="float64") for c in self.jerarquia}
        self._todos = np.arange(len(base))
        self.llamadas_filtro = 0          # trabajo realizado: filtros aplicados

        # Memoización: la misma función, envuelta con functools.lru_cache
        self._subconjunto = (lru_cache(maxsize=None)(self._subconjunto_sin_memoria)
                             if memoizar else self._subconjunto_sin_memoria)

    # ---- recursión 1: el subconjunto de un segmento ------------------------
    def _subconjunto_sin_memoria(self, filtros: tuple) -> np.ndarray:
        """Posiciones de los estudiantes del segmento definido por `filtros`.

        Caso base     : sin filtros, todos los estudiantes.
        Caso recursivo: el subconjunto del padre, filtrado por el último valor.
        """
        if not filtros:
            return self._todos
        padre = self._subconjunto(filtros[:-1])
        columna, valor = filtros[-1]
        self.llamadas_filtro += 1
        return padre[self._x[columna][padre] == valor]

    def estadisticas(self, filtros: tuple = ()) -> dict:
        """n, positivos y porcentaje del segmento."""
        posiciones = self._subconjunto(tuple(filtros))
        n = len(posiciones)
        positivos = int(self._y[posiciones].sum()) if n else 0
        return {"n": n, "positivos": positivos,
                "pct": round(100 * positivos / n, 1) if n else float("nan")}

    # ---- recursión 2: el recorrido del árbol ------------------------------
    def explorar(self, filtros: tuple = ()) -> list:
        """Devuelve una fila por segmento visitado, en profundidad.

        Caso base     : se agotó la jerarquía o el segmento es menor que n_minimo.
        Caso recursivo: se desciende por cada valor observado de la variable
                        siguiente.
        """
        nivel = len(filtros)
        fila = {"nivel": nivel, "segmento": filtros, **self.estadisticas(filtros)}
        filas = [fila]
        if nivel == len(self.jerarquia) or fila["n"] < self.n_minimo:
            return filas                                   # caso base
        columna = self.jerarquia[nivel]
        posiciones = self._subconjunto(filtros)
        valores = np.unique(self._x[columna][posiciones])
        for valor in valores[~np.isnan(valores)]:
            filas += self.explorar(filtros + ((columna, float(valor)),))
        return filas

    def tabla(self) -> pd.DataFrame:
        """El árbol completo como DataFrame ordenado por segmento."""
        return _ordenar(pd.DataFrame(self.explorar()))

    def info_cache(self):
        """Aciertos y fallos de la memoria (None si no se memoiza)."""
        return self._subconjunto.cache_info() if self.memoizar else None


def tabla_por_niveles_groupby(df: pd.DataFrame, jerarquia, desenlace: str,
                              n_minimo: int = 30) -> pd.DataFrame:
    """Mismo árbol con un groupby por nivel y la poda aplicada después.

    Un segmento se conserva si su padre existe y tiene al menos n_minimo
    estudiantes, que es la regla del recorrido recursivo.
    """
    base = df[df[desenlace].notna()].copy()
    base[desenlace] = base[desenlace].astype("float64")
    for c in jerarquia:
        base[c] = pd.to_numeric(base[c].astype("object"), errors="coerce")

    filas = [{"nivel": 0, "segmento": (), "n": len(base),
              "positivos": int(base[desenlace].sum())}]
    abiertos = {()} if len(base) >= n_minimo else set()   # segmentos que se subdividen
    for nivel in range(1, len(jerarquia) + 1):
        columnas = list(jerarquia[:nivel])
        grupos = (base.dropna(subset=columnas)
                  .groupby(columnas, observed=True)[desenlace].agg(["size", "sum"]))
        nuevos = set()
        for clave, (n, pos) in zip(grupos.index, grupos.to_numpy()):
            clave = clave if isinstance(clave, tuple) else (clave,)
            segmento = tuple(zip(columnas, (float(v) for v in clave)))
            if segmento[:-1] not in abiertos:
                continue                                     # padre podado
            filas.append({"nivel": nivel, "segmento": segmento,
                          "n": int(n), "positivos": int(pos)})
            if n >= n_minimo:
                nuevos.add(segmento)
        abiertos = nuevos
    tabla = pd.DataFrame(filas)
    tabla["pct"] = (100 * tabla["positivos"] / tabla["n"]).round(1)
    return _ordenar(tabla[["nivel", "segmento", "n", "positivos", "pct"]])


def _ordenar(tabla: pd.DataFrame) -> pd.DataFrame:
    """Orden canónico para poder comparar implementaciones fila a fila."""
    # Las tuplas se comparan elemento a elemento: el padre queda antes que sus hijos
    orden = sorted(range(len(tabla)), key=lambda i: tabla["segmento"].iloc[i])
    return tabla.iloc[orden].reset_index(drop=True)
