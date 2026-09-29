# Proyecto Grupo 8 — MCDI500

Análisis de la asociación entre el uso de dispositivos electrónicos para
entretenimiento y la salud mental percibida en estudiantes de enseñanza media
de Estados Unidos, mediante un flujo de trabajo reproducible, documentado y
colaborativo.

## Pregunta de investigación

> ¿Qué relación existe entre los patrones de uso de tecnología y los indicadores
> de salud mental autopercibida y horas de sueño en los estudiantes incluidos en el
> dataset YRBS 2023, considerando variables sociodemográficas y de actividad física?


## Integrantes
- Abigail Robles Chávez (@AbigailRoblesC-github)
- Daniel Pérez Ramirez (@DanielRamirezPerez-github)
- Matias Manriquez Ortiz (@MatiasManriquezO-github)
- Roberto Sánchez Saldivia (@RobertSanchezS-github)

## Datos

- **Nombre oficial:** Youth Risk Behavior Survey (YRBS) 2023 — muestra nacional.
- **Institución:** Centers for Disease Control and Prevention (CDC), Estados Unidos.
- **Enlace:** https://www.cdc.gov/yrbs/data/index.html
- **Archivo en el repositorio:** `F1/data/raw/XXH2023_YRBSS_data.csv`
- **Licencia:** dato público de agencia federal estadounidense, de libre uso con
  atribución a la fuente.
- **Dimensiones:** 20.103 registros × 117 variables originales.
- **Tipo de estudio:** encuesta transversal con **diseño muestral complejo**
  (`weight`, `stratum`, `psu`). Sin ponderar, los resultados describen la muestra
  y no la población de estudiantes de EE. UU.
- **Documentación oficial:** *2023 YRBS Data User's Guide* (septiembre 2024),
  codebook en págs. 21–55.

### Variables seleccionadas para el análisis

| Código YRBS | Nombre en el proyecto | Rol | Escala |
|---|---|---|---|
| `q80` | `redes_sociales_cod` | Variable de exposición | Ordinal (1 = no usa … 8 = más de una vez por hora) |
| `q84` | `salud_mental_cod` | Variable de desenlace | Ordinal (1 = Never … 5 = Always) |
| `q85` | `sueno_cod` | Control | Ordinal (1 = ≤4 h … 7 = ≥10 h) |
| `q76` | `actividad_fisica_cod` | Control | Ordinal (1 = 0 días … 8 = 7 días) |
| `q1` | `edad_cod` | Control demográfico | Ordinal (1 = ≤12 … 7 = ≥18 años) |
| `q2` | `sexo_cod` | Control demográfico | Nominal (1 = Femenino, 2 = Masculino) |
| `raceeth` | `raceeth_cod` | Control demográfico | Nominal (8 categorías) |
| `record` | `id_registro` | Identificador | — |
| `weight`, `stratum`, `psu` | `peso_muestral`, `estrato`, `psu` | Diseño muestral | — |

> **Nota metodológica:** las variables codificadas 1–8 son **ordinales**, no
> numéricas discretas. Tratarlas como numéricas asumiría equidistancia entre
> categorías (que la distancia entre "Rara vez" y "A veces" es igual a la que hay
> entre "A veces" y "Siempre"), lo cual el diseño de la escala no garantiza.

### Hallazgos de calidad documentados

- `q6orig` mezcla texto (`"N N"`) y códigos numéricos → se declara
  `dtype={'q6orig': 'string'}` al cargar. No se descarta: es un hallazgo real.
- `orig_rec` está vacía al 100 % (20.103/20.103 nulos) → se elimina.
- Faltantes entre 20 % y 47 % en varias columnas: corresponden a **saltos de
  pregunta** del cuestionario (no aplica), no a suciedad del archivo.

## Estructura del repositorio

Cada fase guarda sus propios datos y su propia documentación. En `docs/` queda
solo lo transversal al proyecto completo.

