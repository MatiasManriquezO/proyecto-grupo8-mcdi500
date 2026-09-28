"""
transformadores.py — Clase base Transformador y los pasos del pipeline de F2.

Cada paso del notebook de la Fase 2 es aquí una clase hija de Transformador.
La base define el contrato (ajustar / transformar) y controla el estado; las
hijas solo implementan lo que cambia: qué aprenden (aprender) y cómo lo
aplican (aplicar).

Principios que se aplican:
  Encapsulamiento : _parametros y _ajustado son internos; nombre y parametros
                    son propiedades de solo lectura; transformar() falla si
                    no se llamó antes a ajustar().
  Herencia        : las ocho clases del proyecto heredan el control de estado,
                    la validación de columnas y la copia defensiva.
  Polimorfismo    : el Pipeline llama ajustar/transformar sin preguntar el
                    tipo; las hijas que trabajan con varias columnas
                    redefinen columnas_requeridas().

Grupo 8 · MCDI500 · Universidad Andrés Bello
"""

from __future__ import annotations

import numpy as np
import pandas as pd

try:                                    # importado como paquete (F3.src)
    from .estrategias import ConservarFaltantes, EstrategiaFaltantes
except ImportError:                     # importado con F3/src en sys.path
    from estrategias import ConservarFaltantes, EstrategiaFaltantes


# ══════════════════════════════════════════════════════════════
# CLASE BASE
# ══════════════════════════════════════════════════════════════

class Transformador:
    """Clase base: define el contrato y controla el estado de cada paso.

    No se usa directamente. Las clases hijas implementan aprender() y
    aplicar(); la base decide CUÁNDO se llaman y valida la entrada.
    """

    def __init__(self, columna: str):
        self.columna = columna          # público: qué columna trabaja el paso
        self._parametros: dict = {}     # interno: lo que el paso aprende
        self._ajustado = False          # interno: impide transformar sin ajustar

    @property
    def nombre(self) -> str:
        """Nombre de la clase REAL del objeto y su columna (solo lectura)."""
        return f"{type(self).__name__}({self.columna})"

    @property
    def parametros(self) -> dict:
        """Copia de lo aprendido: quien la recibe no puede alterar el estado."""
        return dict(self._parametros)

    @property
    def ajustado(self) -> bool:
        """Indica si el paso ya aprendió sus parámetros (solo lectura)."""
        return self._ajustado

    def columnas_requeridas(self) -> list:
        """Columnas que el paso necesita. Por defecto, solo la suya."""
        return [self.columna]

    def ajustar(self, df: pd.DataFrame) -> "Transformador":
        """Valida la entrada, aprende los parámetros y devuelve self."""
        faltan = [c for c in self.columnas_requeridas() if c not in df.columns]
        if faltan:                                  # validar antes de trabajar
            raise KeyError(f"{self.nombre}: no existen las columnas {faltan}.")
        self._parametros = self.aprender(df)        # delega en la clase hija
        self._ajustado = True
        return self                                 # permite encadenar

    def transformar(self, df: pd.DataFrame) -> pd.DataFrame:
        """Aplica lo aprendido sobre una copia; nunca modifica la entrada."""
        if not self._ajustado:
            raise RuntimeError(f"{self.nombre}: hay que ajustar antes de transformar.")
        return self.aplicar(df.copy())              # copia defensiva

    def ajustar_transformar(self, df: pd.DataFrame) -> pd.DataFrame:
        """Atajo: aprender y aplicar sobre el mismo conjunto."""
        return self.ajustar(df).transformar(df)

    # ---- Contrato que cada clase hija DEBE cumplir -------------------------
    def aprender(self, df: pd.DataFrame) -> dict:
        """Calcula y devuelve los parámetros. Lo implementa cada clase hija."""
        raise NotImplementedError("Cada clase hija debe implementar aprender().")

    def aplicar(self, df: pd.DataFrame) -> pd.DataFrame:
        """Aplica la transformación. Lo implementa cada clase hija."""
        raise NotImplementedError("Cada clase hija debe implementar aplicar().")

    def __repr__(self) -> str:
        estado = "ajustado" if self._ajustado else "sin ajustar"
        return f"<{self.nombre}, {estado}>"


