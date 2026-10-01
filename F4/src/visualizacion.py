"""
visualizacion.py — Figuras de resultados de la Fase 4 (Matplotlib + Seaborn).

Cada función recibe una tabla ya calculada (no calcula nada), devuelve la
Figure y, si se entrega `ruta`, la guarda en PNG a 200 ppp. Separar cálculo
y dibujo permite probar los números sin abrir una ventana gráfica.

Criterios del apunte de la Fase 4 aplicados en todas las figuras:
  * Una figura responde un objetivo específico; el título enuncia el hallazgo.
  * Eje de porcentajes desde 0; categorías ordinales en su orden del codebook.
  * El tamaño de cada grupo (n) va bajo cada categoría: un porcentaje sobre
    175 estudiantes no transmite la misma certeza que uno sobre 4.587.
  * Color con función: DESTACADO donde está el hallazgo, NEUTRO para el
    contexto; el color nunca es el único canal (etiquetas y posición).
  * Valores rotulados, anotación del hallazgo y fuente al pie.
  * seaborn fija el tema; Matplotlib dibuja, rotula y anota.

Grupo 8 · MCDI500 · Universidad Andrés Bello
"""

from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")                     # sin ventana: funciona en scripts y pruebas
import matplotlib.pyplot as plt           # noqa: E402
import matplotlib.ticker                  # noqa: E402
import numpy as np                        # noqa: E402
import pandas as pd                       # noqa: E402
import seaborn as sns                     # noqa: E402

DESTACADO = "#AC212E"    # aquello sobre lo que se dirige la mirada (convención del curso)
NEUTRO = "#9FB6C8"       # el contexto
CONTRASTE = "#2F4B6E"    # serie de referencia, oscura para contrastar con DESTACADO
GRIS = "#8a8983"
TINTA, TINTA_2 = "#1a1a1a", "#52514e"
# Compatibilidad con el anexo: los nombres anteriores apuntan a la nueva paleta
AZUL, NARANJO = CONTRASTE, DESTACADO

ETIQUETAS_REDES = {
    1: "No usa", 2: "Pocas veces\nal mes", 3: "Una vez\na la semana",
    4: "Pocas veces\na la semana", 5: "Una vez\nal día", 6: "Varias veces\nal día",
    7: "Una vez\npor hora", 8: "Más de una\nvez por hora",
}
FUENTE = "Fuente: elaboración propia con YRBS 2023 (CDC, 2024)."


def _num(valor: float, decimales: int = 1) -> str:
    """Número con coma decimal y punto de miles, como en el informe."""
    texto = f"{valor:,.{decimales}f}"
    return texto.replace(",", "§").replace(".", ",").replace("§", ".")


def estilo() -> None:
    """Tema común del curso: whitegrid de seaborn y títulos en negrita."""
    sns.set_theme(context="paper", style="whitegrid", palette="deep", font="DejaVu Sans")
    plt.rcParams.update({
        "axes.edgecolor": "#c9c8c2", "grid.color": "#e6e5e0", "grid.linewidth": 0.6,
        "axes.titleweight": "bold", "axes.titlesize": 11, "axes.labelsize": 9,
        "axes.labelcolor": TINTA_2, "xtick.color": TINTA_2, "ytick.color": TINTA_2,
        "xtick.labelsize": 7, "ytick.labelsize": 8, "legend.fontsize": 8,
        "legend.frameon": False, "figure.dpi": 110, "savefig.dpi": 200,
    })


def _verificar(tabla: pd.DataFrame, columnas) -> None:
    faltan = [c for c in columnas if c not in tabla.columns]
    if faltan:
        raise KeyError(f"La tabla no tiene las columnas {faltan}.")
    if tabla.empty:
        raise ValueError("La tabla está vacía: no hay nada que graficar.")


