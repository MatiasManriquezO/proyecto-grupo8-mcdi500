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
| `q80` | `redes_sociales_cod` | Variable de exposición | Ordinal (1 = no usa … 8 = ≥6 h/día) |
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
```
proyecto-grupo8-mcdi500/
├─ src/
│  └─ procesamiento.py    	funciones: carga, selección, diagnóstico,
│                          	clasificación, transformación, validación
├─ F1/
│  ├─ data/raw/
│  │  └─ XXH2023_YRBSS_data.csv      dataset original YRBS 2023 (CDC)
│  └─ notebooks/
│     └─ S1_F1_Definicion.ipynb	Fase 1 — definición problema y 
│					entorno
├─ F2/
│  ├─ data/processed/             salida del pipeline (entrada de F3)
│  └─ notebooks/
│     └─ S1_F2_Preprocesamiento.ipynb  Fase 2 — obtención, limpieza y 
│				transformación
├─ F3/
│  └─ notebooks/
│     └─ Fase 3.md                    (pendiente: notebook de Fase 3)
├─ F4/
│  └─ notebooks/
│     └─ Fase 4.md                    (pendiente: notebook de Fase 4)
├─ docs/
│  ├─ bitacora_decisiones.md 		registro de decisiones técnicas
│  ├─ diccionario_variables.md 	diccionario de variables data set
│  ├─ Informe/
│  └─ Mapa Conceptual Proyecto/
├─ .gitignore
├─ requirements.txt     dependencias del proyecto (único, en la raíz)
└─ README.md
```

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

Bitácora de decisiones tomadas durante F1–F2. Cada entrada registra la decisión
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

**Limitación declarada:** al no aplicar ponderación muestral, todo resultado 
descriptivo de este proyecto describe la muestra de 20.103 estudiantes
encuestados en 2023 y **no se generaliza** a la población de estudiantes de
enseñanza media de Estados Unidos.

**Reproducibilidad:** entorno virtual `.venv` + `requirements.txt` (un solo archivo en la raíz).

## Referencias

- Centers for Disease Control and Prevention. (2024). *2023 Youth Risk Behavior
  Survey data* [Conjunto de datos]. https://www.cdc.gov/yrbs/data/index.html
- Centers for Disease Control and Prevention. (2024). *2023 YRBS data user's
  guide*. https://www.cdc.gov/yrbs/media/pdf/2023/2023_National_YRBS_Data_Users_Guide508.pdf
- McKinney, W. (2022). *Python for data analysis* (3.ª ed.). O'Reilly Media.
