# Bitácora de decisiones técnicas

Proyecto Grupo 8 — MCDI500 · Programación para la Ciencia de Datos
Dataset: Youth Risk Behavior Survey (YRBS) 2023, CDC

Una línea por decisión, con la cifra que la respalda. Este registro alimenta
directamente la sección de metodología del informe.

---

## Fase 0 — Selección del conjunto de datos

| # | Decisión | Evidencia |
|---|---|---|
| 0.1 | **Descartar** *Mental Health and Technology Usage Dataset* (Kaggle) | Variables categóricas repartidas en proporciones perfectamente parejas (33/33/33 y 25/25/25/25), incompatible con una encuesta real de 10.000 personas |
| 0.2 | Confirmar el descarte con evidencia externa | Análisis publicado sobre el mismo conjunto ajustó regresión multinomial: coeficientes ≈ 0 para todas las variables de interés (sueño −0,0034; tecnología −0,0110; redes sociales −0,0089; videojuegos −0,0190). Las variables se generaron de forma independiente: la pregunta no tenía respuesta posible |
| 0.3 | **Adoptar** YRBS 2023 (CDC), muestra nacional | 20.103 filas × 117 columnas, 4,9 MB, sin duplicados, faltantes reales con origen identificable, codebook público y citable |

---

## Fase 1 — Definición del problema

| # | Decisión | Evidencia |
|---|---|---|
| 1.1 | Acotar a **una** pregunta de investigación principal | Con 117 columnas no es posible avanzar sin acotar; la pregunta define la selección de columnas |
| 1.2 | Desenlace: `q84` (salud mental percibida) | Ordinal de 5 niveles (Never–Always), 21,9 % de faltantes |
| 1.3 | Exposición: `q80` (uso de dispositivos electrónicos) | Ordinal de 8 niveles (no usa – ≥6 h/día), 24,4 % de faltantes |
| 1.4 | Controles: `q85` (sueño), `q76` (actividad física), `q1` (edad), `q2` (sexo), `raceeth` | Confusores documentados en la literatura sobre pantallas y salud mental adolescente |
| 1.5 | Declarar alcance sin pruebas de hipótesis formales | Fases 1–2 cubren definición y pipeline de datos; la inferencia corresponde a fases posteriores |

---

## Fase 2 — Preprocesamiento

| # | Decisión | Evidencia |
|---|---|---|
| 2.1 | **Eliminar** `orig_rec` | 20.103/20.103 valores nulos (100 %) |
| 2.2 | **Conservar** `q6orig` declarando `dtype='string'` | Mezcla texto (`"N N"`) y códigos numéricos. No se silencia el `DtypeWarning`: la mezcla se documenta como hallazgo de calidad del archivo original |
| 2.3 | Seleccionar **11 de 117** columnas por código | Selección declarada en `COLUMNAS_ANALISIS` (`src/procesamiento.py`), reproducible desde el archivo original, nunca a mano |
| 2.4 | Clasificar `q1`, `q76`, `q80`, `q84`, `q85` como **ordinales** | Discrepancia documentada con el validador automático, que las lee como discretas por ser enteros 1–8. Tratarlas como numéricas asumiría equidistancia entre categorías, que la escala no garantiza |
| 2.5 | **No imputar** los faltantes de las variables seleccionadas | Según Apéndice C del codebook, ninguna de las 7 variables de análisis depende de una pregunta previa: sus nulos son *no responde* genuino, no *no aplica* estructural. Imputar un faltante estructural sería inventar datos de quien no fue consultado |
| 2.6 | **No ponderar** con `weight` / `stratum` / `psu` en F1–F2 | Ponderar exige análisis de encuestas complejas (varianza por conglomerados), fuera del alcance de esta etapa. Las tres columnas se conservan en el dataset procesado para fases posteriores |
| 2.7 | Transformar ordinales a `pd.Categorical(ordered=True)` | Hace explícito el orden y evita operaciones aritméticas inválidas sobre códigos de escala |

**Faltantes por variable seleccionada** (n = 20.103):

