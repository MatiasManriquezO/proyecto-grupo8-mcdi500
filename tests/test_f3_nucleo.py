"""Pruebas de regresión del código de F1-F3 que usa la Fase 4.

Protegen lo que la Fase 4 da por cierto: que el pipeline de clases sigue
reproduciendo el conjunto de la Fase 2 y que las implementaciones
alternativas del núcleo de F3 siguen entregando el mismo resultado.
Si un commit borra o altera un módulo (como ocurrió con f809a58), estas
pruebas fallan antes de que falle el notebook.
"""

import io

import numpy as np
import pandas as pd
import pytest

import procesamiento as proc
from busqueda import buscar_binaria_rec, buscar_en_indice, buscar_lineal, construir_indice
from contingencia import contar_bincount, contar_crosstab, contar_iterrows, contar_zip, preparar_pares
from fabrica import construir_pipeline_proyecto
from recursion import aplanar
from segmentacion import ArbolPrevalencia, tabla_por_niveles_groupby

from conftest import RUTA_F2


def test_pipeline_de_clases_reproduce_el_csv_de_f2(original):
    """Integración F1 -> F3 -> F2: mismo archivo, carácter por carácter."""
    proyecto = construir_pipeline_proyecto().ajustar(original).transformar(original)
    buffer = io.StringIO()
    proyecto.to_csv(buffer, index=False, lineterminator="\n")
    with open(RUTA_F2, encoding="utf-8") as archivo:          # modo texto: \r\n -> \n
        assert archivo.read() == buffer.getvalue()


def test_validaciones_de_f2_pasan(datos_f2):
    assert datos_f2.shape == (20103, 26)
    assert datos_f2["id_registro"].is_unique
    assert int(datos_f2["caso_completo"].sum()) == 10941


def test_las_cuatro_contingencias_coinciden(datos_f2):
    pares = preparar_pares(datos_f2, "redes_sociales_cod", "salud_mental_cod")
    args = (pares, "redes_sociales_cod", "salud_mental_cod")
    referencia = contar_bincount(*args)
    assert sum(referencia.values()) == 11602
    for funcion in (contar_iterrows, contar_zip, contar_crosstab):
        assert funcion(*args) == referencia


def test_tres_busquedas_coinciden(datos_f2):
    ids = np.sort(datos_f2["id_registro"].to_numpy())
    indice = construir_indice(ids)
    for objetivo in (ids[0], ids[len(ids) // 2], ids[-1], -5):   # extremos y ausente
        esperado = buscar_lineal(ids, objetivo)
        assert buscar_binaria_rec(ids, objetivo) == esperado
        assert buscar_en_indice(indice, objetivo) == esperado


def test_arbol_recursivo_coincide_con_groupby(datos_f2):
    jerarquia = ["redes_sociales_cod", "sexo_cod", "edad_cod"]
    recursivo = ArbolPrevalencia(datos_f2, jerarquia, "salud_mental_mala").tabla()
    vectorizado = tabla_por_niveles_groupby(datos_f2, jerarquia, "salud_mental_mala")
    pd.testing.assert_frame_equal(recursivo, vectorizado, check_dtype=False)
    assert len(recursivo) == 121


def test_aplanar_estructura_anidada():
    assert aplanar({"a": {"b": {"c": 1}}, "d": 2}) == {"a.b.c": 1, "d": 2}


def test_arbol_rechaza_columna_inexistente(datos_f2):
    with pytest.raises(KeyError):
        ArbolPrevalencia(datos_f2, ["no_existe"], "salud_mental_mala")


def test_codebook_declara_las_columnas_de_analisis():
    assert len(proc.COLUMNAS_ANALISIS) == 11
