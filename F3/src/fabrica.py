"""
fabrica.py — Fábricas que arman el pipeline desde la configuración (patrón Factory).

Concentra en un solo lugar la decisión de QUÉ transformador construir para
cada variable, a partir de constantes declaradas, en vez de repetirla en
cada cuaderno.

  construir_pipeline_proyecto  arma los 12 pasos de la Fase 2 desde las
                               constantes de src/procesamiento.py.
  crear_transformador          devuelve el transformador que corresponde a
                               un rol analítico (ejemplo didáctico, sección 10).
  RAZA, INDICADORES, VARIABLES_ANALISIS
                               constantes de la Fase 2 que usa la fábrica.

Las constantes de columnas y escalas NO se copian: se importan del módulo de
la Fase 2 (src/procesamiento.py, en la raíz del repositorio), que sigue
siendo la fuente única de verdad del proyecto.

Ubicación proyectada en la Tabla 8 de la Formativa 3 (capa «Orquestación»).

Grupo 8 · MCDI500 · Universidad Andrés Bello
"""

from __future__ import annotations

import sys
from pathlib import Path

try:                                    # importado como paquete (F3.src)
    from .transformadores import (EliminadorColumnaVacia, SeleccionadorColumnas,
                                  MarcadorFaltantes, TratamientoFaltantes,
                                  CastearCodigos, ConversorOrdinal,
                                  CodificadorOneHot, IndicadorBinario,
                                  ImputadorFlexible, CodificadorNominal,
                                  EscaladorEstandar, EliminadorColumnas)
    from .pipeline import Pipeline, PipelineObservable
except ImportError:                     # importado con F3/src en sys.path
    from transformadores import (EliminadorColumnaVacia, SeleccionadorColumnas,
                                 MarcadorFaltantes, TratamientoFaltantes,
                                 CastearCodigos, ConversorOrdinal,
                                 CodificadorOneHot, IndicadorBinario,
                                 ImputadorFlexible, CodificadorNominal,
                                 EscaladorEstandar, EliminadorColumnas)
    from pipeline import Pipeline, PipelineObservable

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
# FÁBRICA DEL PROYECTO
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


# ══════════════════════════════════════════════════════════════
# FÁBRICA DIDÁCTICA (sección 10 del cuaderno)
# ══════════════════════════════════════════════════════════════

def crear_transformador(rol: str, columna: str, **parametros):
    """Devuelve el transformador que corresponde al rol analítico."""
    rol = rol.strip().lower()

    if rol == "continua":
        return ImputadorFlexible(columna, parametros.get("estrategia"))
    if rol == "nominal":
        return CodificadorNominal(columna)
    if rol == "escalar":
        return EscaladorEstandar(columna)
    if rol == "identificador":
        return EliminadorColumnas(columna)

    raise ValueError(
        f"Rol desconocido: '{rol}'. "
        "Roles válidos: continua, nominal, escalar, identificador."
    )
