"""Pruebas de F4/src/encuesta.py: casos normales, límite y excepciones."""

import numpy as np
import pandas as pd
import pytest

from encuesta import (ArbolPrevalenciaPonderada, DisenoMuestral, PrevalenciaPonderada,
                      RegresionLogisticaPonderada)
from segmentacion import ArbolPrevalencia


# ---------------------------------------------------------------- casos normales
def test_proporcion_ponderada_calculada_a_mano(mini):
    """Σw·y / Σw = 6/9 en la encuesta mínima (la fila con NA no cuenta)."""
    tabla = PrevalenciaPonderada(DisenoMuestral(mini)).estimar(mini, "y")
    assert tabla.loc[0, "n"] == 7
    assert tabla.loc[0, "pct_ponderado"] == pytest.approx(100 * 6 / 9, abs=0.05)


def test_tres_implementaciones_de_la_varianza_coinciden(datos_f2):
    diseno = DisenoMuestral(datos_f2)
    z = np.random.default_rng(42).normal(size=len(datos_f2))
    v = diseno.varianza(z)
    assert diseno.varianza_bucle(z) == pytest.approx(v, rel=1e-10)
    assert diseno.varianza_pandas(z) == pytest.approx(v, rel=1e-10)


@pytest.mark.parametrize("indicador, sexo, esperado, ic", [
    ("salud_mental_mala", None, 28.5, (26.7, 30.4)),
    ("salud_mental_mala", 1, 38.8, (36.2, 41.4)),
    ("salud_mental_mala", 2, 18.8, (17.3, 20.5)),
    ("redes_uso_frecuente", None, 77.0, (73.5, 80.1)),
    ("redes_uso_frecuente", 1, 81.8, (77.6, 85.3)),
    ("redes_uso_frecuente", 2, 72.9, (69.8, 75.8)),
])
def test_reproduce_cifras_oficiales_del_cdc(datos_f2, indicador, sexo, esperado, ic):
    """Validación externa: Verlenden et al. (2024) y Young et al. (2024), MMWR 73(4)."""
    estimador = PrevalenciaPonderada(DisenoMuestral(datos_f2))
    tabla = estimador.estimar(datos_f2, indicador, por=None if sexo is None else "sexo_cod")
    fila = tabla.iloc[0] if sexo is None else tabla[tabla["sexo_cod"] == sexo].iloc[0]
    assert fila["pct_ponderado"] == pytest.approx(esperado, abs=0.05)
    assert (fila["ic_inf"], fila["ic_sup"]) == pytest.approx(ic, abs=0.05)


def test_regresion_recupera_coeficientes_simulados():
    """Con datos simulados de coeficientes conocidos, IRLS los recupera."""
    rng = np.random.default_rng(7)
    n = 20000
    df = pd.DataFrame({"peso_muestral": 1.0, "estrato": np.repeat([1, 2], n // 2),
                       "psu": np.tile(np.arange(50), n // 50), "x": rng.integers(0, 2, n)})
    prob = 1 / (1 + np.exp(-(-1.0 + 0.8 * df["x"])))
    df["y"] = (rng.random(n) < prob).astype(float)
    X = RegresionLogisticaPonderada.matriz_diseno(df, {}, ["x"])
    tabla = RegresionLogisticaPonderada(DisenoMuestral(df)).estimar(df, "y", X=X)
    assert tabla["coef"].to_numpy() == pytest.approx([-1.0, 0.8], abs=0.08)


def test_arbol_ponderado_conserva_la_parte_muestral_de_f3(datos_f2):
    """La subclase de F4 no altera lo que calculaba la clase de F3."""
    jerarquia = ["redes_sociales_cod", "sexo_cod"]
    f3 = ArbolPrevalencia(datos_f2, jerarquia, "salud_mental_mala").tabla()
    f4 = ArbolPrevalenciaPonderada(datos_f2, jerarquia, "salud_mental_mala",
                                   DisenoMuestral(datos_f2)).tabla()
    pd.testing.assert_frame_equal(f3, f4[f3.columns])
    assert f4.loc[0, "pct_ponderado"] == pytest.approx(28.5, abs=0.05)


# ------------------------------------------------------------------ casos límite
def test_dominio_vacio_devuelve_nan_sin_fallar(mini):
    est = PrevalenciaPonderada(DisenoMuestral(mini))
    fila = est.estimar_dominio(mini["y"].to_numpy(float), np.zeros(len(mini), bool))
    assert fila["n"] == 0 and np.isnan(fila["pct_ponderado"])


def test_proporcion_cero_tiene_intervalo_degenerado(mini):
    datos = mini.assign(y=0)
    fila = PrevalenciaPonderada(DisenoMuestral(datos)).estimar(datos, "y").iloc[0]
    assert fila["pct_ponderado"] == 0 and fila["ic_inf"] == 0 and fila["ic_sup"] == 0


def test_estimacion_por_grupo_suma_los_n(mini):
    tabla = PrevalenciaPonderada(DisenoMuestral(mini)).estimar(mini, "y", por="grupo")
    assert tabla["n"].sum() == 7


# ------------------------------------------------------------------- excepciones
def test_columnas_de_diseno_ausentes(mini):
    with pytest.raises(KeyError):
        DisenoMuestral(mini.drop(columns="psu"))


def test_pesos_no_positivos(mini):
    with pytest.raises(ValueError, match="positivos"):
        DisenoMuestral(mini.assign(peso_muestral=0.0))


def test_estrato_con_un_solo_conglomerado(mini):
    with pytest.raises(ValueError, match="un solo conglomerado"):
        DisenoMuestral(mini.assign(psu=[10, 10, 10, 10, 10, 10, 30, 30]))


def test_desenlace_que_no_es_indicador(mini):
    with pytest.raises(ValueError, match="0/1"):
        PrevalenciaPonderada(DisenoMuestral(mini)).estimar(mini.assign(y=5), "y")


def test_resumen_antes_de_estimar(mini):
    with pytest.raises(RuntimeError):
        PrevalenciaPonderada(DisenoMuestral(mini)).resumen()


def test_estimador_exige_un_diseno():
    with pytest.raises(TypeError):
        PrevalenciaPonderada("no es un diseño")


def test_dataframe_distinto_al_del_diseno(mini):
    with pytest.raises(ValueError, match="no corresponde"):
        PrevalenciaPonderada(DisenoMuestral(mini)).estimar(mini.iloc[:4], "y")