def _cerrar(fig, titulo, subtitulo, nota, ruta):
    fig.suptitle(titulo, x=0.01, ha="left", fontsize=11.5, fontweight="bold", color=TINTA)
    fig.text(0.01, 0.905, subtitulo, ha="left", fontsize=8.5, color=TINTA_2)
    fig.text(0.01, 0.01, nota, ha="left", fontsize=7, color=TINTA_2)
    sns.despine(fig=fig, left=True)
    if ruta is not None:
        Path(ruta).parent.mkdir(parents=True, exist_ok=True)
        fig.savefig(ruta, bbox_inches="tight", facecolor="white")
    return fig


def _eje_redes(ax, niveles, n=None):
    """Etiquetas del codebook en su orden y, si se entrega, el n de cada nivel."""
    ax.set_xticks(list(niveles))
    etiquetas = [ETIQUETAS_REDES[int(v)] for v in niveles]
    if n is not None:
        etiquetas = [f"{e}\nn = {_num(k, 0)}" for e, k in zip(etiquetas, n)]
    ax.set_xticklabels(etiquetas, linespacing=1.1)
    ax.set_xlabel("Frecuencia de uso de redes sociales (q80)")


def grafico_prevalencia_redes(tabla, total: float, ruta=None):
    """Figura 1 · % con salud mental no buena por frecuencia de uso de redes (H1)."""
    _verificar(tabla, ["redes_sociales_cod", "pct_ponderado", "ic_inf", "ic_sup",
                       "pct_muestral", "n"])
    estilo()
    t = tabla.sort_values("redes_sociales_cod")
    x = t["redes_sociales_cod"].to_numpy()
    y = t["pct_ponderado"].to_numpy()
    extremos = np.isin(x, [x.min(), x.max()])
    colores = np.where(extremos, DESTACADO, CONTRASTE)
    fig, ax = plt.subplots(figsize=(8.0, 4.5))
    ax.axhline(total, color=GRIS, lw=1, ls=":", zorder=1)
    ax.text(x.max() + 0.45, total, f"Total\n{_num(total)} %", va="center",
            fontsize=7.5, color=TINTA_2)
    ax.plot(x, t["pct_muestral"], "o", ms=7, mfc="white", mec=GRIS, mew=1.4,
            zorder=2, label="Muestral, sin ponderar")
    for xi, yi, lo, hi, c in zip(x, y, t["ic_inf"], t["ic_sup"], colores):
        ax.errorbar(xi, yi, yerr=[[yi - lo], [hi - yi]], fmt="o", ms=7, color=c,
                    ecolor=c, elinewidth=1.6, capsize=3, zorder=3)
        ax.annotate(f"{_num(yi)}", (xi, yi), xytext=(9, -3), textcoords="offset points",
                    fontsize=7, color=TINTA)
    ax.plot([], [], "o", color=CONTRASTE, label="Ponderada, IC 95 %")
    razon = y[-1] / y[0]
    ax.annotate("", xy=(x.max() - 0.25, y[-1]), xytext=(x.min() + 0.25, y[0]),
                arrowprops=dict(arrowstyle="->", color=DESTACADO, lw=1.3,
                                connectionstyle="arc3,rad=-0.25"))
    ax.text(x.max() - 0.2, 41.5, f"× {_num(razon)} entre no usar redes y usarlas "
            "más de una vez por hora", ha="right", fontsize=8, color=DESTACADO,
            fontweight="bold")
    _eje_redes(ax, x, t["n"].to_numpy())
    ax.set_ylabel("Estudiantes con salud mental no buena (%)")
    ax.set_ylim(0, 45)
    ax.set_xlim(0.5, x.max() + 1.1)
    ax.legend(loc="lower right")
    fig.subplots_adjust(top=0.84, bottom=0.24)
    return _cerrar(
        fig, "La salud mental no buena se duplica entre quienes no usan redes y quienes las usan cada hora",
        "Porcentaje con salud mental no buena la mayor parte del tiempo o siempre (q84 = 4-5), "
        "por frecuencia de uso",
        FUENTE + " Estimación con pesos, estratos y conglomerados; IC 95 % en escala logit; "
        "n = estudiantes con q80 y q84 respondidas.", ruta)


