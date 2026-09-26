"""
analisis.py — Componente con estado del análisis de contingencia.

Contiene la única clase de esta entrega. La guía de la Formativa 3 es
explícita al respecto: una clase se justifica cuando el componente
necesita recordar algo entre una llamada y otra; si cada llamada es
independiente, una función es más simple.

AnalisisContingencia recuerda tres cosas que de otro modo habría que
recalcular o arrastrar en variables sueltas: el conjunto cargado, la
tabla de conteos y el método con el que se obtuvo. Eso permite pedir
la proporción, las marginales o el total sin volver a contar.

Grupo 8 · MCDI500 · Universidad Andrés Bello
"""

from __future__ import annotations

import pandas as pd

from contingencia import (
    contar_bincount,
    contar_crosstab,
    contar_iterrows,
    contar_zip,
    preparar_pares,
    proporcion_por_fila,
)

# Las cuatro implementaciones disponibles, por nombre.
METODOS = {
    "iterrows": contar_iterrows,
    "zip": contar_zip,
    "crosstab": contar_crosstab,
    "bincount": contar_bincount,
}


class AnalisisContingencia:
    """Encapsula el cruce de dos variables ordinales del conjunto.

    El estado interno se marca con guion bajo: son atributos que la
    clase administra y que no deben modificarse desde fuera, porque la
    coherencia entre la tabla y los datos que la produjeron depende de
    que se actualicen juntos.

    Ejemplo de uso
    --------------
    >>> analisis = AnalisisContingencia(df, "redes_sociales_cod",
    ...                                 "salud_mental_cod")
    >>> analisis.calcular(metodo="bincount")
    >>> analisis.proporcion([4, 5])
    """

    def __init__(self, df: pd.DataFrame, x: str, y: str) -> None:
        """Prepara los pares válidos y deja la tabla sin calcular.

        Se guarda una copia del DataFrame para no modificar el original
        de quien llama.
        """
        self.x = x
        self.y = y
        self._pares = preparar_pares(df.copy(), x, y)
        self._tabla: dict | None = None
        self._metodo: str | None = None

    @property
    def n_pares(self) -> int:
        """Cantidad de pares completos que entraron al conteo."""
        return len(self._pares)

    @property
    def calculado(self) -> bool:
        """Indica si la tabla ya se calculó."""
        return self._tabla is not None

    def calcular(self, metodo: str = "bincount") -> dict:
        """Cuenta los pares con la implementación indicada.

        Lanza ValueError si el método no existe.
        """
        if metodo not in METODOS:
            raise ValueError(
                f"Método desconocido: '{metodo}'. "
                f"Disponibles: {', '.join(METODOS)}"
            )

        self._tabla = METODOS[metodo](self._pares, self.x, self.y)
        self._metodo = metodo
        return self._tabla

    def tabla(self) -> dict:
        """Devuelve la tabla de conteos ya calculada.

        Lanza RuntimeError si se pide antes de calcular. Esa comprobación
        es la razón de encapsular: detecta el error donde se origina y no
        veinte celdas después.
        """
        self._exigir_calculo()
        return self._tabla

    def proporcion(self, codigos_positivos: list[int]) -> pd.DataFrame:
        """Porcentaje del desenlace de interés por cada nivel de x."""
        self._exigir_calculo()
        return proporcion_por_fila(self._tabla, codigos_positivos)

    def marginales(self) -> tuple[pd.Series, pd.Series]:
        """Totales por nivel de x y por nivel de y.

        Sirven para verificar el conteo por un camino independiente:
        deben coincidir con value_counts de pandas.
        """
        self._exigir_calculo()
        marg_x, marg_y = {}, {}
        for (a, b), n in self._tabla.items():
            marg_x[a] = marg_x.get(a, 0) + n
            marg_y[b] = marg_y.get(b, 0) + n
        return (
            pd.Series(marg_x).sort_index(),
            pd.Series(marg_y).sort_index(),
        )

    def resumen(self) -> dict:
        """Trazabilidad del análisis: qué se cruzó, con qué y con cuántos."""
        return {
            "variables": f"{self.x} × {self.y}",
            "pares_validos": self.n_pares,
            "metodo": self._metodo,
            "celdas": len(self._tabla) if self._tabla else 0,
        }

    def _exigir_calculo(self) -> None:
        """Comprobación interna: la tabla debe existir."""
        if self._tabla is None:
            raise RuntimeError(
                "La tabla aún no se calcula. Llame a calcular() primero."
            )

    def __repr__(self) -> str:
        estado = self._metodo if self._metodo else "sin calcular"
        return (
            f"AnalisisContingencia({self.x} × {self.y}, "
            f"n={self.n_pares}, {estado})"
        )