| Variable | Código YRBS | % faltantes | Tipo |
|---|---|---|---|
| `id_registro` | `record` | 0,0 % | — |
| `peso_muestral` | `weight` | 0,0 % | — |
| `estrato` | `stratum` | 0,0 % | — |
| `psu` | `psu` | 0,0 % | — |
| `edad_cod` | `q1` | 0,5 % | No responde |
| `sexo_cod` | `q2` | 0,8 % | No responde |
| `raceeth_cod` | `raceeth` | 1,8 % | No responde |
| `actividad_fisica_cod` | `q76` | 6,1 % | No responde |
| `sueno_cod` | `q85` | 13,2 % | No responde |
| `salud_mental_cod` | `q84` | 21,9 % | No responde |
| `redes_sociales_cod` | `q80` | 24,4 % | No responde |

---

## Fase 3 — Núcleo algorítmico, eficiencia y POO

| # | Decisión | Evidencia |
|---|---|---|
| F3.1 | **No generar datos nuevos**: la Fase 3 parte del CSV de la Fase 2 | El conjunto oficial sigue siendo `F2/data/processed/yrbs2023_seleccion_procesada.csv`. La guía de la evaluación lo dice expresamente: «No hay datos nuevos ni pipeline nuevo. Lo que cambia es la arquitectura del código» |
| F3.2 | Acotar el núcleo algorítmico al cruce `q80` × `q84` | 11.602 pares válidos de 20.103 registros (57,7 %): son los estudiantes que respondieron ambas preguntas. La tabla resultante tiene 8 × 5 = 40 celdas que suman 11.602 |
| F3.3 | Comparar **cuatro** implementaciones del mismo conteo antes de elegir | `iterrows`, diccionario, `crosstab` y `bincount` producen las 40 celdas idénticas. La equivalencia se comprueba con `assert` antes de medir: una versión más rápida que entrega otro resultado es un error, no una optimización |
| F3.4 | Adoptar `bincount` como implementación del conteo | Es la más rápida del grupo por dos órdenes de magnitud frente a `iterrows`. La medición cambió la decisión: `iterrows` era la forma intuitiva de escribirlo |
| F3.5 | **Descartar** la recursión lineal para recorrer filas | Lanza `RecursionError` sobre ~1.000 filas: el límite de profundidad de Python impide aplicarla a las 20.103 del conjunto |
| F3.6 | **Descartar** también *divide y vencerás* para el conteo | Funciona con profundidad ⌈log₂ 20.103⌉ = 15, pero tarda 8,11 ms frente a 6,42 ms del bucle iterativo. Un recorrido secuencial no gana nada partiéndose en dos |
| F3.7 | **Conservar** la recursión solo donde la profundidad es desconocida | `aplanar()` recorre metadatos anidados cuya profundidad puede crecer, y `buscar_binaria_rec()` resulta ~218 veces más rápida que la búsqueda lineal en 1.000 consultas |
| F3.8 | Reportar **razones** entre implementaciones, no tiempos absolutos | Los milisegundos dependen del equipo; las razones se mantienen entre máquinas. Es la única forma de que la medición sea reproducible por el equipo docente |
| F3.9 | Incorporar **una sola clase**, `AnalisisContingencia` | Una clase se justifica cuando el componente necesita recordar algo entre llamadas. Las demás piezas son funciones puras: convertirlas en clases habría agregado estado sin motivo |
| F3.10 | Separar el código en cinco módulos por responsabilidad | Cada archivo tiene un propósito enunciable en una frase (alta cohesión) y `medicion.py` no conoce ninguna función del proyecto (bajo acoplamiento): puede medir cualquier implementación nueva sin modificarse |
| F3.11 | Reorganizar cada paso del pipeline como clase hija de `Transformador`, con `ajustar` y `transformar` separados | Evita la fuga de datos: la media de `edad_cod` escalada en prueba es −0,013 y no 0, porque los parámetros vienen solo del entrenamiento. Transformar sin ajustar lanza `RuntimeError` |
| F3.12 | Separar entrenamiento y prueba solo con los registros que respondieron `salud_mental_cod` | La variable objetivo no se imputa (2.5): 15.705 de 20.103 registros, 12.564 de entrenamiento y 3.141 de prueba (80/20, semilla 42) |
| F3.13 | Armar el pipeline desde la configuración con `IMPUTAR_ORDINALES = False` y `ESCALAR_ORDINALES = False` | Respeta 2.4 y 2.5: conserva 5.687 NA en las cuatro escalas ordinales y deja los códigos del codebook intactos. Seis controles OK («VERIFICACIÓN APROBADA») |
| F3.14 | Localizar la raíz del repositorio con `encontrar_raiz()` en el notebook de la Formativa 3 | Misma convención de F1 y F2: el notebook corre en cualquier computador del grupo sin editar rutas |
| F3.15 | Guardar las salidas de la Formativa 3 en `F3/data/_demo/` con prefijo `demo_` | Son evidencia de la ejecución, no datos oficiales: el conjunto oficial sigue siendo el de F2 (F3.1) |
| F3.16 | Adoptar **Strategy** como patrón principal, aplicado al tratamiento de faltantes | En la Sumativa 2, rellenar con moda o mediana inventa 4.398 respuestas de salud mental y desvía su distribución en 15,3 puntos porcentuales; conservar NA no la desvía (0,0) |
| F3.17 | Adoptar la versión vectorizada (`pd.cut`) para clasificar horas de sueño desde el tamaño real | Con 1.000 filas es más lenta que el bucle (razón 0,4), pero gana desde 5.000 filas: 3,7 veces con 20.000 y 5,1 con 50.000. Costo: unas tres veces más memoria (0,51 frente a 0,17 MB) |
| F3.18 | Verificar el pipeline de clases contra el archivo de F2, no contra código reescrito | Formativa 3: las 8 columnas `raza_*` coinciden en 19.733 filas y las 370 sin raza siguen como NA. Sumativa 2: el pipeline de 12 clases reproduce el CSV de F2 carácter por carácter |
| F3.19 | Mover las clases del notebook a `F3/src/` (`transformadores.py`, `estrategias.py`, `pipeline.py`) y que el notebook las **importe** | Retroalimentación de la Formativa 3 (repositorio). El informe declaraba una organización en módulos que todavía no existía; ahora la tabla de arquitectura se genera con `inspect.getfile` y muestra el archivo real de cada clase (27 componentes, 5 didácticos en el cuaderno). El pipeline importado reproduce el CSV de F2 carácter por carácter. *Completada por F3.26* |
| F3.20 | Mantener **dos carpetas de código con propósitos distintos**: `src/` (F1–F2) y `F3/src/` (núcleo de F3) | Retroalimentación de la Formativa 3. `src/procesamiento.py` sigue siendo la fuente única de las constantes del codebook y lo usan los notebooks de F1 y F2; `F3/src/fabrica.py` lo importa en vez de copiar sus constantes. Consolidarlas habría obligado a reescribir F1 y F2 sin beneficio |
| F3.21 | Un solo notebook central para la Sumativa 2 | Retroalimentación de la Formativa 3. `S2_F3_NucleoAlgoritmico_POO_Grupo8.ipynb` es el entregable; el de la Formativa 3 pasa a `F3/notebooks/formativa3/` como registro histórico |
| F3.22 | Integrar en el notebook central los scripts del avance formativo sin copiarlos | Contingencia q80 × q84: `bincount` 0,070 ms frente a `iterrows` 168,2 ms (≈2.400 veces). Búsqueda de 1.000 registros: diccionario 0,124 ms, binaria recursiva 2,68 ms, lineal 637,8 ms; el diccionario ocupa ≈11 veces más memoria que el arreglo ordenado (1,70 frente a 0,15 MB) |
| F3.23 | Reemplazar Fibonacci por un cálculo propio que se beneficia de memoización: prevalencia de salud mental no buena por segmentos anidados (redes → sexo → edad), con poda en n < 30 | Retroalimentación de la Formativa 3 (eficiencia). Con 4 niveles (530 segmentos) la recursión ingenua aplica 2.187 filtros y la memoizada 529 (uno por segmento): 54,8 frente a 12,1 ms (4,5 veces); `groupby` por nivel tarda 30,9 ms. La caché retiene ≈0,47 MB. Las tres versiones entregan la misma tabla |
| F3.24 | Adoptar la recursión memoizada (`ArbolPrevalencia(memoizar=True)`) para la descripción por segmentos | Es la más rápida desde tres niveles, que es la profundidad de `JERARQUIA_SEGMENTOS` (2,0 veces la ingenua con 3 niveles y 4,5 con 4), respeta la poda sin calcular segmentos que luego se descartan y la profundidad de cada rama depende de los datos (criterio F3.7). Con uno y dos niveles hay poco o ningún trabajo repetido y la memoizada queda algo más lenta (razón 0,9): se reporta |
| F3.25 | Validar también el núcleo analítico | El nivel 1 del árbol coincide con la tabla de contingencia calculada por otro camino (`bincount`); los segmentos de nivel 1 suman 11.602, los estudiantes con ambas respuestas; cinco excepciones nuevas verificadas (columna inexistente, `n_minimo` = 0, estrategia inválida, observador sin `notificar()`, versiones que no coinciden) |
| F3.26 | Ejecutar completa la Tabla 8 de la Formativa 3: **ninguna clase se define en el notebook** | Retroalimentación de la Formativa 3 («muevan las clases del notebook a los archivos que ya proyectaron en la Tabla 8»). Se crean `carga.py` (leer_archivo, verificar_esquema, cargar, perfilar), `fabrica.py` (construir_pipeline_proyecto y crear_transformador) y `observadores.py` (Bitacora, ReporteConsola); `pipeline.py` queda solo con la orquestación. Las 5 clases hijas didácticas pasan a `transformadores.py` (`CLASES_DIDACTICAS`), sus estrategias a `estrategias.py` y los ejemplos de las secciones 2, 3 y 6 a `didacticos.py`. Evidencia en la sección 17 del notebook: 0 clases definidas en el cuaderno, 15 de 15 componentes de la Tabla 8 en el archivo proyectado (`F3/resultados/tabla8_ejecutada_f3.csv`), 40 componentes documentados y el pipeline sigue reproduciendo el CSV de F2 carácter por carácter |

