"""Núcleo algorítmico de la Fase 3 — Grupo 8, MCDI500.

El notebook central (F3/notebooks/S2_F3_NucleoAlgoritmico_POO_Grupo8.ipynb)
importa estos módulos: no define ninguna clase propia. La organización
ejecuta la Tabla 8 de la Formativa 3 («Componentes, responsabilidades y
ubicación propuesta»).

Entrada
    carga           : leer_archivo, verificar_esquema, cargar, perfilar

Pipeline de la Fase 2 reorganizado en clases (POO)
    transformadores : Transformador (base), los 8 pasos del proyecto y
                      5 pasos genéricos didácticos
    estrategias     : tratamiento de faltantes (patrón Strategy)
    pipeline        : Pipeline y PipelineObservable (orquestación)
    fabrica         : construir_pipeline_proyecto (patrón Factory)
    observadores    : Bitacora y ReporteConsola (patrón Observer)

Núcleo analítico
    segmentacion    : prevalencia por segmentos anidados (recursión + memoización)
    contingencia    : tabla de contingencia q80 x q84, cuatro implementaciones
    analisis        : AnalisisContingencia, clase con estado de la Formativa 3
    busqueda        : recuperación por identificador (lineal, binaria, índice)

Utilidades y ejemplos
    recursion       : casos recursivos evaluados y su alternativa iterativa
    medicion        : tiempo y memoria (timeit, tracemalloc)
    didacticos      : clases de ejemplo de las secciones 2, 3 y 6 del cuaderno

Las constantes del codebook no se repiten aquí: fabrica.py las importa de
src/procesamiento.py (módulo de F1-F2, en la raíz del repositorio).

Uso (con F3/src en sys.path):
    from fabrica import construir_pipeline_proyecto
    resultado = construir_pipeline_proyecto().ajustar(df).transformar(df)
"""

__all__ = [
    "analisis",
    "busqueda",
    "carga",
    "contingencia",
    "didacticos",
    "estrategias",
    "fabrica",
    "medicion",
    "observadores",
    "pipeline",
    "recursion",
    "segmentacion",
    "transformadores",
]
