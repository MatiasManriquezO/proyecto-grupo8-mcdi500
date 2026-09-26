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
| 3.9 | Versionar los dos notebooks de F3 por separado | `S2_F3_NucleoAlgoritmico_Eficiencia_POO.ipynb` (Formativa 3) y `S2_F3_NucleoAlgoritmico_POO_Grupo8.ipynb` (Sumativa 2): cada entrega queda trazable en su propio archivo |

---

## Esquema de documentación aplicado

Cada hallazgo de calidad se documenta con cinco elementos:

1. **Dato original** — qué trae el archivo tal como viene del CDC
2. **Problema detectado** — qué impide usarlo directamente
3. **Criterio aplicado** — qué regla se usó para decidir
4. **Resultado** — qué quedó tras aplicar la decisión, con su cifra
5. **Validación** — cómo se comprobó que la decisión no rompió nada
