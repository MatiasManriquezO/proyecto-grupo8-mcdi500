"""
observadores.py — Observadores del pipeline (patrón Observer).

PipelineObservable (pipeline.py) avisa al terminar cada paso; los objetos de
este módulo deciden qué hacer con el aviso. El pipeline no sabe quién anota:
basta con que el observador tenga un método notificar().

  Bitacora        acumula lo ocurrido en cada paso y lo entrega como tabla.
  ReporteConsola  imprime cada paso mientras ocurre.

Ubicación proyectada en la Tabla 8 de la Formativa 3 (capa «Soporte»).

Grupo 8 · MCDI500 · Universidad Andrés Bello
"""

from __future__ import annotations

import pandas as pd


class Bitacora:
    """Observador que acumula lo ocurrido en cada paso y lo entrega como tabla."""

    def __init__(self):
        self.registros = []

    def notificar(self, paso, filas, columnas, segundos, parametros):
        """Recibe el aviso de un paso terminado y lo guarda."""
        self.registros.append({"paso": paso, "filas": filas, "columnas": columnas,
                               "segundos": round(segundos, 5), "parametros": parametros})

    def a_dataframe(self) -> pd.DataFrame:
        """Devuelve lo registrado como DataFrame, un paso por fila."""
        return pd.DataFrame(self.registros)


class ReporteConsola:
    """Observador que imprime cada paso mientras ocurre."""

    def notificar(self, paso, filas, columnas, segundos, parametros):
        """Imprime una línea por paso: filas, columnas y tiempo."""
        print(f"  {paso:<44} {filas:>6} filas, {columnas:>3} col  [{segundos:.4f}s]")
