"""Integración, resultados y comunicación de la Fase 4 — Grupo 8, MCDI500.

El notebook F4/notebooks/S3_F4_Integracion_Resultados_Grupo8.ipynb importa
estos módulos; reutiliza sin copiar los de F3/src/ y src/.

    encuesta       : DisenoMuestral, PrevalenciaPonderada,
                     RegresionLogisticaPonderada, ArbolPrevalenciaPonderada
                     (estimación con pesos, estratos y conglomerados)
    rendimiento    : medir_timeit, curva_crecimiento, orden_empirico (timeit)
    visualizacion  : las figuras de resultados (Matplotlib + Seaborn)
    verificacion   : entorno, requirements, ejecución de notebooks y pruebas

Dependencias entre capas (sin ciclos):
    src/procesamiento.py  <-  F3/src/  <-  F4/src/  <-  notebook F4
"""

__all__ = ["encuesta", "rendimiento", "verificacion", "visualizacion"]
