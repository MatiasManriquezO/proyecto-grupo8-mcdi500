# ADR-0004: Recursión memoizada para segmentos y extensión por herencia

- **Estado:** aceptada (F3.23–F3.24) · extendida en F4 (F4.9)
- **Contexto:** la prevalencia por segmentos anidados (redes → sexo → edad) poda los segmentos
  con menos de 30 estudiantes, así que la profundidad de cada rama depende de los datos.
- **Decisión:** `ArbolPrevalencia` recorre el árbol recursivamente y memoiza el subconjunto de
  cada segmento con `functools.lru_cache` (4 niveles: 2.187 filtros → 529). En F4, la versión
  ponderada **hereda** y redefine solo `estadisticas()`.
- **Alternativas descartadas:** recursión ingenua (repite el trabajo de los ancestros); copiar el
  recorrido en F4 (duplicaría código y rompería la trazabilidad con F3).
- **Consecuencias:** `segmentacion.py` no se modificó en F4; una prueba verifica que las
  columnas muestrales del árbol ponderado son idénticas a las de F3.
