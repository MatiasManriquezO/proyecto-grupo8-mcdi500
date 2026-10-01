# ADR-0001: No imputar los valores faltantes

- **Estado:** aceptada (F2, decisión 2.5) · ratificada en F3 (F3.16) y F4
- **Contexto:** las siete variables de análisis tienen entre 0,5 % y 24,4 % de faltantes. Según
  el Apéndice C del codebook, ninguna depende de una pregunta previa: son no respuesta, no
  saltos. La no respuesta no es aleatoria (varía con la posición en el cuestionario y la edad).
- **Decisión:** conservar los NA, marcar `n_faltantes_analisis` y `caso_completo`, y estimar con
  los casos disponibles en cada análisis. La estrategia se inyecta con el patrón Strategy
  (`ConservarFaltantes`).
- **Alternativas descartadas:** moda o mediana (inventa 4.398 respuestas de `q84` y desvía la
  distribución en 15,3 pp); eliminar filas con algún NA (pierde el 45,6 % de la muestra).
- **Consecuencias:** cada resultado declara su n (11.602 para `q80` × `q84`; 10.941 casos
  completos en el modelo). Cambiar la decisión es cambiar un argumento.