```
proyecto-grupo8-mcdi500/
├─ src/                            código de F1–F2 (ver «Dos carpetas src»)
│  └─ procesamiento.py              funciones compartidas por todas las fases:
│                                   carga, selección, diagnóstico,
│                                   clasificación, transformación, validación
├─ F1/
│  ├─ data/raw/
│  │  └─ XXH2023_YRBSS_data.csv     dataset original YRBS 2023 (CDC)
│  ├─ data/docs/                    documentación de la Fase 1
│  │  ├─ diccionario_variables_f1.csv
│  │  ├─ evaluacion_criterios_dataset.csv
│  │  ├─ metadatos_fase1.json
│  │  └─ vinculacion_mapa_conceptual.csv
│  └─ notebooks/
│     └─ S1_F1_Definicion.ipynb     Fase 1 — definición del problema y entorno
├─ F2/
│  ├─ data/processed/
│  │  └─ yrbs2023_seleccion_procesada.csv   salida del pipeline: el conjunto
│  │                                        oficial del proyecto
│  ├─ docs/                         documentación de la Fase 2
│  │  ├─ diccionario_variables_f2.csv
│  │  ├─ metadatos_f2.csv
│  │  └─ registro_preprocesamiento_f2.csv
│  └─ notebooks/
│     └─ S1_F2_Preprocesamiento.ipynb   Fase 2 — obtención, limpieza y
│                                       transformación
├─ F3/
│  ├─ notebooks/
│  │  ├─ S2_F3_NucleoAlgoritmico_POO_Grupo8.ipynb
│  │  │                             ★ NOTEBOOK CENTRAL DE LA FASE 3 (Sumativa 2):
│  │  │                             pipeline de F2 en clases, núcleo analítico,
│  │  │                             mediciones y verificación contra F2
│  │  └─ formativa3/
│  │     └─ S2_F3_NucleoAlgoritmico_Eficiencia_POO.ipynb
│  │                                registro histórico de la Formativa 3 (no se evalúa)
│  ├─ src/                          núcleo algorítmico de F3 (lo importa el notebook,
│  │                                que no define ninguna clase; organización de la
│  │                                Tabla 8 de la Formativa 3)
│  │  ├─ __init__.py
│  │  ├─ carga.py                   entrada: leer_archivo, verificar_esquema, cargar, perfilar
│  │  ├─ transformadores.py         Transformador (base), los 8 pasos del pipeline de F2
│  │  │                             y 5 pasos genéricos didácticos (CLASES_DIDACTICAS)
│  │  ├─ estrategias.py             tratamiento de faltantes (patrón Strategy)
│  │  ├─ pipeline.py                Pipeline y PipelineObservable (orquestación)
│  │  ├─ fabrica.py                 construir_pipeline_proyecto (patrón Factory)
│  │  ├─ observadores.py            Bitacora y ReporteConsola (patrón Observer)
│  │  ├─ segmentacion.py            prevalencia por segmentos (recursión + memoización)
│  │  ├─ contingencia.py            tabla q80 × q84, cuatro implementaciones
│  │  ├─ analisis.py                AnalisisContingencia (clase con estado)
│  │  ├─ busqueda.py                búsqueda por identificador (3 versiones)
│  │  ├─ recursion.py               casos recursivos y alternativa iterativa
│  │  ├─ medicion.py                medir(), comparar(): tiempo y memoria
│  │  └─ didacticos.py              clases de ejemplo de las secciones 2, 3 y 6 del notebook
│  ├─ data/_demo/                   salidas de demostración de la Formativa 3
│  └─ resultados/                   tablas de las mediciones y del pipeline
│     ├─ *_f3.csv                   notebook central (Sumativa 2), incluida
│     │                             tabla8_ejecutada_f3.csv (Tabla 8 vs. archivo real)
│     └─ tabla*.csv, tabla_proporciones.csv, arquitectura_codigo.csv
│                                   notebook de la Formativa 3
├─ F4/
│  └─ notebooks/
│     └─ Fase 4.md                  (pendiente: notebook de Fase 4)
├─ docs/                            documentación transversal al proyecto
│  ├─ bitacora_decisiones.md        registro de decisiones técnicas
│  ├─ diccionario_variables.md      diccionario de variables del dataset
│  ├─ Informe/                      informes entregados (PDF)
│  │  ├─ f1_s01_evaluacion_entregable_grupo8.pdf
│  │  ├─ f3_s02_grupo8.pdf         Formativa 3
│  │  └─ f3_s02_entregable_grupo8.pdf   Sumativa 2
│  └─ Mapa Conceptual Proyecto/
├─ .gitignore
├─ .mailmap                         unifica las identidades Git del equipo
├─ requirements.txt                 dependencias del proyecto (único, en la raíz)
└─ README.md
```

