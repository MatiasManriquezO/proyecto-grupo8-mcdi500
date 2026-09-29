"""
estrategias.py — Tratamiento de valores faltantes (patrón Strategy).

TratamientoFaltantes (en transformadores.py) sabe CUÁNDO tratar los
faltantes; la estrategia que recibe decide CÓMO. Cambiar la decisión del
proyecto es cambiar un argumento, no el pipeline.

La estrategia del proyecto es ConservarFaltantes (bitácora 2.5): los
faltantes de las siete variables de análisis son "no responde" genuino,
no aleatorio, y rellenarlos inventaría respuestas. RellenarModa y
RellenarMediana se conservan porque fueron las alternativas evaluadas en
la Fase 2 y permiten repetir esa comparación cambiando solo la estrategia.

Al final del módulo están las estrategias de imputación GENÉRICAS que usa
ImputadorFlexible en la sección 10 del cuaderno (EstrategiaImputacion,
PorMediana, PorMedia, PorMedianaDeGrupo). Son didácticas: en el proyecto no
se imputa. Antes se definían en el cuaderno; se trasladaron aquí según la
Tabla 8 de la Formativa 3.

Grupo 8 · MCDI500 · Universidad Andrés Bello
"""

from __future__ import annotations

import pandas as pd


class EstrategiaFaltantes:
    """Contrato común: recibe una columna y devuelve la columna tratada."""

    etiqueta = "sin definir"

    def tratar(self, serie: pd.Series) -> pd.Series:
        """Devuelve la serie tratada. Lo implementa cada estrategia."""
        raise NotImplementedError("Cada estrategia debe implementar tratar().")

    def __repr__(self) -> str:
        return f"{type(self).__name__}()"


class ConservarFaltantes(EstrategiaFaltantes):
    """Estrategia del proyecto (bitácora 2.5): los faltantes se conservan como NA."""

    etiqueta = "conservar NA"

    def tratar(self, serie: pd.Series) -> pd.Series:
        # No cambia ningún valor, pero la decisión queda explícita en el código
        return serie


class RellenarModa(EstrategiaFaltantes):
    """Alternativa evaluada en F2: rellenar con la categoría más frecuente."""

    etiqueta = "moda"

    def tratar(self, serie: pd.Series) -> pd.Series:
        return serie.fillna(serie.mode().iloc[0])


class RellenarMediana(EstrategiaFaltantes):
    """Alternativa evaluada en F2: rellenar con la mediana del código."""

    etiqueta = "mediana"

    def tratar(self, serie: pd.Series) -> pd.Series:
        return serie.fillna(serie.median())


# ══════════════════════════════════════════════════════════════
# ESTRATEGIAS DE IMPUTACIÓN GENÉRICAS (didácticas, sección 10)
# ══════════════════════════════════════════════════════════════

class EstrategiaImputacion:
    """Contrato común de las estrategias de imputación de ImputadorFlexible."""

    etiqueta = "sin definir"

    def calcular(self, df: pd.DataFrame, columna: str):
        """Devuelve el valor (o el dict por grupo) con que se rellenará."""
        raise NotImplementedError("Cada estrategia debe implementar calcular().")

    def __repr__(self) -> str:
        return f"{type(self).__name__}()"


class PorMediana(EstrategiaImputacion):
    """Rellena con la mediana de la columna."""

    etiqueta = "mediana"

    def calcular(self, df, columna):
        return float(df[columna].median())


class PorMedia(EstrategiaImputacion):
    """Rellena con la media de la columna."""

    etiqueta = "media"

    def calcular(self, df, columna):
        return float(df[columna].mean())


class PorMedianaDeGrupo(EstrategiaImputacion):
    """Rellena con la mediana del grupo al que pertenece cada fila."""

    etiqueta = "mediana por grupo"

    def __init__(self, columna_grupo: str):
        self.columna_grupo = columna_grupo

    def calcular(self, df, columna):
        return df.groupby(self.columna_grupo)[columna].median().to_dict()
