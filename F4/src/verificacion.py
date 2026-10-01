"""
verificacion.py — Evidencia de reproducibilidad de inicio a fin.

Responde a la pregunta «¿el proyecto corre completo en otro equipo?» con
código y no con una afirmación:

  entorno_actual           versiones instaladas de las librerías declaradas.
  comparar_con_requirements  versión instalada frente a la fijada en
                           requirements.txt, librería por librería.
  ejecutar_notebooks       ejecuta los notebooks F1-F3 en una COPIA temporal
                           del repositorio (nbclient), de modo que los CSV
                           versionados no se sobrescriben; registra estado,
                           celdas de código y segundos de cada uno.
  ejecutar_pruebas         corre la batería automatizada de tests/ con pytest.

Grupo 8 · MCDI500 · Universidad Andrés Bello
"""

from __future__ import annotations

import platform
import shutil
import subprocess
import sys
import tempfile
import time
from importlib import metadata
from pathlib import Path

import pandas as pd

LIBRERIAS = ["pandas", "numpy", "scipy", "matplotlib", "seaborn",
             "jupyterlab", "ipykernel", "nbclient", "pytest"]


def entorno_actual(librerias=LIBRERIAS) -> dict:
    """Python, sistema y versión instalada de cada librería (None si falta)."""
    versiones = {}
    for nombre in librerias:
        try:
            versiones[nombre] = metadata.version(nombre)
        except metadata.PackageNotFoundError:
            versiones[nombre] = None
    en_venv = sys.prefix != sys.base_prefix or "conda" in sys.version.lower() \
        or Path(sys.prefix, "conda-meta").exists()
    return {"python": platform.python_version(), "sistema": platform.platform(terse=True),
            "entorno_aislado": en_venv, "versiones": versiones}


def leer_requirements(ruta) -> dict:
    """{librería: versión} de las líneas 'nombre==versión' de requirements.txt."""
    ruta = Path(ruta)
    if not ruta.exists():
        raise FileNotFoundError(f"No existe {ruta}.")
    fijadas = {}
    for linea in ruta.read_text(encoding="utf-8").splitlines():
        linea = linea.strip()
        if linea and not linea.startswith("#") and "==" in linea:
            nombre, version = linea.split("==", 1)
            fijadas[nombre.strip().lower().replace("_", "-")] = version.strip()
    if not fijadas:
        raise ValueError(f"{ruta} no fija ninguna versión: el entorno no es reproducible.")
    return fijadas


def comparar_con_requirements(ruta, librerias=LIBRERIAS) -> pd.DataFrame:
    """Tabla librería | fijada | instalada | coincide."""
    fijadas = leer_requirements(ruta)
    instaladas = entorno_actual(librerias)["versiones"]
    filas = [{"libreria": n, "fijada": fijadas.get(n), "instalada": instaladas[n],
              "coincide": fijadas.get(n) is not None and fijadas.get(n) == instaladas[n]}
             for n in librerias]
    return pd.DataFrame(filas)


def _copiar_repositorio(raiz: Path) -> Path:
    """Copia el repositorio (incluido .git, que los notebooks usan para ubicar la raíz)."""
    destino = Path(tempfile.mkdtemp(prefix="grupo8_verif_")) / raiz.name
    shutil.copytree(raiz, destino, ignore=shutil.ignore_patterns(
        ".venv", "__pycache__", ".ipynb_checkpoints", ".pytest_cache"))
    return destino


def ejecutar_notebooks(raiz, notebooks, tiempo_max: int = 900, kernel: str = "python3") -> pd.DataFrame:
    """Ejecuta cada notebook de principio a fin en una copia del repositorio.

    Un notebook con una celda que falla queda con estado 'ERROR' y el nombre
    de la excepción; no detiene la verificación de los demás.
    """
    import nbformat
    from nbclient import NotebookClient
    from nbclient.exceptions import CellExecutionError

    raiz = Path(raiz)
    copia = _copiar_repositorio(raiz)
    filas = []
    try:
        for relativo in notebooks:
            ruta = copia / relativo
            if not ruta.exists():
                filas.append({"notebook": relativo, "estado": "NO EXISTE",
                              "celdas_codigo": 0, "segundos": 0.0, "detalle": ""})
                continue
            nb = nbformat.read(ruta, as_version=4)
            n_codigo = sum(c.cell_type == "code" for c in nb.cells)
            cliente = NotebookClient(nb, timeout=tiempo_max, kernel_name=kernel,
                                     resources={"metadata": {"path": str(ruta.parent)}})
            inicio = time.perf_counter()
            try:
                cliente.execute()
                estado, detalle = "OK", ""
            except CellExecutionError as error:
                estado, detalle = "ERROR", str(error.ename)
            filas.append({"notebook": relativo, "estado": estado, "celdas_codigo": n_codigo,
                          "segundos": round(time.perf_counter() - inicio, 1),
                          "detalle": detalle})
    finally:
        shutil.rmtree(copia.parent, ignore_errors=True)
    return pd.DataFrame(filas)


def ejecutar_pruebas(raiz, carpeta: str = "tests") -> dict:
    """Corre pytest en la raíz y devuelve el resumen y el código de salida."""
    proceso = subprocess.run([sys.executable, "-m", "pytest", carpeta, "-q", "--no-header", "--color=no",
                              "-p", "no:cacheprovider"],
                             cwd=raiz, capture_output=True, text=True)
    lineas = [l for l in proceso.stdout.strip().splitlines() if l.strip()]
    return {"codigo_salida": proceso.returncode, "resumen": lineas[-1] if lineas else "",
            "salida": proceso.stdout}