**Dónde buscar cada cosa.** La documentación específica de una fase vive dentro
de esa fase (`F1/data/docs/`, `F2/docs/`, `F3/resultados/`); `docs/` guarda lo que
cruza todo el proyecto: la bitácora de decisiones, el diccionario general, los
informes y el mapa conceptual.

**Datos oficiales y salidas de demostración.** El único conjunto procesado oficial
es `F2/data/processed/yrbs2023_seleccion_procesada.csv`. Lo que queda en
`F3/data/_demo/` son salidas de la Formativa 3 que documentan la ejecución del
notebook; no lo reemplazan y la Fase 4 no las usa.


### Módulo `src/procesamiento.py`

| Función | Parámetros | Retorna |
|---|---|---|
| `cargar_datos(ruta)` | ruta al CSV original | DataFrame 20.103 × 117 |
| `seleccionar_columnas(df)` | DataFrame completo | DataFrame 20.103 × 11 |
| `diagnosticar_datos(df)` | DataFrame | dict: nulos, duplicados, tipos |
| `clasificar_variables(df)` | DataFrame | dict: columna → rol y escala |
| `transformar_datos(df)` | DataFrame | DataFrame con ordinales categóricas |
| `validar_datos(df)` | DataFrame transformado | dict de validaciones + global |
| `guardar_dataset(df, ruta)` | DataFrame, ruta destino | Path absoluto del archivo |

## Requisitos y ejecución
Python 3.11 o superior.

```bash
python -m venv .venv
source .venv/Scripts/activate      # Windows, Git Bash
# .venv\Scripts\Activate.ps1       # Windows, PowerShell
python -m pip install -r requirements.txt
python -m ipykernel install --user --name grupo8_mcdi500 --display-name "Python (grupo8-mcdi500)"
```

Ejecutar los notebooks en orden, desde la raíz del proyecto, seleccionando el
kernel `Python (grupo8-mcdi500)`:
1. `F1/notebooks/S1_F1_Definicion.ipynb`
2. `F2/notebooks/S1_F2_Preprocesamiento.ipynb`
3. `F3/notebooks/S2_F3_NucleoAlgoritmico_POO_Grupo8.ipynb` — **notebook central de la Fase 3**

El cuaderno de la Formativa 3 (`F3/notebooks/formativa3/`) queda como registro histórico:
no es necesario ejecutarlo para reproducir la Fase 3.

### Fase 3 · Notebook central: `S2_F3_NucleoAlgoritmico_POO_Grupo8.ipynb`

**Es el entregable de la Sumativa 2 y el único notebook de F3 que se evalúa.** Se ejecuta con
*Restart Kernel and Run All Cells* (116 celdas, 54 de código, numeración continua, ≈1 minuto).
Localiza la raíz del repositorio con `encontrar_raiz()`, así que funciona desde cualquier
carpeta. **No define ninguna clase: todas las importa de `F3/src/`**, de modo que el código que
se prueba en el cuaderno es exactamente el del repositorio. La sección 17 lo comprueba: cuenta
las clases definidas en el cuaderno (0) y compara la Tabla 8 de la Formativa 3 con el archivo
real de cada componente (`F3/resultados/tabla8_ejecutada_f3.csv`).

Lee dos archivos que ya están en el repositorio y **no genera datos nuevos**:

| Entrada | Para qué |
|---|---|
| `F1/data/raw/XXH2023_YRBSS_data.csv` | archivo original del CDC: el pipeline de clases parte de aquí |
| `F2/data/processed/yrbs2023_seleccion_procesada.csv` | salida de la Fase 2: entrada del núcleo analítico y referencia para verificar |

