"""Pruebas de F4/src/rendimiento.py y F4/src/visualizacion.py."""

import numpy as np
import pandas as pd
import pytest

from rendimiento import curva_crecimiento, medir_timeit, orden_empirico
import visualizacion as vis


def test_medir_timeit_ordena_y_calcula_razon():
    datos = np.arange(10_000)
    tabla = medir_timeit({"suma_numpy": np.sum, "suma_python": sum}, datos, repeticiones=3)
    assert tabla.loc[0, "implementacion"] == "suma_numpy"
    assert tabla.loc[0, "veces_mas_lenta"] == 1.0
    assert (tabla["ejecuciones"] >= 1).all()


def test_medir_timeit_rechaza_resultados_distintos():
    with pytest.raises(ValueError, match="no coincide"):
        medir_timeit({"a": lambda: 1, "b": lambda: 2})


def test_medir_timeit_exige_tres_repeticiones():
    with pytest.raises(ValueError):
        medir_timeit({"a": lambda: 1}, repeticiones=2)


def test_orden_empirico_de_un_recorrido_lineal():
    curva = curva_crecimiento({"lineal": lambda x: sum(x)},
                              lambda n: (list(range(n)),), [20_000, 80_000, 320_000],
                              repeticiones=3)
    pendiente = orden_empirico(curva).loc[0, "pendiente_loglog"]
    assert 0.8 < pendiente < 1.2


def test_orden_empirico_necesita_dos_tamanos():
    curva = pd.DataFrame({"n": [10], "implementacion": ["a"], "tiempo_min_ms": [1.0]})
    with pytest.raises(ValueError):
        orden_empirico(curva)


def test_figura_rechaza_tabla_incompleta():
    with pytest.raises(KeyError):
        vis.grafico_sueno_redes(pd.DataFrame({"x": [1]}), total=20)


def test_figura_se_guarda(tmp_path):
    tabla = pd.DataFrame({"redes_sociales_cod": [1, 2], "pct_ponderado": [20.0, 30.0],
                          "ic_inf": [15.0, 25.0], "ic_sup": [25.0, 35.0],
                          "pct_muestral": [21.0, 31.0], "n": [300, 900]})
    ruta = tmp_path / "fig.png"
    vis.grafico_prevalencia_redes(tabla, total=25.0, ruta=ruta)
    assert ruta.exists() and ruta.stat().st_size > 10_000


def test_punto_de_cruce_interpola_en_escala_log():
    from rendimiento import punto_de_cruce
    curva = pd.DataFrame({"n": [1000, 1000, 10000, 10000],
                          "implementacion": ["vectorizada", "bucle"] * 2,
                          "tiempo_min_ms": [2.0, 1.0, 5.0, 10.0]})
    cruce = punto_de_cruce(curva, "vectorizada", "bucle")
    assert 1000 < cruce < 10000
    assert punto_de_cruce(curva.assign(tiempo_min_ms=[0.5, 1.0, 5.0, 10.0]),
                          "vectorizada", "bucle") is None
