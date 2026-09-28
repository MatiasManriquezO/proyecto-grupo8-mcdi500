"""Núcleo algorítmico de la Fase 3 — Grupo 8, MCDI500.

El notebook central (F3/notebooks/S2_F3_NucleoAlgoritmico_POO_Grupo8.ipynb)
importa estos módulos: no redefine las clases del proyecto.

Pipeline de la Fase 2 reorganizado en clases (POO)
    transformadores : Transformador (base) y los 8 pasos del proyecto
    estrategias     : tratamiento de faltantes (patrón Strategy)
    pipeline        : Pipeline, PipelineObservable, Bitacora y la fábrica

Núcleo analítico
    segmentacion    : prevalencia por segmentos anidados (recursión + memoización)
    contingencia    : tabla de contingencia q80 x q84, cuatro implementaciones
    analisis        : AnalisisContingencia, clase con estado de la Formativa 3
    busqueda        : recuperación por identificador (lineal, binaria, índice)

Utilidades
    recursion       : casos recursivos evaluados y su alternativa iterativa
    medicion        : tiempo y memoria (timeit, tracemalloc)

Las constantes del codebook no se repiten aquí: pipeline.py las importa de
src/procesamiento.py (módulo de F1-F2, en la raíz del repositorio).

Uso (con F3/src en sys.path):
    from pipeline import construir_pipeline_proyecto
    resultado = construir_pipeline_proyecto().ajustar(df).transformar(df)
"""

__all__ = [
    "analisis",
    "busqueda",
    "contingencia",
    "estrategias",
    "medicion",
    "pipeline",
    "recursion",
    "segmentacion",
    "transformadores",
]