| Sección | Qué hace | Código que usa |
|---|---|---|
| 0–10 | Configuración y conceptos (encapsulamiento, herencia, polimorfismo, cohesión, recursión, medición, patrones), con clases didácticas | `carga.py`, `didacticos.py`, `transformadores.py`, `estrategias.py`, `pipeline.py`, `fabrica.py`, `observadores.py`, `recursion.py`, `medicion.py` |
| 11 | El pipeline de F2 en 12 pasos (8 clases) armado por la fábrica | `transformadores.py`, `estrategias.py`, `fabrica.py`, `observadores.py` |
| 12 | Conteo de faltantes: bucle, `apply` y vectorizado | `transformadores.py` |
| 13 | Integración de la Formativa 3: contingencia q80 × q84 y búsqueda por id | `contingencia.py`, `analisis.py`, `busqueda.py` |
| 14 | Prevalencia por segmentos redes → sexo → edad: recursión ingenua, memoizada y `groupby` | `segmentacion.py` |
| 15 | Validación: caso normal, límites y excepciones del pipeline y del núcleo | — |
| 16 | Strategy y verificación: el pipeline reproduce el CSV de F2 carácter por carácter | `estrategias.py` |
| 17 | Arquitectura generada desde el código, Tabla 8 de la Formativa 3 ejecutada (0 clases en el cuaderno) y registro en `F3/resultados/*_f3.csv` | todos |

La comprobación central es la de la sección 16 (`pd.testing.assert_frame_equal` más
comparación del texto completo). Si esa celda falla, la reorganización alteró un resultado.

**Entorno de la ejecución versionada:** Python 3.13.15, pandas 3.0.6, NumPy 2.5.3
(`requirements.txt`). Los tiempos absolutos cambian con el equipo; lo reproducible son las
razones entre implementaciones y la forma de las curvas.

### Registro histórico: notebook de la Formativa 3

`F3/notebooks/formativa3/S2_F3_NucleoAlgoritmico_Eficiencia_POO.ipynb` es el cuaderno evaluado
en la Formativa 3 (110 celdas, 45 de código). Se conserva para trazabilidad y generó
`F3/data/_demo/` y los `tabla*.csv` de `F3/resultados/`. Su contenido quedó integrado en el
notebook central; su ejemplo de Fibonacci fue reemplazado por el cálculo propio de la
sección 14 (bitácora F3.23).

### Dos carpetas `src`: cuál usar

| Carpeta | Contiene | La usan | Estado |
|---|---|---|---|
| `src/` | `procesamiento.py`: constantes del codebook (columnas, escalas), carga del archivo original y funciones del pipeline de F2 | notebooks de F1 y F2; `F3/src/fabrica.py` la importa | **vigente** para F1–F2 y como fuente única de constantes |
| `F3/src/` | Núcleo algorítmico de F3: clases del pipeline, núcleo analítico, mediciones | notebook central de F3 | **vigente** para F3 y F4 |

No se consolidaron en una sola carpeta porque tienen propósitos distintos y consolidarlas
obligaría a modificar los notebooks de F1 y F2 ya evaluados (bitácora F3.20). La regla es
simple: **las constantes del proyecto se definen una sola vez, en `src/procesamiento.py`**, y
`F3/src/` las importa.

### Núcleo algorítmico `F3/src/`

| Módulo | Contenido | Criterio de optimización aplicado |
|---|---|---|
| `carga.py` | `leer_archivo`, `verificar_esquema`, `cargar`, `perfilar` | Valida el esquema antes de devolver datos |
| `transformadores.py` | `Transformador`, los 8 pasos del pipeline (`CLASES_PROYECTO`) y 5 pasos didácticos (`CLASES_DIDACTICAS`) | `MarcadorFaltantes` vectorizado: 16,5 veces más rápido que el bucle y 260 veces más que `apply` |
| `estrategias.py` | `ConservarFaltantes` (proyecto), `RellenarModa`, `RellenarMediana`; estrategias didácticas de imputación | Cambiar la decisión = cambiar un argumento |
| `pipeline.py` | `Pipeline`, `PipelineObservable` | Solo encadena los pasos; `_ejecutar_paso()` es el punto de extensión |
| `fabrica.py` | `construir_pipeline_proyecto` (y las constantes `RAZA`, `INDICADORES`, `VARIABLES_ANALISIS`), `crear_transformador` | Agregar un paso = una línea en la fábrica |
| `observadores.py` | `Bitacora`, `ReporteConsola` | Observer registra tiempo y parámetros de cada paso |
| `segmentacion.py` | `ArbolPrevalencia` (recursión con poda y `lru_cache`), `tabla_por_niveles_groupby` | Memoización: 4,5 veces más rápida que la recursión ingenua con 4 niveles |
| `contingencia.py`, `analisis.py` | Tabla q80 × q84 y `AnalisisContingencia` | `bincount`: ≈2.400 veces más rápido que `iterrows` |
| `busqueda.py` | Búsqueda lineal, binaria recursiva y diccionario | Diccionario: O(1) por consulta a cambio de ≈11 veces más memoria |
| `recursion.py` | `aplanar()` y los casos descartados | Recursión solo con profundidad desconocida |
| `medicion.py` | `medir()`, `comparar()`, `medir_tiempo()`, `medir_memoria()` | Exige resultados idénticos antes de medir |
| `didacticos.py` | `Preprocesador`, `ImputadorSimple`, `ProcesadorTodoEnUno`, `Cargador`, `Limpiador` | Ejemplos de las secciones 2, 3 y 6; no forman parte del pipeline |