def grafico_brecha_sexo(tabla, ruta=None):
    """Figura 2 · la misma relación separada por sexo, con banda de IC 95 % (H2)."""
    _verificar(tabla, ["redes_sociales_cod", "sexo_cod", "pct_ponderado", "ic_inf", "ic_sup", "n"])
    estilo()
    fig, ax = plt.subplots(figsize=(8.0, 4.5))
    series = [(2, "Masculino", CONTRASTE), (1, "Femenino", DESTACADO)]
    finales = {}
    for codigo, nombre, color in series:
        t = tabla[tabla["sexo_cod"] == codigo].sort_values("redes_sociales_cod")
        x = t["redes_sociales_cod"].to_numpy()
        ax.fill_between(x, t["ic_inf"], t["ic_sup"], color=color, alpha=0.12, lw=0)
        ax.plot(x, t["pct_ponderado"], "-o", color=color, lw=2.2, ms=6,
                mec="white", mew=1.2, label=nombre)
        ultimo = t.iloc[-1]
        finales[nombre] = (x[-1], ultimo["pct_ponderado"])
        ax.text(x[-1] + 0.18, ultimo["pct_ponderado"],
                f"{nombre}\n{_num(ultimo['pct_ponderado'])} %",
                va="center", fontsize=7.5, color=color, fontweight="bold")
    xf, yf = finales["Femenino"]
    _, ym = finales["Masculino"]
    ax.annotate("", xy=(xf, yf - 1), xytext=(xf, ym + 1),
                arrowprops=dict(arrowstyle="<->", color=TINTA_2, lw=1))
    ax.text(xf - 0.12, (yf + ym) / 2, f"brecha\n{_num(yf - ym)} pp", ha="right",
            va="center", fontsize=7.5, color=TINTA_2)
    n_nivel = tabla.groupby("redes_sociales_cod")["n"].sum()
    _eje_redes(ax, n_nivel.index.to_numpy(), n_nivel.to_numpy())
    ax.set_ylabel("Estudiantes con salud mental no buena (%)")
    ax.set_ylim(0, 60)
    ax.set_xlim(0.5, 9.3)
    ax.legend(loc="upper left", title=None)
    fig.subplots_adjust(top=0.84, bottom=0.24)
    return _cerrar(
        fig, "Con más uso de redes, la salud mental no buena sube 23 puntos en mujeres y 7 en hombres",
        "Porcentaje ponderado con salud mental no buena por uso de redes y sexo (q2); "
        "banda = IC 95 %",
        FUENTE + " n = estudiantes de ambos sexos con q80 y q84 respondidas.", ruta)


def grafico_sueno_redes(tabla, total: float, ruta=None):
    """Figura 3 · % que duerme 8 horas o más por frecuencia de uso de redes (H3)."""
    _verificar(tabla, ["redes_sociales_cod", "pct_ponderado", "ic_inf", "ic_sup", "n"])
    estilo()
    t = tabla.sort_values("redes_sociales_cod")
    x = t["redes_sociales_cod"].to_numpy()
    y = t["pct_ponderado"].to_numpy()
    fig, ax = plt.subplots(figsize=(8.0, 4.5))
    barras = ax.bar(x, y, width=0.62, color=NEUTRO, zorder=2, label="Ponderada")
    ax.errorbar(x, y, yerr=[y - t["ic_inf"], t["ic_sup"] - y], fmt="none",
                ecolor=CONTRASTE, elinewidth=1, capsize=3, zorder=3, label="IC 95 %")
    for xi, yi in zip(x, y):
        ax.text(xi, 1.2, _num(yi), ha="center", fontsize=7, color=TINTA,
                fontweight="bold", zorder=5)
    ax.axhline(total, color=DESTACADO, lw=1.2, ls="--", zorder=4)
    ax.text(x.max() + 0.45, total, f"Total\n{_num(total)} %", va="center",
            fontsize=7.5, color=DESTACADO, fontweight="bold")
    _eje_redes(ax, x, t["n"].to_numpy())
    ax.set_ylabel("Estudiantes que duermen 8 h o más (%)")
    ax.set_ylim(0, 45)
    ax.set_xlim(0.5, x.max() + 1.1)
    ax.legend(loc="upper right", bbox_to_anchor=(0.88, 1))
    fig.subplots_adjust(top=0.84, bottom=0.24)
    return _cerrar(
        fig, "En todos los niveles de uso de redes, menos de un tercio duerme 8 horas o más",
        "Porcentaje ponderado que duerme 8 horas o más en una noche escolar (q85 = 5-7); "
        "barras de error = IC 95 %",
        FUENTE + " n = estudiantes con q80 y q85 respondidas.", ruta)


