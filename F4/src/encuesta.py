"""
encuesta.py — Estimación con el diseño muestral complejo del YRBS 2023.

Problema del proyecto: hasta la Fase 3 todas las cifras describían a los
20.103 estudiantes encuestados (bitácora 2.6). El YRBS es una muestra
estratificada por conglomerados con pesos de expansión, de modo que una
proporción sin ponderar no estima la de la población de estudiantes de
enseñanza media de EE. UU. Este módulo cierra esa decisión abierta.

Método (linealización de Taylor, conglomerados con reemplazo):

  p = sum(w * y) / sum(w)                        proporción ponderada
  z_i = w_i * (y_i - p) / sum(w)                  variable linealizada
  Z_hj = suma de z_i en el conglomerado j del estrato h
  Var(p) = sum_h  n_h / (n_h - 1) * sum_j (Z_hj - media_h(Z))^2
  IC: transformación logit y t de Student con (conglomerados - estratos)
      grados de libertad, como en los informes del CDC.

Una subpoblación (dominio) se estima poniendo z = 0 fuera del dominio, sin
eliminar filas: así se conservan todos los conglomerados y la varianza no
se subestima.

Componentes:
  DisenoMuestral              encapsula pesos, estratos y conglomerados;
                              calcula la varianza de un total linealizado
                              (versión vectorizada y versión con bucles).
  EstimadorEncuesta           clase base abstracta: todo estimador recibe un
                              DisenoMuestral y expone estimar().
  PrevalenciaPonderada        proporción ponderada por grupo, con EE, IC y
                              efecto de diseño.
  RegresionLogisticaPonderada regresión logística ponderada (IRLS) con
                              varianza sándwich por diseño; odds ratios.
  ArbolPrevalenciaPonderada   hereda de ArbolPrevalencia (F3) y agrega a cada
                              segmento la estimación ponderada.

Grupo 8 · MCDI500 · Universidad Andrés Bello
"""

from __future__ import annotations

from abc import ABC, abstractmethod

import numpy as np
import pandas as pd
from scipy import stats

from segmentacion import ArbolPrevalencia          # F3/src/segmentacion.py


