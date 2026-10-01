# ADR-0002: Vectorizar los conteos con np.bincount

- **Estado:** aceptada (F3.4) · extendida en F4 (F4.7)
- **Contexto:** el proyecto cuenta pares (contingencia q80 × q84) y suma aportes por
  conglomerado (varianza por diseño). Ambas son O(n), pero la constante depende de si el bucle
  corre en Python o en código compilado.
- **Decisión:** usar `np.bincount` sobre un índice entero (par codificado o conglomerado).
- **Evidencia (`timeit`):** contingencia, `iterrows` es miles de veces más lenta que `bincount`;
  varianza, el bucle es ≈ 39 veces y `groupby` ≈ 13 veces más lentos con 20.103 filas. Con pocos
  datos el costo fijo pesa: `groupby` supera al bucle solo desde ≈ 5.300 filas y `crosstab` es más
  lento que `zip` bajo ≈ 32.600; `bincount` gana en todos los tamaños medidos.
- **Alternativas descartadas:** `iterrows` (crea una Serie por fila), bucle con diccionario,
  `groupby`/`crosstab` (correctos, pero con alto costo fijo y más memoria).
- **Consecuencias:** se conserva la versión con bucle como referencia para verificar
  (`varianza_bucle`) y medir; nunca se usa en producción.