### Sobre los valores faltantes

Los datos oficiales del proyecto **no están imputados**, y es una decisión
documentada (bitácora 2.5), no un descuido. Se verifica así:

```python
import pandas as pd
orig = pd.read_csv("F1/data/raw/XXH2023_YRBSS_data.csv", usecols=["q80", "q84"])
f2 = pd.read_csv("F2/data/processed/yrbs2023_seleccion_procesada.csv")
print(orig["q80"].isna().sum(), f2["redes_sociales_cod"].isna().sum())   # 4900 4900
print(orig["q84"].isna().sum(), f2["salud_mental_cod"].isna().sum())     # 4398 4398
```

Los nulos del archivo del CDC y los del procesado coinciden en las siete
variables de análisis. El conteo queda registrado en las columnas
`n_faltantes_analisis` y `caso_completo`, que marcan los faltantes sin
rellenarlos.

**Por qué no se imputan.** Los faltantes corresponden a no-respuesta y a saltos
de pregunta del cuestionario, así que no son aleatorios: rellenarlos con la
mediana o la moda inventaría respuestas y concentraría miles de casos en una
categoría. Además, las variables son **ordinales 1–8**; imputar un valor central
y escalar a media 0 / desviación 1 asumiría equidistancia entre categorías, que
es justamente lo que la nota metodológica de este README descarta.

### Uso de los módulos sin el cuaderno

```python
import sys; sys.path.insert(0, "F3/src")
import pandas as pd
from fabrica import construir_pipeline_proyecto
from segmentacion import ArbolPrevalencia

original = pd.read_csv("F1/data/raw/XXH2023_YRBSS_data.csv", dtype={"q6orig": "string"})
proyecto = construir_pipeline_proyecto().ajustar(original).transformar(original)

arbol = ArbolPrevalencia(proyecto, ["redes_sociales_cod", "sexo_cod"], "salud_mental_mala")
print(arbol.tabla())
```

## Contribuciones por integrante

El criterio de repositorio pide que las contribuciones sean **trazables por
integrante**. La forma de verificarlo es:

```bash
git shortlog -sne        # commits por persona
git log --oneline --author="Apellido"
```

El archivo `.mailmap` de la raíz unifica las identidades de quien commiteó con
más de un nombre de usuario sobre el mismo correo. Sin él, Git cuenta a esa
persona **como dos autores distintos** y sus commits aparecen divididos.

| Integrante | Foco de trabajo en la Fase 3 |
|---|---|
| Abigail Robles Chávez | bitácora de decisiones (F3.19–F3.25) y documentación de la fase (README) |
| Daniel Pérez Ramirez | notebook central de la Fase 3, núcleo analítico (`segmentacion.py`) y mediciones |
| Matías Manríquez Ortiz | organización de `F3/notebooks/`, paquete `F3/src/__init__.py` e informes |
| Roberto Sánchez Saldivia | núcleo POO (`transformadores.py`, `estrategias.py`, `pipeline.py`) |

El trabajo se reparte por componente, no por archivo: cada integrante toma una
parte del sistema y la documenta en la bitácora.