# ---------------------------------------------------------------------------
# Diseño muestral
# ---------------------------------------------------------------------------
class DisenoMuestral:
    """Pesos, estratos y conglomerados (PSU) de una encuesta compleja.

    Los identificadores de PSU del YRBS se repiten entre estratos, así que el
    conglomerado se define por el par (estrato, psu): 89 conglomerados en 16
    estratos.
    """

    def __init__(self, df: pd.DataFrame, peso: str = "peso_muestral",
                 estrato: str = "estrato", psu: str = "psu"):
        faltan = [c for c in (peso, estrato, psu) if c not in df.columns]
        if faltan:
            raise KeyError(f"DisenoMuestral: faltan las columnas {faltan}.")
        if len(df) == 0:
            raise ValueError("DisenoMuestral: el DataFrame está vacío.")
        if df[[peso, estrato, psu]].isna().any().any():
            raise ValueError("DisenoMuestral: pesos, estratos y PSU no admiten NA.")

        w = df[peso].to_numpy(dtype="float64")
        if (w <= 0).any():
            raise ValueError("DisenoMuestral: todos los pesos deben ser positivos.")

        # Conglomerado = par (estrato, psu), recodificado a 0..G-1
        pares = pd.MultiIndex.from_arrays([df[estrato].to_numpy(), df[psu].to_numpy()])
        codigos, unicos = pd.factorize(pares, sort=True)
        estrato_de_cong = np.asarray(unicos.get_level_values(0))
        cod_estrato, estratos = pd.factorize(estrato_de_cong, sort=True)
        n_por_estrato = np.bincount(cod_estrato)
        if (n_por_estrato < 2).any():
            solos = list(np.asarray(estratos)[n_por_estrato < 2])
            raise ValueError(f"DisenoMuestral: estratos con un solo conglomerado {solos}; "
                             "la varianza no es estimable sin colapsar estratos.")

        self._w = w
        self._cong = codigos                        # conglomerado de cada fila
        self._estrato_cong = cod_estrato            # estrato de cada conglomerado
        self._n_h = n_por_estrato                   # conglomerados por estrato
        self.n = len(df)
        self.n_estratos = len(estratos)
        self.n_conglomerados = len(unicos)
        self.gl = self.n_conglomerados - self.n_estratos

    # -- acceso de solo lectura ------------------------------------------------
    @property
    def pesos(self) -> np.ndarray:
        return self._w.copy()          # copia: nadie modifica los pesos desde fuera

    def t_critico(self, nivel: float = 0.95) -> float:
        """Cuantil t con los grados de libertad del diseño."""
        if not 0 < nivel < 1:
            raise ValueError("nivel debe estar entre 0 y 1.")
        return float(stats.t.ppf(0.5 + nivel / 2, self.gl))

    # -- varianza de un total linealizado --------------------------------------
    def varianza(self, z: np.ndarray) -> np.ndarray:
        """Varianza por diseño del total de z (vector n o matriz n x k).

        Versión vectorizada: np.bincount suma z por conglomerado y por estrato
        en código compilado. O(n·k) en tiempo, O(G·k) en espacio.
        """
        z = np.asarray(z, dtype="float64")
        matriz = z.reshape(self.n, -1)
        k = matriz.shape[1]
        G, H = self.n_conglomerados, self.n_estratos
        totales = np.column_stack([np.bincount(self._cong, weights=matriz[:, c], minlength=G)
                                   for c in range(k)])                       # G x k
        suma_h = np.column_stack([np.bincount(self._estrato_cong, weights=totales[:, c],
                                              minlength=H) for c in range(k)])  # H x k
        media_h = suma_h / self._n_h[:, None]
        desvio = totales - media_h[self._estrato_cong]                         # G x k
        factor = (self._n_h / (self._n_h - 1))[self._estrato_cong]
        v = (desvio * factor[:, None]).T @ desvio                              # k x k
        return v[0, 0] if z.ndim == 1 else v

    def varianza_bucle(self, z: np.ndarray) -> float:
        """Misma fórmula con bucles de Python (implementación de referencia).

        Sirve para verificar la versión vectorizada y para medirla: recorre
        fila por fila para acumular los totales. O(n) con constante alta.
        """
        z = np.asarray(z, dtype="float64")
        if z.ndim != 1:
            raise ValueError("varianza_bucle acepta solo un vector.")
        totales = {}
        for fila in range(self.n):
            g = int(self._cong[fila])
            totales[g] = totales.get(g, 0.0) + float(z[fila])
        por_estrato = {}
        for g, total in totales.items():
            por_estrato.setdefault(int(self._estrato_cong[g]), []).append(total)
        v = 0.0
        for valores in por_estrato.values():
            n_h = len(valores)
            media = sum(valores) / n_h
            v += n_h / (n_h - 1) * sum((t - media) ** 2 for t in valores)
        return v

    def varianza_pandas(self, z: np.ndarray) -> float:
        """Misma fórmula con groupby de pandas (alternativa idiomática)."""
        z = np.asarray(z, dtype="float64")
        totales = pd.Series(z).groupby(self._cong).sum()
        estrato = pd.Series(self._estrato_cong[totales.index], index=totales.index)
        grupos = totales.groupby(estrato)
        n_h = grupos.transform("size")
        desvio = totales - grupos.transform("mean")
        return float((n_h / (n_h - 1) * desvio ** 2).sum())

    def __repr__(self):
        return (f"DisenoMuestral(n={self.n}, estratos={self.n_estratos}, "
                f"conglomerados={self.n_conglomerados}, gl={self.gl})")


def _ic_logit(p: float, ee: float, t: float) -> tuple:
    """IC de una proporción en escala logit (queda dentro de [0, 1])."""
    if ee == 0 or p <= 0 or p >= 1:
        return p, p
    logit = np.log(p / (1 - p))
    ee_logit = ee / (p * (1 - p))
    inf, sup = logit - t * ee_logit, logit + t * ee_logit
    return 1 / (1 + np.exp(-inf)), 1 / (1 + np.exp(-sup))


# ---------------------------------------------------------------------------
# Estimadores
# ---------------------------------------------------------------------------
class EstimadorEncuesta(ABC):
    """Base de todo estimador por diseño: recibe el diseño y expone estimar().

    Las subclases solo implementan estimar(); resumen() y el control del
    orden de llamadas quedan aquí (plantilla común, polimorfismo).
    """

    def __init__(self, diseno: DisenoMuestral, nivel: float = 0.95):
        if not isinstance(diseno, DisenoMuestral):
            raise TypeError("El estimador requiere un DisenoMuestral.")
        self._diseno = diseno
        self.nivel = nivel
        self._resultado: pd.DataFrame | None = None

    @property
    def diseno(self) -> DisenoMuestral:
        return self._diseno

    @abstractmethod
    def estimar(self, df: pd.DataFrame, desenlace: str, **opciones) -> pd.DataFrame:
        """Calcula la estimación y la devuelve como DataFrame."""

    def resumen(self) -> pd.DataFrame:
        if self._resultado is None:
            raise RuntimeError(f"{type(self).__name__}: llame a estimar() antes de resumen().")
        return self._resultado.copy()

    def _verificar(self, df: pd.DataFrame, columnas) -> None:
        if len(df) != self._diseno.n:
            raise ValueError("El DataFrame no corresponde al diseño (distinto n° de filas).")
        faltan = [c for c in columnas if c not in df.columns]
        if faltan:
            raise KeyError(f"{type(self).__name__}: no existen las columnas {faltan}.")