# ══════════════════════════════════════════════════════════════
# PASOS DEL PIPELINE DE LA FASE 2 (en el orden en que se aplican)
# ══════════════════════════════════════════════════════════════

class EliminadorColumnaVacia(Transformador):
    """Elimina una columna solo si está 100 % vacía (bitácora 2.1).

    Si la columna tiene aunque sea un dato, el paso se niega a borrarla y
    avisa: un cambio en el archivo original no pasa inadvertido.
    """

    def aprender(self, df):
        pct = float(df[self.columna].isna().mean() * 100)
        if pct < 100:
            raise ValueError(f"{self.nombre}: la columna tiene datos "
                             f"({pct:.1f} % nulos); no se elimina.")
        return {"pct_nulos": pct}

    def aplicar(self, df):
        return df.drop(columns=[self.columna])


class SeleccionadorColumnas(Transformador):
    """Selecciona y renombra las columnas de análisis (bitácora 2.3)."""

    def __init__(self, mapa: dict):
        super().__init__("columnas de análisis")
        self.mapa = dict(mapa)                      # original -> nombre del proyecto

    def columnas_requeridas(self):                  # redefine el de la base
        return list(self.mapa)

    def aprender(self, df):
        # El identificador debe ser único antes de confiar en él
        if not df["record"].is_unique:
            raise ValueError(f"{self.nombre}: 'record' tiene valores repetidos.")
        return {"columnas_entrada": df.shape[1], "columnas_salida": len(self.mapa)}

    def aplicar(self, df):
        return df[list(self.mapa)].rename(columns=self.mapa)


class MarcadorFaltantes(Transformador):
    """Agrega la bandera de faltantes: cuántas variables faltan y si el caso está completo."""

    def __init__(self, columnas):
        super().__init__("bandera de faltantes")
        self.columnas = list(columnas)

    def columnas_requeridas(self):
        return self.columnas

    def aprender(self, df):
        completos = int(df[self.columnas].notna().all(axis=1).sum())
        return {"variables": len(self.columnas), "casos_completos": completos}

    def aplicar(self, df):
        # Versión vectorizada: la que ganó la medición (notebook, sección 12)
        df["n_faltantes_analisis"] = df[self.columnas].isna().sum(axis=1).astype("int8")
        df["caso_completo"] = (df["n_faltantes_analisis"] == 0).astype("int8")
        return df


class TratamientoFaltantes(Transformador):
    """No sabe tratar faltantes: sabe cuándo hacerlo. El cómo lo aporta la estrategia."""

    def __init__(self, columnas, estrategia: EstrategiaFaltantes | None = None):
        super().__init__("faltantes")
        self.columnas = list(columnas)
        self.estrategia = estrategia or ConservarFaltantes()
        if not isinstance(self.estrategia, EstrategiaFaltantes):
            raise TypeError("La estrategia debe heredar de EstrategiaFaltantes.")

    def columnas_requeridas(self):
        return self.columnas

    def aprender(self, df):
        return {"estrategia": self.estrategia.etiqueta,
                "nulos_antes": int(df[self.columnas].isna().sum().sum())}

    def aplicar(self, df):
        for columna in self.columnas:
            df[columna] = self.estrategia.tratar(df[columna])   # polimorfismo
        return df