## Documentación (docs/)
Cada tipo de documento va en su propia subcarpeta, para no mezclar archivos:
- `docs/Mapa Conceptual Proyecto/`
- `docs/Informe/`
- `docs/Referencias/` (crear si se necesita)

## Convención de commits

Cada commit debe empezar con un prefijo que indique el **tipo de cambio**, seguido
de dos puntos y una descripción breve en presente. Lo que decide el prefijo es
**qué archivo cambia y por qué**, no si el cambio "corrige algo" o no.

### Definición de cada prefijo

| Prefijo | Úsalo cuando... | No lo uses para... |
|---|---|---|
| `docs` | subes o editas documentación: README, mapa conceptual, informe, comentarios explicativos, bitácora de decisiones | cambios en el dataset o en código ejecutable (aunque el archivo sea texto) |
| `data` | agregas, actualizas o reemplazas el dataset (archivos de datos, diccionario de variables, fuente/licencia) | limpiar o transformar el dataset dentro del código (eso es `feat` o `fix`) |
| `feat` | implementas algo nuevo: una función, un notebook, un análisis, una carpeta de fase | corregir algo que ya existía y no funcionaba (eso es `fix`) |
| `fix` | corriges un error real en el código, en la estructura de archivos o en los datos (duplicados, rutas rotas, archivos que no debían subirse) | mejorar redacción o completar información en documentación (eso es `docs`) |
| `test` | agregas o ejecutas validaciones (nulos, duplicados, rangos, tipos de dato, casos límite) | escribir la función que se está validando (eso es `feat`) |

### Ejemplos de commits

| Prefijo | Mensaje de commit | Qué cambia realmente |
|---|---|---|
| `docs` | `docs: agrega mapa conceptual v1 y v2` | se sube un archivo de documentación (imagen del mapa) |
| `docs` | `docs: actualiza README con estructura completa` | se edita texto explicativo, no código ni datos |
| `data` | `data: incorpora dataset mental_health_and_technology_usage_2024.csv` | se agrega el archivo de datos original |
| `feat` | `feat: implementa funciones de preprocesamiento` | se escribe código nuevo (funciones en `src/procesamiento.py`) |
| `feat` | `feat: crea estructura de carpetas F3 y F4` | se crea algo que no existía antes en el proyecto |
| `fix` | `fix: elimina requirements.txt duplicados en F1 y F2` | se corrige un problema real en la estructura de archivos |
| `fix` | `fix: agrega .gitignore y elimina archivos .DS_Store` | se corrige algo que no debía estar versionado |
| `test` | `test: valida nulos, duplicados y rangos del dataset procesado` | se ejecutan validaciones sobre datos ya existentes |

## Decisiones técnicas

Bitácora de decisiones tomadas durante F1–F3. Cada entrada registra la decisión
y la cifra que la respalda; este registro alimenta directamente la sección de
metodología del informe.

| # | Decisión | Evidencia |
|---|---|---|
| 1 | Eliminar `orig_rec` | 20.103/20.103 valores nulos (100 %) |
| 2 | Declarar `q6orig` como `string` | Mezcla texto (`"N N"`) y códigos numéricos; se documenta como hallazgo de calidad, no se descarta |
| 3 | Seleccionar 11 de 117 columnas por código | Acotar a las variables que responden la pregunta de investigación; selección reproducible desde el archivo original, nunca a mano |
| 4 | Clasificar `q1`, `q76`, `q80`, `q84`, `q85` como **ordinales** | Discrepancia documentada con el validador automático, que las lee como discretas por ser enteros 1–8 |
| 5 | **No ponderar** en F1–F2 | Ponderar exige análisis de encuestas complejas (varianza por conglomerados), fuera del alcance de esta etapa. Las columnas `weight`, `stratum` y `psu` se conservan para fases posteriores |
| 6 | No imputar faltantes de las variables seleccionadas | Según Apéndice C del codebook, ninguna depende de una pregunta previa: sus nulos son *no responde* genuino, no *no aplica* estructural |

Las decisiones de la Fase 3 (F3.1 a F3.26) y de infraestructura del repositorio
están en `docs/bitacora_decisiones.md`. Las más relevantes:

| # | Decisión | Evidencia |
|---|---|---|
| F3.1 | La Fase 3 no genera datos nuevos: parte del CSV de la Fase 2 | El conjunto oficial sigue siendo `F2/data/processed/yrbs2023_seleccion_procesada.csv` |
| F3.11 | Separar `ajustar` de `transformar` en cada paso | La media de `edad_cod` escalada en prueba es −0,013 y no 0: los parámetros vienen solo del entrenamiento |
| F3.13 | Armar el pipeline desde la configuración sin imputar ni escalar | 5.687 NA conservados y códigos del codebook intactos; seis controles OK |
| F3.16 | Strategy como patrón principal, aplicado a los faltantes | Rellenar con moda o mediana inventa 4.398 respuestas y desvía la distribución en 15,3 pp |
| F3.18 | El pipeline de clases debe reproducir el resultado de F2 | Archivo idéntico carácter por carácter (Sumativa 2) |
| F3.19 | Las clases del pipeline viven en `F3/src/` y el notebook las importa | La tabla de arquitectura se genera con el archivo real de cada clase |
| F3.20 | `src/` (F1–F2) y `F3/src/` (F3) conviven con propósitos distintos | Las constantes se definen una sola vez, en `src/procesamiento.py` |
| F3.21 | Un solo notebook central para la Fase 3 | El de la Formativa 3 pasa a `F3/notebooks/formativa3/` |
| F3.23 | Memoización en un cálculo propio: prevalencia por segmentos | 4 niveles: 2.187 filtros → 529; 4,5 veces más rápida que la recursión ingenua |
| F3.26 | Ejecutar completa la Tabla 8 de la Formativa 3: ninguna clase se define en el notebook | 0 clases en el cuaderno; 15 de 15 componentes en el archivo proyectado (`carga.py`, `transformadores.py`, `pipeline.py`, `fabrica.py`, `observadores.py`, `medicion.py`) |

**Limitación declarada:** al no aplicar ponderación muestral, todo resultado 
descriptivo de este proyecto describe la muestra de 20.103 estudiantes
encuestados en 2023 y **no se generaliza** a la población de estudiantes de
enseñanza media de Estados Unidos.

**Reproducibilidad:** entorno virtual `.venv` + `requirements.txt` (un solo archivo en la raíz).

## Referencias

Las referencias del proyecto en APA 7. El criterio de aspectos formales pide al
menos cinco fuentes: dos del material del curso, dos de documentación oficial de
Python o de las librerías, y una académica de los últimos cinco años. Toda
fuente listada debe estar citada en el informe o en los notebooks.

**Fuente de los datos**

- Centers for Disease Control and Prevention. (2024). *2023 Youth Risk Behavior
  Survey data* [Conjunto de datos]. https://www.cdc.gov/yrbs/data/index.html
- Centers for Disease Control and Prevention. (2024). *2023 YRBS data user's
  guide*. https://www.cdc.gov/yrbs/media/pdf/2023/2023_National_YRBS_Data_Users_Guide508.pdf

**Documentación oficial de Python y librerías**

- McKinney, W. (2022). *Python for data analysis* (3.ª ed.). O'Reilly Media.
- Python Software Foundation. (s. f.). *timeit — Measure execution time of small
  code snippets*. https://docs.python.org/3/library/timeit.html
- Python Software Foundation. (s. f.). *tracemalloc — Trace memory allocations*.
  https://docs.python.org/3/library/tracemalloc.html
- The pandas development team. (s. f.). *pandas documentation*.
  https://pandas.pydata.org/docs/

**Arquitectura de software**

- Gamma, E., Helm, R., Johnson, R., & Vlissides, J. (1994). *Design patterns:
  Elements of reusable object-oriented software*. Addison-Wesley.

**Académica complementaria (últimos cinco años)**

- Gentzler, A. L., Hughes, J. L., Johnston, M., & Alderson, J. E. (2023). Which
  social media platforms matter and for whom? Examining moderators of links
  between adolescents' social media use and depressive symptoms. *Journal of
  Adolescence, 95*(8), 1725–1748. https://doi.org/10.1002/jad.12243

**Material del curso**

- Universidad Andrés Bello. (2026). *MCDI500 Programación para la Ciencia de
  Datos: Apunte Fase 3* [Material docente]. Magíster en Ciencia de Datos e
  Inteligencia Artificial.
