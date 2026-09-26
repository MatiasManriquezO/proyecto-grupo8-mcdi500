"""Núcleo algorítmico de la Fase 3 — Grupo 8, MCDI500.

Dos conjuntos de módulos, con propósitos distintos:

Formativa 3 — el núcleo algorítmico con funciones
    contingencia : tabla de contingencia q80 x q84, cuatro implementaciones
    busqueda     : recuperación por identificador (lineal, binaria, índice)
    recursion    : versiones recursivas y su alternativa iterativa
    medicion     : tiempo y memoria (timeit, tracemalloc)
    analisis     : AnalisisContingencia, la única clase de esa entrega

Sumativa 2 — el mismo pipeline de la Fase 2, reorganizado en clases
    transformadores : Transformador (base) y los 8 pasos del proyecto
    estrategias     : tratamiento de faltantes (patrón Strategy)
    pipeline        : Pipeline, PipelineObservable, Bitacora y la fábrica

Los tres últimos se extraen del cuaderno
F3/notebooks/S2_F3_NucleoAlgoritmico_POO_Grupo8.ipynb, de modo que el código
de los módulos y el del cuaderno no pueden divergir.

Uso:
    from src.pipeline import construir_pipeline_proyecto
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
    "transformadores",
]
