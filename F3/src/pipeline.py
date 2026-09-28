"""
pipeline.py — Orquestación del núcleo algorítmico.

Contiene lo que encadena los pasos, no los pasos mismos:
  Pipeline            ejecuta una lista de Transformadores en orden.
  PipelineObservable  además notifica cada paso a sus observadores (Observer).
  Bitacora            observador que acumula lo ocurrido como tabla.
  ReporteConsola      observador que imprime mientras ocurre.
  construir_pipeline_proyecto
                      fábrica (Factory) que arma los 12 pasos de la Fase 2
                      desde las constantes de src/procesamiento.py.

Las constantes de columnas y escalas NO se copian: se importan del módulo de
la Fase 2 (src/procesamiento.py, en la raíz del repositorio), que sigue
siendo la fuente única de verdad del proyecto.

Grupo 8 · MCDI500 · Universidad Andrés Bello
"""

from __future__ import annotations

import sys
import time
from pathlib import Path

import pandas as pd

try:
    from .transformadores import (Transformador, EliminadorColumnaVacia,
                                  SeleccionadorColumnas, MarcadorFaltantes,
                                  TratamientoFaltantes, CastearCodigos,
                                  ConversorOrdinal, CodificadorOneHot,
                                  IndicadorBinario)
except ImportError:
    from transformadores import (Transformador, EliminadorColumnaVacia,
                                 SeleccionadorColumnas, MarcadorFaltantes,
                                 TratamientoFaltantes, CastearCodigos,
                                 ConversorOrdinal, CodificadorOneHot,
                                 IndicadorBinario)

# Módulo de la Fase 2: <raíz>/src/procesamiento.py (dos niveles sobre F3/src)
_SRC_F2 = Path(__file__).resolve().parents[2] / "src"
if str(_SRC_F2) not in sys.path:
    sys.path.insert(0, str(_SRC_F2))
import procesamiento as proc  # noqa: E402


# ══════════════════════════════════════════════════════════════
# CONSTANTES DE LA FASE 2 QUE USA LA FÁBRICA
# ══════════════════════════════════════════════════════════════

# raceeth (codebook YRBS 2023): código -> columna 0/1
RAZA = {1: "raza_amerindia", 2: "raza_asiatica", 3: "raza_negra",
        4: "raza_hawaiana_pacifico", 5: "raza_blanca", 6: "raza_hispana",
        7: "raza_multiple_hispana", 8: "raza_multiple_no_hispana"}

# (columna, códigos positivos, nombre del indicador)
INDICADORES = [
    ("sexo_cod",             [1],       "sexo_femenino"),
    ("salud_mental_cod",     [4, 5],    "salud_mental_mala"),
    ("redes_sociales_cod",   [6, 7, 8], "redes_uso_frecuente"),
    ("sueno_cod",            [5, 6, 7], "sueno_8h_o_mas"),
    ("actividad_fisica_cod", [6, 7, 8], "actividad_5_dias"),
]

# Las 7 variables de análisis, con su nombre de proyecto
VARIABLES_ANALISIS = [proc.COLUMNAS_ANALISIS[v] for v in proc.COLUMNAS_SIN_DEPENDENCIA]


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


# ══════════════════════════════════════════════════════════════
# OBSERVADORES
# ══════════════════════════════════════════════════════════════

class Bitacora:
    """Observador que acumula lo ocurrido en cada paso y lo entrega como tabla."""

    def __init__(self):
        self.registros = []

    def notificar(self, paso, filas, columnas, segundos, parametros):
        self.registros.append({"paso": paso, "filas": filas, "columnas": columnas,
                               "segundos": round(segundos, 5), "parametros": parametros})

    def a_dataframe(self) -> pd.DataFrame:
        return pd.DataFrame(self.registros)


class ReporteConsola:
    """Observador que imprime cada paso mientras ocurre."""

    def notificar(self, paso, filas, columnas, segundos, parametros):
        print(f"  {paso:<44} {filas:>6} filas, {columnas:>3} col  [{segundos:.4f}s]")


# ══════════════════════════════════════════════════════════════
# FÁBRICA
# ══════════════════════════════════════════════════════════════

def construir_pipeline_proyecto(estrategia=None, observable: bool = False) -> Pipeline:
    """Fábrica: arma el pipeline de la Fase 2 como una lista de Transformadores.

    Parámetros
    ----------
    estrategia : EstrategiaFaltantes, opcional (por defecto ConservarFaltantes).
    observable : si es True devuelve un PipelineObservable (patrón Observer).

    El orden es el de la Fase 2: eliminar orig_rec, seleccionar, marcar
    faltantes ANTES de cambiar tipos, tratar faltantes, castear, declarar
    ordinales, codificar raza/etnicidad y crear los cinco indicadores.
    """
    pasos = [
        EliminadorColumnaVacia("orig_rec"),
        SeleccionadorColumnas(proc.COLUMNAS_ANALISIS),
        MarcadorFaltantes(VARIABLES_ANALISIS),
        TratamientoFaltantes(VARIABLES_ANALISIS, estrategia),
        CastearCodigos(VARIABLES_ANALISIS),
        ConversorOrdinal(proc.ESCALAS_ORDINALES),
        CodificadorOneHot("raceeth_cod", RAZA),
    ]
    pasos += [IndicadorBinario(col, positivos, nombre)
              for col, positivos, nombre in INDICADORES]

    clase = PipelineObservable if observable else Pipeline
    return clase(pasos)
