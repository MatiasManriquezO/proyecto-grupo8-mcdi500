"""
pipeline.py — Orquestación del núcleo algorítmico.

Contiene lo que encadena los pasos, no los pasos mismos ni quién los arma:
  Pipeline            ejecuta una lista de Transformadores en orden.
  PipelineObservable  además notifica cada paso a sus observadores (Observer).

Los observadores (Bitacora, ReporteConsola) están en observadores.py y la
fábrica que arma el pipeline del proyecto, en fabrica.py: este módulo solo
cambia si cambia la forma de encadenar los pasos.

Grupo 8 · MCDI500 · Universidad Andrés Bello
"""

from __future__ import annotations

import time

import pandas as pd

try:                                    # importado como paquete (F3.src)
    from .transformadores import Transformador
except ImportError:                     # importado con F3/src en sys.path
    from transformadores import Transformador


# ══════════════════════════════════════════════════════════════
# ORQUESTADORES
# ══════════════════════════════════════════════════════════════

class Pipeline:
    """Encadena transformadores y los ejecuta en orden."""

    def __init__(self, pasos=None):
        self._pasos = []
        self._ajustado = False
        for paso in pasos or []:
            self.agregar(paso)

    def agregar(self, transformador: Transformador) -> "Pipeline":
        """Agrega un paso al final; solo acepta objetos Transformador."""
        if not isinstance(transformador, Transformador):
            raise TypeError(
                f"Se esperaba un Transformador y se recibió {type(transformador).__name__}."
            )
        self._pasos.append(transformador)
        self._ajustado = False          # un paso nuevo obliga a volver a ajustar
        return self

    def ajustar(self, df: pd.DataFrame) -> "Pipeline":
        """Aprende los parámetros de cada paso SOLO con estos datos."""
        intermedio = df.copy()
        for paso in self._pasos:
            intermedio = paso.ajustar_transformar(intermedio)
        self._ajustado = True
        return self

    def transformar(self, df: pd.DataFrame) -> pd.DataFrame:
        """Aplica los pasos en orden sobre una copia de df."""
        if not self._ajustado:
            raise RuntimeError("Pipeline: hay que ajustar antes de transformar.")
        resultado = df.copy()
        for paso in self._pasos:
            resultado = self._ejecutar_paso(paso, resultado)
        return resultado

    def _ejecutar_paso(self, paso, df):
        """Punto de extensión: las subclases pueden envolver cada paso."""
        return paso.transformar(df)

    def pasos_ejecutados(self) -> tuple:
        """Devuelve los pasos (tupla inmutable) para registrar sus parámetros."""
        return tuple(self._pasos)

    def resumen(self) -> pd.DataFrame:
        """Tabla con el orden, el nombre y la clase de cada paso."""
        return pd.DataFrame([
            {"orden": i, "paso": p.nombre, "clase": type(p).__name__}
            for i, p in enumerate(self._pasos, start=1)
        ])

    def __len__(self):
        return len(self._pasos)

    def __repr__(self):
        estado = "ajustado" if self._ajustado else "sin ajustar"
        return f"{type(self).__name__}({len(self._pasos)} pasos, {estado})"


class PipelineObservable(Pipeline):
    """Pipeline que además notifica cada paso a sus observadores (Observer)."""

    def __init__(self, pasos=None):
        super().__init__(pasos)
        self._observadores = []

    def suscribir(self, observador) -> "PipelineObservable":
        """Registra un objeto con método notificar(paso, filas, columnas, segundos, parametros)."""
        if not callable(getattr(observador, "notificar", None)):
            raise TypeError("El observador debe tener un método notificar().")
        self._observadores.append(observador)
        return self

    def _ejecutar_paso(self, paso, df):
        # Redefine solo el punto de extensión: el recorrido lo hereda de Pipeline
        inicio = time.perf_counter()
        resultado = paso.transformar(df)
        transcurrido = time.perf_counter() - inicio
        for observador in self._observadores:
            observador.notificar(paso.nombre, len(resultado), resultado.shape[1],
                                 transcurrido, paso.parametros)
        return resultado
