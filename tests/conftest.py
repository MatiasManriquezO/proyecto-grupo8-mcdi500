"""Configuración común de las pruebas: rutas del proyecto y datos compartidos.

Ejecutar desde la raíz del repositorio:  python -m pytest tests -q
"""

import sys
from pathlib import Path

import pandas as pd
import pytest

RAIZ = Path(__file__).resolve().parents[1]
for carpeta in ("src", "F3/src", "F4/src"):
    sys.path.insert(0, str(RAIZ / carpeta))

RUTA_F2 = RAIZ / "F2" / "data" / "processed" / "yrbs2023_seleccion_procesada.csv"
RUTA_ORIGINAL = RAIZ / "F1" / "data" / "raw" / "XXH2023_YRBSS_data.csv"


@pytest.fixture(scope="session")
def datos_f2():
    """Conjunto oficial del proyecto (salida de la Fase 2)."""
    return pd.read_csv(RUTA_F2)


@pytest.fixture(scope="session")
def original():
    """Archivo original del CDC, como lo lee la Fase 2."""
    return pd.read_csv(RUTA_ORIGINAL, dtype={"q6orig": "string"})


@pytest.fixture
def mini():
    """Encuesta mínima inventada: 2 estratos x 2 conglomerados, 8 filas.

    Permite calcular a mano el resultado esperado.
    """
    return pd.DataFrame({
        "peso_muestral": [1.0, 1.0, 2.0, 2.0, 1.0, 1.0, 1.0, 1.0],
        "estrato":       [1, 1, 1, 1, 2, 2, 2, 2],
        "psu":           [10, 10, 20, 20, 10, 10, 30, 30],
        "y":             [1, 0, 1, 1, 0, 0, 1, None],
        "grupo":         [1, 1, 1, 2, 2, 2, 2, 2],
    })