**Resultados persistidos** en `F3/resultados/`, cada uno releído tras guardarse
para verificar la escritura:

| Archivo | Contenido |
|---|---|
| `tabla4_implementaciones.csv` | Las cuatro implementaciones del conteo, con tiempo y memoria |
| `tabla5_busqueda.csv` | Búsqueda lineal, binaria e índice sobre 1.000 consultas |
| `tabla6_recursion.csv` | Casos de recursión evaluados y la decisión de cada uno |
| `tabla7_modulos.csv` | Los cinco módulos, leídos de sus propios docstrings |
| `tabla_proporciones.csv` | Prevalencia de salud mental deteriorada por nivel de uso |
| `arquitectura_codigo.csv` | Componentes por capa, generado leyendo el código real |
| `parametros_pipeline_f3.csv` | Sumativa 2: lo que aprendió cada una de las 12 clases del pipeline |
| `bitacora_ejecucion_f3.csv` | Sumativa 2: filas, columnas y tiempo de cada paso, registrados por el patrón Observer |
| `arquitectura_f3.csv` | Sumativa 2: clase base, clases hijas, estrategias y orquestadores |
| `eficiencia_faltantes_f3.csv` | Sumativa 2: conteo de faltantes por fila con bucle, `apply` y vectorizado |
| `eficiencia_crecimiento_f3.csv` | Sumativa 2: cómo crece el costo de las tres versiones con el tamaño |
| `eficiencia_contingencia_f3.csv` | Sumativa 2: las cuatro implementaciones de la contingencia, re-medidas desde el notebook central |
| `eficiencia_busqueda_f3.csv` | Sumativa 2: búsqueda lineal, binaria recursiva y diccionario, re-medidas |
| `eficiencia_memoizacion_f3.csv` | Sumativa 2: recursión ingenua, memoizada y `groupby` según la profundidad (1 a 4 niveles) |
| `prevalencia_segmentos_f3.csv` | Sumativa 2: los 121 segmentos redes → sexo → edad con n, positivos y porcentaje |