class CastearCodigos(Transformador):
    """Convierte códigos float64 a entero Int64, conservando los faltantes (bitácora 2.4)."""

    def __init__(self, columnas):
        super().__init__("códigos a Int64")
        self.columnas = list(columnas)

    def columnas_requeridas(self):
        return self.columnas

    def aprender(self, df):
        # Un código 2.5 no existe en el codebook: se detiene antes de convertir
        for columna in self.columnas:
            valores = df[columna].dropna()
            no_enteros = valores[valores != np.floor(valores)]
            if len(no_enteros):
                raise ValueError(f"{self.nombre}: '{columna}' tiene valores no enteros, "
                                 f"p. ej. {no_enteros.iloc[0]}")
        return {"columnas": len(self.columnas)}

    def aplicar(self, df):
        for columna in self.columnas:
            df[columna] = df[columna].astype("Int64")
        return df


class ConversorOrdinal(Transformador):
    """Declara el orden de las escalas ordinales con el orden del codebook."""

    def __init__(self, escalas: dict):
        super().__init__("escalas ordinales")
        self.escalas = {c: list(v) for c, v in escalas.items()}

    def columnas_requeridas(self):
        return list(self.escalas)

    def aprender(self, df):
        return {"escalas": {c: len(v) for c, v in self.escalas.items()}}

    def aplicar(self, df):
        for columna, categorias in self.escalas.items():
            df[columna] = pd.Categorical(df[columna], categories=categorias, ordered=True)
        return df


class CodificadorOneHot(Transformador):
    """Codifica una nominal en columnas 0/1 con nombres declarados; <NA> donde falta.

    Conserva la columna original (trazabilidad) y no convierte un faltante en 0.
    Un código que no está declarado en el codebook detiene el proceso.
    """

    def __init__(self, columna: str, nombres: dict):
        super().__init__(columna)
        self.nombres = dict(nombres)          # código -> nombre de la columna nueva

    def aprender(self, df):
        observados = set(df[self.columna].dropna().astype(int).unique())
        no_declarados = observados - set(self.nombres)
        if no_declarados:
            raise ValueError(f"{self.nombre}: códigos no declarados "
                             f"{sorted(int(c) for c in no_declarados)}")
        return {"columnas_nuevas": list(self.nombres.values())}

    def aplicar(self, df):
        falta = df[self.columna].isna()
        for codigo, nombre in self.nombres.items():
            nueva = (df[self.columna] == codigo).astype("Int8")
            nueva[falta] = pd.NA
            df[nombre] = nueva
        return df


class IndicadorBinario(Transformador):
    """Crea una columna 0/1 que vale 1 si el código está en los valores positivos.

    Conserva <NA> donde el original falta: no convierte un faltante en 0.
    """

    def __init__(self, columna: str, valores_positivos, nuevo_nombre: str):
        super().__init__(columna)
        # Se valida al construir: un indicador sin valores positivos no tiene sentido
        if not valores_positivos:
            raise ValueError("valores_positivos no puede estar vacío.")
        self.valores_positivos = list(valores_positivos)
        self.nuevo_nombre = nuevo_nombre

    def _codigos(self, df):
        # Método interno: convierte a número aunque la columna sea Categorical
        return pd.to_numeric(df[self.columna].astype("object"), errors="coerce")

    def aprender(self, df):
        codigos = self._codigos(df)
        con_dato = codigos.notna()
        pct = float(codigos[con_dato].isin(self.valores_positivos).mean() * 100)
        return {"positivos": self.valores_positivos, "pct_positivos": round(pct, 1)}

    def aplicar(self, df):
        codigos = self._codigos(df)
        indicador = codigos.isin(self.valores_positivos).astype("Int8")
        indicador[codigos.isna()] = pd.NA
        df[self.nuevo_nombre] = indicador
        return df


# Clases que forman el pipeline real del proyecto (las demás subclases de
# Transformador que se definan en el notebook son didácticas)
CLASES_PROYECTO = (EliminadorColumnaVacia, SeleccionadorColumnas, MarcadorFaltantes,
                   TratamientoFaltantes, CastearCodigos, ConversorOrdinal,
                   CodificadorOneHot, IndicadorBinario)