def grafico_odds_ratios(tabla, n_casos: int, ruta=None):
    """Figura A1 · odds ratios ajustados (escala logarítmica, referencia = 1)."""
    _verificar(tabla, ["etiqueta", "odds_ratio", "ic_inf", "ic_sup"])
    estilo()
    t = tabla.iloc[::-1].reset_index(drop=True)
    fig, ax = plt.subplots(figsize=(8.0, 0.32 * len(t) + 1.6))
    y = np.arange(len(t))
    ax.axvline(1, color=GRIS, lw=1)
    ax.errorbar(t["odds_ratio"], y, xerr=[t["odds_ratio"] - t["ic_inf"],
                t["ic_sup"] - t["odds_ratio"]], fmt="o", color=AZUL, ms=6,
                elinewidth=1.5, capsize=2.5)
    for yi, (orr, sup) in enumerate(zip(t["odds_ratio"], t["ic_sup"])):
        ax.text(sup * 1.06, yi, f"{orr:.2f}".replace(".", ","), va="center",
                fontsize=7, color=TINTA)
    ax.set_xscale("log")
    ax.xaxis.set_minor_formatter(matplotlib.ticker.NullFormatter())
    ax.set_xticks([0.25, 0.5, 1, 2, 4])
    ax.set_xticklabels(["0,25", "0,5", "1", "2", "4"])
    ax.set_yticks(y)
    ax.set_yticklabels(t["etiqueta"])
    ax.set_xlabel("Odds ratio ajustado (escala logarítmica); IC 95 %")
    ax.grid(axis="y", visible=False)
    fig.subplots_adjust(top=0.88, left=0.3)
    return _cerrar(
        fig, "Uso de redes y salud mental no buena, ajustado por sexo, edad, sueño, "
             "actividad y raza",
        "Regresión logística ponderada por diseño; referencia: no usa redes",
        f"Fuente: elaboración propia con YRBS 2023 (CDC, 2024); {n_casos:,} casos completos.".replace(",", "."), ruta)


def grafico_crecimiento(curva, ruta=None, titulo="Tiempo según tamaño de la entrada"):
    """Figura A2 · curvas de crecimiento en escala log-log (una por implementación)."""
    _verificar(curva, ["n", "implementacion", "tiempo_min_ms"])
    estilo()
    colores = [DESTACADO, CONTRASTE, NEUTRO, GRIS]   # la adoptada, destacada
    fig, ax = plt.subplots(figsize=(8.0, 4.3))
    for color, (nombre, g) in zip(colores, curva.groupby("implementacion", sort=False)):
        g = g.sort_values("n")
        ax.plot(g["n"], g["tiempo_min_ms"], "-o", color=color, lw=2, ms=5,
                mec="white", mew=1, label=nombre)
    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_xlabel("Filas de entrada (n, escala log)")
    ax.set_ylabel("Tiempo mínimo por ejecución (ms, escala log)")
    ax.legend(loc="upper left")
    fig.subplots_adjust(top=0.84)
    return _cerrar(fig, titulo, "timeit: mínimo de 5 repeticiones; pendiente log-log = orden "
                   "empírico", "Fuente: elaboración propia (F4/resultados).", ruta)