Los archivos `tabla*.csv`, `tabla_proporciones.csv` y `arquitectura_codigo.csv` los generó el notebook de la Formativa 3 (hoy en `F3/notebooks/formativa3/`); los terminados en `_f3.csv`, el notebook central de la Sumativa 2.

Las salidas de la Formativa 3 quedan en `F3/data/_demo/` (F3.15).

**Cifras verificadas de esta fase** (n = 20.103):

| Medida | Valor |
|---|---|
| Pares válidos `q80` × `q84` | 11.602 (57,7 % del total) |
| Celdas de la tabla de contingencia | 40 (8 niveles × 5 niveles) |
| Prevalencia de salud mental deteriorada | 20,3 % en el nivel 1 (no usa) → 35,3 % en el nivel 8 (más de una vez por hora). El aumento es casi monótono: el nivel 2 baja a 17,6 %, único quiebre de la serie |
| Faltantes conservados, sin imputar | 13.813 en las siete variables de análisis |
| Profundidad de *divide y vencerás* | ⌈log₂ 20.103⌉ = 15 |
| Límite de la recursión lineal | `RecursionError` sobre ~1.000 filas |
| Prevalencia por uso de redes y sexo (Sumativa 2) | Sexo femenino: 27,3 % (no usa) → 45,8 % (más de una vez por hora). Sexo masculino: 16,3 % → 22,5 %. La brecha crece con la frecuencia de uso |
| Segmentos del árbol redes → sexo → edad (n ≥ 30 para subdividir) | 121 (1 + 8 + 16 + 96) |