class PrevalenciaPonderada(EstimadorEncuesta):
    """Proporción ponderada de un indicador 0/1, total o por grupos."""

    def estimar_dominio(self, y: np.ndarray, dominio: np.ndarray | None = None) -> dict:
        """Estimación para un dominio (máscara booleana) sobre y con NA."""
        d = self._diseno
        valido = ~np.isnan(y)
        if dominio is not None:
            valido &= dominio
        n = int(valido.sum())
        if n == 0:
            return {"n": 0, "positivos": 0, "pct_muestral": np.nan, "pct_ponderado": np.nan,
                    "ee": np.nan, "ic_inf": np.nan, "ic_sup": np.nan, "deff": np.nan}
        w = np.where(valido, d._w, 0.0)
        yv = np.where(valido, y, 0.0)
        W = w.sum()
        p = float((w * yv).sum() / W)
        z = w * (yv - p) / W                      # cero fuera del dominio
        ee = float(np.sqrt(d.varianza(z)))
        inf, sup = _ic_logit(p, ee, d.t_critico(self.nivel))
        p_srs = yv[valido].mean()
        var_srs = p * (1 - p) / n
        return {"n": n, "positivos": int(yv[valido].sum()),
                "pct_muestral": 100 * p_srs, "pct_ponderado": 100 * p,
                "ee": 100 * ee, "ic_inf": 100 * inf, "ic_sup": 100 * sup,
                "deff": ee ** 2 / var_srs if var_srs > 0 else np.nan}

    def estimar(self, df, desenlace, por=None, **opciones) -> pd.DataFrame:
        """Una fila para el total (por=None) o una por combinación de grupos."""
        grupos = [] if por is None else ([por] if isinstance(por, str) else list(por))
        self._verificar(df, [desenlace, *grupos])
        y = pd.to_numeric(df[desenlace].astype("object"), errors="coerce").to_numpy(float)
        valores_y = set(np.unique(y[~np.isnan(y)]))
        if not valores_y <= {0.0, 1.0}:
            raise ValueError(f"'{desenlace}' debe ser un indicador 0/1; tiene {sorted(valores_y)}.")

        if not grupos:
            filas = [{**self.estimar_dominio(y)}]
        else:
            claves = df[grupos].astype("object").apply(pd.to_numeric, errors="coerce")
            combinaciones = claves.dropna().drop_duplicates().sort_values(grupos)
            filas = []
            for combinacion in combinaciones.itertuples(index=False):
                dominio = np.ones(len(df), dtype=bool)
                for columna, valor in zip(grupos, combinacion):
                    dominio &= (claves[columna] == valor).to_numpy()
                filas.append({**dict(zip(grupos, map(int, combinacion))),
                              **self.estimar_dominio(y, dominio)})
        tabla = pd.DataFrame(filas)
        redondeo = {"pct_muestral": 1, "pct_ponderado": 1, "ee": 2,
                    "ic_inf": 1, "ic_sup": 1, "deff": 2}
        self._resultado = tabla.round(redondeo)
        return self.resumen()


