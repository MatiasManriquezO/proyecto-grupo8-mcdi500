"""
didacticos.py — Clases de ejemplo que el cuaderno usa para explicar conceptos.

No forman parte del pipeline del proyecto. Cada una ilustra un paso del
recorrido de las secciones 2, 3 y 6 del cuaderno central:

  Preprocesador        sección 2: de funciones sueltas a un objeto con estado.
  ImputadorSimple      sección 3: encapsulamiento (ajustar / transformar).
  ProcesadorTodoEnUno  sección 6.1: contraejemplo de cohesión baja.
  Cargador, Limpiador  sección 6.2: la misma tarea con cohesión alta.

Antes se definían en celdas del cuaderno; se trasladaron a este módulo para
que el cuaderno no defina ninguna clase y solo importe y use código del
repositorio (retroalimentación de la Formativa 3). El cuaderno muestra su
código con inspect.getsource, así la explicación no se pierde.

Grupo 8 · MCDI500 · Universidad Andrés Bello
"""

from __future__ import annotations

import pandas as pd


class Preprocesador:
    """Guarda la tabla del proyecto y sabe prepararla para el análisis.

    La tabla vive en self.df. Cada método es un paso del pipeline que trabaja
    sobre esa misma tabla y devuelve self, para poder encadenar.
    """

    def __init__(self, df: pd.DataFrame, columna_id: str = "id_registro"):
        self.df = df.copy()          # copia: no se modifica el original
        self.columna_id = columna_id
        self.registro = []           # lo que el objeto va recordando

    def quitar_identificador(self):
        """El id no aporta información al análisis: identifica, no describe."""
        if self.columna_id in self.df.columns:
            self.df = self.df.drop(columns=[self.columna_id])
            self.registro.append(f"{self.columna_id} eliminado")
        return self

    def imputar(self, columna):
        """Rellena los nulos de una columna con la mediana."""
        nulos = int(self.df[columna].isna().sum())
        mediana = float(self.df[columna].median())
        self.df[columna] = self.df[columna].fillna(mediana)
        self.registro.append(f"{columna}: {nulos} nulos imputados con mediana={mediana:.1f}")
        return self

    def codificar(self, columnas):
        """Convierte columnas de categorías en columnas 0/1."""
        antes = self.df.shape[1]
        self.df = pd.get_dummies(self.df, columns=columnas, dtype=int)
        self.registro.append(f"codificadas {columnas}: {antes} -> {self.df.shape[1]} columnas")
        return self

    def informe(self):
        """Devuelve lo que el objeto recuerda haber hecho."""
        return "\n".join(f"  {i}. {paso}" for i, paso in enumerate(self.registro, 1))


class ImputadorSimple:
    """Imputa una columna separando lo que aprende de lo que aplica (ejemplo didáctico)."""

    def __init__(self, columna: str = "actividad_fisica_cod"):
        self.columna = columna
        self._mediana = None        # interno: se aprende, no se asigna desde fuera
        self._ajustado = False      # interno: controla el orden de las llamadas

    @property
    def ajustado(self):
        """Solo lectura: se puede consultar, no asignar."""
        return self._ajustado

    @property
    def mediana(self):
        """Mediana aprendida en el ajuste (solo lectura)."""
        return self._mediana

    def ajustar(self, df):
        """Aprende la mediana, solo del conjunto que recibe."""
        self._mediana = float(df[self.columna].median())
        self._ajustado = True
        return self

    def transformar(self, df):
        """Aplica la mediana aprendida sobre una copia de df."""
        if not self._ajustado:
            raise RuntimeError(
                "ImputadorSimple: hay que llamar a ajustar() antes de transformar(). "
                "La mediana se aprende del conjunto de entrenamiento."
            )
        df = df.copy()
        df[self.columna] = df[self.columna].fillna(self._mediana)
        return df


class ProcesadorTodoEnUno:
    """Ejemplo de COHESIÓN BAJA: hace cuatro cosas sin relación entre sí."""

    def __init__(self, ruta):
        self.ruta = ruta
        self.df = None

    def cargar(self):            # responsabilidad 1: entrada y salida de archivos
        self.df = pd.read_csv(self.ruta)

    def limpiar(self):           # responsabilidad 2: transformar datos
        self.df = self.df.dropna()

    def graficar(self):          # responsabilidad 3: visualización
        pass

    def enviar_correo(self):     # responsabilidad 4: comunicación
        pass


class Cargador:
    """Una sola responsabilidad: leer datos desde una fuente."""

    def __init__(self, ruta):
        self.ruta = ruta

    def cargar(self):
        return pd.read_csv(self.ruta)


class Limpiador:
    """Una sola responsabilidad: transformar un DataFrame que le entregan.

    NO sabe de dónde vienen los datos. Recibe un DataFrame y
    devuelve otro. Eso es bajo acoplamiento: no depende del Cargador.
    """

    def limpiar(self, df):
        return df.dropna()