---

## Fase 4 — Integración, validación y comunicación

| # | Decisión | Evidencia |
|---|---|---|
| F4.1 | **Ponderar** con `weight`, `stratum` y `psu` todas las cifras de resultados (cierra 2.6) | Sin ponderar, 30,6 % reporta salud mental no buena; la cifra poblacional es 28,5 %. En estudiantes que no usan redes la diferencia es de 4,8 pp (20,3 % → 15,5 %) |
| F4.2 | **Restaurar** los 7 módulos borrados por el commit `f809a58` (`src/procesamiento.py`, `F3/src/{segmentacion, contingencia, analisis, busqueda, medicion, recursion}.py`) | El commit subió la carpeta `F3/src/` por la web y reemplazó su contenido: el notebook central de F3 fallaba con `ModuleNotFoundError`. Se restauraron desde `f809a58^` sin cambios; F1, F2 y F3 vuelven a ejecutarse completos |
| F4.3 | Varianza por **linealización de Taylor** (conglomerados con reemplazo) e IC en **escala logit** con *t* de 73 gl | Es el método de los informes del CDC. Las 6 cifras y los 6 IC oficiales (Verlenden et al., 2024; Young et al., 2024) se reproducen al decimal |
| F4.4 | Conglomerado = par (`estrato`, `psu`) | Los códigos de PSU se repiten entre estratos: 82 códigos, 89 conglomerados reales en 16 estratos |
| F4.5 | Regresión logística implementada con IRLS + sándwich por diseño, sin `statsmodels` | Coeficientes contrastados con `statsmodels.GLM` (mismos pesos): diferencia máxima 3·10⁻¹⁵. Se evita una dependencia pesada que no calcula varianza por diseño |
| F4.6 | Subpoblaciones con **z = 0 fuera del dominio**, sin eliminar filas | Eliminar filas quitaría conglomerados y subestimaría la varianza; los IC por sexo coinciden con el CDC |
| F4.7 | Adoptar `np.bincount` para la varianza por diseño | `timeit` con 20.103 filas: ≈ 13 veces más rápida que `groupby` y ≈ 39 veces más que el bucle; acepta matrices n × k (sándwich) |
| F4.8 | Medir con **`timeit`** (`autorange` + `repeat`, mínimo de 5) y estimar el **orden empírico** (pendiente log-log) | Búsqueda lineal: pendiente ≈ 1; binaria ≈ 0,1; diccionario ≈ 0. Las vectorizadas muestran costo fijo a n pequeño |
| F4.9 | Extender el árbol de F3 por **herencia** (`ArbolPrevalenciaPonderada`) en vez de modificar `segmentacion.py` | Solo se redefine `estadisticas()`; las columnas muestrales son idénticas a F3 y el nivel 2 coincide con `PrevalenciaPonderada` |
| F4.10 | Jerarquía `EstimadorEncuesta` (abstracta) → `PrevalenciaPonderada`, `RegresionLogisticaPonderada` | Comparten diseño, verificación y `resumen()`; cada una implementa `estimar()` (polimorfismo) |
| F4.11 | Edad como término lineal en el modelo; uso de redes con un indicador por nivel | La edad tiene 7 niveles con muy pocos casos en ≤ 13 años; `q80` es ordinal y no se asume equidistancia (2.4) |
| F4.12 | Contrastar H2 con un término de interacción uso frecuente × sexo femenino | OR de interacción 1,49 (IC 1,11–2,00; p = 0,008) |
| F4.13 | Agregar `tests/` con 36 pruebas `pytest` (F4 y regresión de F1–F3) | Un borrado como el de F4.2 falla en segundos; el notebook F4 corre la batería |
| F4.14 | Verificar la reproducibilidad ejecutando F1–F3 en una **copia temporal** del repositorio | `nbclient` los ejecuta sin sobrescribir los CSV versionados; 3 de 3 sin errores |
| F4.15 | Separar cálculo y dibujo: las figuras reciben tablas ya calculadas (`visualizacion.py`) | Las cifras se prueban sin abrir gráficos; las 5 figuras usan colores validados para daltonismo |
| F4.16 | Agregar `scipy`, `matplotlib`, `seaborn` y `pytest` a `requirements.txt` | `scipy` solo para el cuantil *t*; el resto, figuras y pruebas |
| F4.17 | Graficar desde una **copia interpretable** (`tabla_visual`), no desde la matriz del modelo | La matriz `X` tiene 19 columnas de indicadores 0/1; la copia tiene 8 filas con etiqueta del codebook, orden ordinal declarado y n por grupo (apunte Fase 4, §5). No hay escalamiento que revertir (2.4) |
| F4.18 | Reportar el **punto de cruce** de las versiones con costo fijo | `groupby` supera al bucle solo desde ≈ 5.300 filas; `crosstab` es más lento que `zip` bajo ≈ 32.600 filas, el rango del proyecto (11.602 pares) |
| F4.19 | Una figura por objetivo específico, en tres actos (contexto, contraste, resolución) | Título con el hallazgo, n bajo cada categoría (niveles 2–3 con 307 y 175 casos), color con función (rojo = hallazgo) y cuatro frases por figura |
| F4.20 | Verificación final calculada desde archivos (sección 14) | Cada OE1–OE5 se enlaza a su archivo de evidencia y se comprueba que existe; huella SHA-256 del CSV del CDC, del CSV de F2 y de `requirements.txt` con fin de línea normalizado a `\n` (Git en Windows guarda `\r\n`); lista de 11 comprobaciones de la guía, 11 de 11 |
| F4.21 | Declarar el significado de cada código en un solo lugar (`CATEGORIAS` en `src/procesamiento.py`) y mostrarlo en la sección 3 del notebook | 7 variables y 45 códigos con etiqueta, validados contra los dominios; se corrige el comentario que describía `q80` en horas diarias, cuando es una escala de frecuencia (F1 y F2 ya lo aclaraban) |