class RegresionLogisticaPonderada(EstimadorEncuesta):
    """Regresión logística ponderada con errores estándar por diseño.

    Coeficientes: Newton-Raphson / IRLS sobre la verosimilitud ponderada.
    Varianza: sándwich H^-1 G H^-1, donde G es la varianza por diseño de los
    aportes al score (mismo método que svyglm en R).
    """

    def __init__(self, diseno, nivel=0.95, max_iter: int = 50, tolerancia: float = 1e-10):
        super().__init__(diseno, nivel)
        self.max_iter = max_iter
        self.tolerancia = tolerancia
        self.coeficientes_: pd.Series | None = None
        self.iteraciones_ = 0

    @staticmethod
    def matriz_diseno(df, categoricas: dict, numericas=()) -> pd.DataFrame:
        """Intercepto + indicadores de cada categoría (menos la referencia) + numéricas.

        Filas con algún NA quedan como NA en toda la fila (análisis de casos
        completos, sin imputar: bitácora 2.5).
        """
        partes = [pd.Series(1.0, index=df.index, name="intercepto")]
        for columna, referencia in categoricas.items():
            valores = pd.to_numeric(df[columna].astype("object"), errors="coerce")
            for nivel in sorted(v for v in valores.dropna().unique() if v != referencia):
                partes.append(((valores == nivel).astype("float64")
                               .where(valores.notna())).rename(f"{columna}={int(nivel)}"))
        for columna in numericas:
            partes.append(pd.to_numeric(df[columna].astype("object"), errors="coerce")
                          .astype("float64").rename(columna))
        X = pd.concat(partes, axis=1)
        X.loc[X.isna().any(axis=1)] = np.nan
        return X

    def estimar(self, df, desenlace, X: pd.DataFrame | None = None, **opciones):
        if X is None:
            raise ValueError("Entregue la matriz X (use matriz_diseno).")
        self._verificar(df, [desenlace])
        y = pd.to_numeric(df[desenlace].astype("object"), errors="coerce").to_numpy(float)
        Xv = X.to_numpy(dtype="float64")
        usar = ~np.isnan(y) & ~np.isnan(Xv).any(axis=1)
        if usar.sum() <= Xv.shape[1]:
            raise ValueError("Muy pocas filas completas para estimar el modelo.")

        w = np.where(usar, self._diseno._w, 0.0)
        Xc, yc = np.where(usar[:, None], Xv, 0.0), np.where(usar, y, 0.0)
        beta = np.zeros(Xv.shape[1])
        for iteracion in range(1, self.max_iter + 1):
            mu = 1 / (1 + np.exp(-(Xc @ beta)))
            H = (Xc * (w * mu * (1 - mu))[:, None]).T @ Xc           # información
            paso = np.linalg.solve(H, Xc.T @ (w * (yc - mu)))       # score
            beta = beta + paso
            if np.max(np.abs(paso)) < self.tolerancia:
                break
        else:
            raise RuntimeError("IRLS no convergió; revise separación o colinealidad.")
        self.iteraciones_ = iteracion

        mu = 1 / (1 + np.exp(-(Xc @ beta)))
        H = (Xc * (w * mu * (1 - mu))[:, None]).T @ Xc
        aportes = Xc * (w * (yc - mu))[:, None]                     # n x k, 0 fuera
        H_inv = np.linalg.inv(H)
        V = H_inv @ self._diseno.varianza(aportes) @ H_inv
        ee = np.sqrt(np.diag(V))
        t = self._diseno.t_critico(self.nivel)
        tabla = pd.DataFrame({
            "termino": X.columns, "coef": beta, "ee": ee,
            "odds_ratio": np.exp(beta),
            "ic_inf": np.exp(beta - t * ee), "ic_sup": np.exp(beta + t * ee),
            "p_valor": 2 * stats.t.sf(np.abs(beta / ee), self._diseno.gl),
        })
        self.n_usadas_ = int(usar.sum())
        self.coeficientes_ = pd.Series(beta, index=X.columns)
        self._resultado = tabla.round({"coef": 4, "ee": 4, "odds_ratio": 2,
                                       "ic_inf": 2, "ic_sup": 2, "p_valor": 4})
        return self.resumen()


# ---------------------------------------------------------------------------
# Extensión del árbol recursivo de la Fase 3
# ---------------------------------------------------------------------------
class ArbolPrevalenciaPonderada(ArbolPrevalencia):
    """ArbolPrevalencia (F3) + estimación ponderada en cada segmento.

    No reescribe la recursión: hereda explorar() y la memoización de F3 y
    solo redefine estadisticas(), que explorar() llama en cada nodo.
    """

    def __init__(self, df, jerarquia, desenlace, diseno: DisenoMuestral,
                 n_minimo: int = 30, memoizar: bool = True, nivel: float = 0.95):
        super().__init__(df, jerarquia, desenlace, n_minimo=n_minimo, memoizar=memoizar)
        if diseno.n != len(df):
            raise ValueError("El diseño no corresponde al DataFrame.")
        self._estimador = PrevalenciaPonderada(diseno, nivel)
        # Posición en el DataFrame completo de cada fila de la base del árbol
        self._fila_original = np.flatnonzero(df[desenlace].notna().to_numpy())
        self._y_completo = pd.to_numeric(df[desenlace].astype("object"),
                                         errors="coerce").to_numpy(float)

    def estadisticas(self, filtros: tuple = ()) -> dict:
        fila = super().estadisticas(filtros)                  # n, positivos, pct (F3)
        dominio = np.zeros(len(self._y_completo), dtype=bool)
        dominio[self._fila_original[self._subconjunto(tuple(filtros))]] = True
        est = self._estimador.estimar_dominio(self._y_completo, dominio)
        fila.update({"pct_ponderado": round(est["pct_ponderado"], 1),
                     "ic_inf": round(est["ic_inf"], 1), "ic_sup": round(est["ic_sup"], 1)})
        return fila