**Cifras verificadas de esta fase** (ponderadas, IC 95 %):

| Medida | Valor |
|---|---|
| Salud mental no buena, total | 28,5 % (26,7–30,4) · femenino 38,8 % · masculino 18,8 % |
| No usa redes → más de una vez por hora | 15,5 % (11,8–20,1) → 33,1 % (30,7–35,6) |
| Femenino: no usa → más de una vez por hora | 20,9 % → 44,1 % (+23,2 pp) |
| Masculino: no usa → más de una vez por hora | 12,6 % → 20,1 % (+7,5 pp) |
| Duerme 8 h o más | 23,2 % (21,4–25,1); no usa 30,6 % (22,6–39,9), más de una vez por hora 21,4 % |
| OR ajustado, más de una vez por hora vs. no usa | 2,45 (1,55–3,85), n = 10.941 casos completos |
| OR ajustado, duerme 8 h o más | 0,48 (0,40–0,58) |

Las decisiones de arquitectura con contexto y alternativas descartadas están en `docs/adr/`.

---

## Infraestructura del repositorio

| # | Decisión | Evidencia |
|---|---|---|
| 3.1 | Agregar `.gitignore` | No existía; se excluyen `.DS_Store`, `.ipynb_checkpoints/`, `__pycache__/`, entornos virtuales y salidas regenerables |
| 3.2 | Eliminar `.ipynb_checkpoints` del control de versiones | 1 archivo versionado por error en `F2/notebooks/` |
| 3.3 | Normalizar `F1/Data/` → `F1/data/` | Git registraba minúscula y el disco mayúscula: la ruta fallaba en Linux y Windows, no en macOS |
| 3.4 | Eliminar `mental_health_and_technology_usage_2024.csv` | Dataset descartado en la decisión 0.1; 10.000 filas sin uso en el proyecto |
| 3.5 | Mover `F2/src/` → `src/` en la raíz | El README y el informe declaraban `src/` en la raíz; se unifica con lo declarado |
| 3.6 | Crear `F2/data/processed/` | Declarada en el README como salida del pipeline y entrada de la Fase 3 |
| 3.7 | Mantener un único `requirements.txt` en la raíz | Se regenera con `pip freeze` tras cada instalación |
| 3.8 | Eliminar `F3/data/processed/` | Contenía salidas de una versión anterior del notebook de F3 que imputaba y escalaba las escalas ordinales, en contra de 2.4 y 2.5. Se reemplaza por `F3/data/_demo/` |
| 3.9 | Versionar los dos notebooks de F3 por separado | `S2_F3_NucleoAlgoritmico_Eficiencia_POO.ipynb` (Formativa 3) y `S2_F3_NucleoAlgoritmico_POO_Grupo8.ipynb` (Sumativa 2): cada entrega queda trazable en su propio archivo. *Actualizada por 3.10* |
| 3.10 | Mover el notebook de la Formativa 3 a `F3/notebooks/formativa3/` | Retroalimentación de la Formativa 3: dos cuadernos parecidos en la misma carpeta no dejaban claro cuál evaluar. En `F3/notebooks/` queda solo el entregable de la Sumativa 2 |
| 3.11 | Documentar en el README qué contiene cada carpeta `src` | `src/` = módulo de F1–F2; `F3/src/` = núcleo de F3 (decisión F3.20) |
| 3.12 | Restaurar los módulos borrados por `f809a58` y prohibir subir carpetas por la web que reemplacen su contenido | Ver F4.2. Regla: se suben archivos, no carpetas; antes de subir se ejecuta `python -m pytest tests -q` |
| 3.13 | Crear `changelog.md` en la raíz | Registro por fecha, descripción, commit y justificación técnica, exigido por la Sumativa 3 |
| 3.14 | Crear `tests/`, `docs/adr/` y `docs/arquitectura.md` | Pruebas automatizadas, registro de decisiones de arquitectura (ADR) y diagramas de flujo, componentes, secuencia y datos |

---

## Esquema de documentación aplicado

Cada hallazgo de calidad se documenta con cinco elementos:

1. **Dato original** — qué trae el archivo tal como viene del CDC
2. **Problema detectado** — qué impide usarlo directamente
3. **Criterio aplicado** — qué regla se usó para decidir
4. **Resultado** — qué quedó tras aplicar la decisión, con su cifra
5. **Validación** — cómo se comprobó que la decisión no rompió nada
