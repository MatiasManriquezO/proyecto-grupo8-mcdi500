"""
changelog.py — Genera changelog.md desde el historial real de Git.

El changelog no se escribe a mano: se lee `git log` de la rama main y a cada
commit se le agrega su fase y su justificación técnica. Así cada fila enlaza
a un commit que existe (vínculo verificable) y no puede contradecir al
historial.

Uso, desde la raíz del repositorio, después de subir los commits:
    python F4/src/changelog.py

Grupo 8 · MCDI500 · Universidad Andrés Bello
"""

from __future__ import annotations

import subprocess
from pathlib import Path

REPOSITORIO = "https://github.com/MatiasManriquezO/proyecto-grupo8-mcdi500"

# Justificación de los commits históricos (hash corto -> (fase, justificación))
HISTORICOS = {
    "c7d96b5": ("F1", "Repositorio nuevo con cuentas universitarias: el anterior mezclaba identidades Gmail (retroalimentación Sumativa 1)"),
    "1749813": ("F3", "Primer avance de la Fase 3 en el repositorio nuevo"),
    "aa786eb": ("F1", "Retroalimentación Sumativa 1: el notebook F1 tenía 2 celdas de código; se agregan verificación de entorno, pruebas y trazabilidad"),
    "5f59df7": ("F2", "Retroalimentación Sumativa 1: pipeline F2 con resultados intermedios separados y rutas reales"),
    "0854f81": ("F2", "El dataset procesado declarado en el informe no estaba versionado (retroalimentación Sumativa 1)"),
    "e370ee9": ("F2", "Misma subida desde otra identidad; unificada después con .mailmap (05e7d34)"),
    "3de97bc": ("F1-F2", "Documentación de cada fase dentro de su carpeta: diccionario, registro de preprocesamiento y metadatos"),
    "9cb21b7": ("F1-F2", "Integración de cambios remotos"),
    "587116f": ("F2", "q80 es frecuencia de uso de redes, no horas: la descripción anterior inducía a interpretar mal la escala"),
    "7716529": ("F1", "Excluir checkpoints, entornos y cachés del control de versiones"),
    "b5054a8": ("F1", "El archivo se había subido como gitignore.txt y Git lo ignoraba"),
    "c35d574": ("F1", "Reglas del .gitignore corregidas"),
    "a8b9505": ("F2", "La exportación apuntaba a una ruta inexistente (../../F2/data/raw)"),
    "1feef0f": ("F1", "Notebook F1 ejecutado con el entorno del proyecto"),
    "514dd71": ("F1", "Salidas versionadas del notebook F1 (metadatos y vinculación con el mapa)"),
    "2328df8": ("F3", "Avance de la Formativa 3"),
    "d9b39ef": ("F3", "Archivos que el notebook necesitaba para ejecutarse"),
    "a7df0ec": ("F3", "Actualización de archivos del avance de F3"),
    "05e7d34": ("Repositorio", "Nueve identidades para cuatro personas (retroalimentación Sumativa 1): .mailmap las unifica"),
    "4643d65": ("F3", "Núcleo algorítmico en módulos por responsabilidad (contingencia, búsqueda, recursión, medición, análisis)"),
    "c2b137d": ("F3", "README con cómo ejecutar F3 y qué contiene cada módulo"),
    "f11df47": ("Repositorio", "Completar .mailmap con todos los correos del equipo"),
    "382d2bc": ("F3", "El árbol declarado no coincidía con el repositorio (retroalimentación Sumativa 1)"),
    "18a9f65": ("F3", "Decisiones F3.1–F3.10 con la cifra que las respalda"),
    "114c04a": ("F3", "Notebook de la Sumativa 2: pipeline de F2 reorganizado en clases"),
    "77e7fda": ("F3", "Evidencia del pipeline de clases: parámetros, bitácora y arquitectura"),
    "a6b28e8": ("F3", "Salidas de demostración separadas del dataset oficial (F3.15)"),
    "1aadb6c": ("F3", "Se eliminan salidas que imputaban y escalaban ordinales, contrarias a 2.4 y 2.5 (F3 3.8)"),
    "7bec267": ("F3", "Decisiones F3.11–F3.18 registradas"),
    "742c66f": ("F3", "Informe de la Formativa 3 versionado"),
    "af92c71": ("F3", "Actualización de F3/src con segmentacion.py (memoización, F3.23)"),
    "ce2078e": ("F3", "Notebook central que importa las clases de F3/src (retroalimentación Formativa 3)"),
    "f3a4a26": ("F3", "Tablas de eficiencia y prevalencia por segmentos del notebook central"),
    "68b025d": ("F3", "Informes organizados en docs/Informe"),
    "1d57dd4": ("F3", "Bitácora F3.19–F3.25"),
    "1505dc8": ("F3", "README declara el notebook central y las dos carpetas src (F3.20, F3.21)"),
    "cc97088": ("F3", "Actualización de documentación"),
    "7fdb2ef": ("F3", "Integración de cambios remotos"),
    "3d02c4a": ("F3", "Un solo notebook central: el de la Formativa pasa a formativa3/ (retroalimentación Formativa 3)"),
    "590fc25": ("F3", "Notebook central sin clases propias: todas se importan de F3/src (F3.26)"),
    "ff55e7a": ("F3", "README y bitácora alineados con la versión final de F3"),
    "f809a58": ("F3", "Nuevos módulos de F3 (carga, fábrica, observadores, didácticos). Borró por error 7 módulos; se restauran en F4 (F4.2)"),
    "a2535d1": ("F3", "Resultados re-medidos del notebook central"),
    "2bdfc06": ("F3", "Informe de la Sumativa 2 versionado"),
}

# Commits planificados de la Sumativa 3 (mensaje -> justificación)
FASE4 = {
    "fix: restaura modulos de src y F3/src eliminados en f809a58":
        "El notebook de F3 fallaba con ModuleNotFoundError; se restauran desde f809a58^ sin cambios (F4.2)",
    "fix: restaura modulos de src y F3/src eliminados":
        "El commit f809a58 borró 7 módulos y el notebook de F3 fallaba con ModuleNotFoundError; se restauran sin cambios (F4.2)",
    "feat: agrega dependencias de F4 a requirements.txt":
        "scipy (cuantil t), matplotlib y seaborn (figuras) y pytest (pruebas), versiones fijadas (F4.16)",
    "feat: agrega modulo de diseno muestral en F4/src/encuesta.py":
        "Estimación ponderada con linealización de Taylor; reproduce 6 cifras e IC del CDC (F4.1, F4.3)",
    "feat: agrega mediciones con timeit, figuras y verificacion en F4/src":
        "timeit y orden empírico (F4.8); cálculo separado del dibujo (F4.15); ejecución de F1-F3 en copia (F4.14)",
    "test: agrega pruebas automatizadas con pytest en tests/":
        "36 pruebas: normales, límite y excepciones de F4 y regresión de F1-F3 (F4.13)",
    "feat: agrega notebook central de la Fase 4 ejecutado":
        "Integra F1-F4, resultados ponderados, modelo, eficiencia y verificación final (11 de 11, F4.20) y codebook (F4.21); corrige en src/procesamiento.py la descripción de q80, que es de frecuencia y no de horas; ejecución continua sin errores",
    "test: agrega resultados y figuras de la Fase 4":
        "Tablas en F4/resultados y figuras en F4/figuras generadas por el notebook, citadas en el informe",
    "docs: agrega arquitectura y registro de decisiones ADR":
        "Diagramas de flujo, componentes, secuencia y datos; 5 ADR con alternativas descartadas",
    "docs: actualiza bitacora con decisiones F4.1 a F4.21":
        "Cada decisión de F4 con la cifra que la respalda",
    "docs: actualiza README con la Fase 4":
        "Instrucciones de ejecución de F4, pruebas, dependencias y estructura final",
    "docs: agrega informe final de la Sumativa 3":
        "Informe técnico versionado junto al código que describe",
    "docs: agrega changelog con commits de F1 a F4":
        "Registro trazable de fecha, commit y justificación (este archivo)",
}


def _norm(mensaje: str) -> str:
    """Compara mensajes sin distinguir mayúsculas, espacios extremos ni punto final."""
    return mensaje.strip().rstrip(".").lower()


_FASE4_NORM = {_norm(m): j for m, j in FASE4.items()}


def _git(*args, raiz: Path) -> str:
    return subprocess.run(["git", *args], cwd=raiz, capture_output=True, text=True,
                          check=True, encoding="utf-8").stdout


def leer_historial(raiz: Path, rama: str = "HEAD") -> list[dict]:
    """Commits de la rama en orden cronológico (del más antiguo al más nuevo)."""
    salida = _git("log", rama, "--reverse", "--date=short",
                  "--format=%H%x1f%h%x1f%aN%x1f%ad%x1f%s", raiz=raiz)
    commits = []
    for linea in salida.strip().splitlines():
        completo, corto, autor, fecha, mensaje = linea.split("\x1f")
        commits.append({"hash": completo, "corto": corto, "autor": autor,
                        "fecha": fecha, "mensaje": mensaje})
    return commits


def _categoria(mensaje: str) -> str:
    """Agregado / Cambiado / Corregido, según el prefijo y el verbo del commit."""
    m = _norm(mensaje)
    if m.startswith("fix"):
        return "Corregido"
    if " actualiza" in m:
        return "Cambiado"
    return "Agregado"


def seccion_fase4(commits: list[dict]) -> list[str]:
    """Bloque «## [F4] fecha» con los commits de la Fase 4 agrupados por tipo."""
    propios = [c for c in commits if _norm(c["mensaje"]) in _FASE4_NORM]
    if not propios:
        return []
    lineas = [f"## [F4] {propios[-1]['fecha']}", ""]
    for tipo in ("Corregido", "Agregado", "Cambiado"):
        grupo = [c for c in propios if _categoria(c["mensaje"]) == tipo]
        if not grupo:
            continue
        lineas += [f"### {tipo}", ""]
        for c in grupo:
            enlace = f"[`{c['corto'][:7]}`]({REPOSITORIO}/commit/{c['hash']})"
            lineas.append(f"- {c['mensaje']} (commit {enlace}, {c['autor']}). "
                          f"{_FASE4_NORM[_norm(c['mensaje'])]}.")
        lineas.append("")
    return lineas


def generar(raiz: Path | str = ".") -> str:
    raiz = Path(raiz).resolve()
    commits = leer_historial(raiz)
    filas = []
    for c in commits:
        fase, motivo = HISTORICOS.get(c["corto"][:7], (None, None))
        if fase is None:
            motivo = _FASE4_NORM.get(_norm(c["mensaje"]), "—")
            fase = "F4" if motivo != "—" else "—"
            if c["mensaje"].startswith("Merge pull request"):
                fase, motivo = "F4", "Integración de la rama de la Fase 4 a main mediante pull request revisado"
            elif c["mensaje"].startswith("Merge branch"):
                fase, motivo = "Repositorio", "Integración de cambios remotos"
        enlace = f"[`{c['corto'][:7]}`]({REPOSITORIO}/commit/{c['hash']})"
        filas.append(f"| {c['fecha']} | {fase} | {enlace} | {c['autor']} | {c['mensaje']} | {motivo} |")

    planificados = {_norm(c["mensaje"]) for c in leer_historial(raiz)}
    pendientes = [m for m in FASE4 if _norm(m) not in planificados and not m.startswith("docs: agrega changelog")
                  and not m.startswith("fix: restaura modulos")]

    texto = [
        "# Changelog — Proyecto Grupo 8, MCDI500",
        "",
        "Registro de cambios del proyecto por fecha, fase, commit y justificación técnica.",
        "Se genera desde el historial real con `python F4/src/changelog.py`: cada enlace",
        "abre el commit en GitHub. Autores unificados con `.mailmap`.",
        "",
        *seccion_fase4(commits),
        "## Historial completo (F1–F4)",
        "",
        "| Fecha | Fase | Commit | Autor | Mensaje | Justificación técnica |",
        "|---|---|---|---|---|---|",
        *filas,
        "",
        "## Síntesis del impacto de las mejoras",
        "",
        "- **Modularidad:** de 7 funciones en `src/` (F2) a un núcleo POO en `F3/src/` y una "
        "jerarquía de estimadores en `F4/src/` que hereda de F3 sin modificarlo.",
        "- **Rendimiento:** `bincount` en conteos y varianza por diseño; búsquedas O(1) con "
        "índice; memoización del árbol de segmentos; todo medido con `timeit`.",
        "- **Documentación:** bitácora con cifra por decisión, ADR, diagramas de arquitectura, "
        "pruebas automatizadas y este changelog generado desde Git.",
    ]
    if pendientes:
        texto += ["", "## Commits planificados aún no subidos", "",
                  *[f"- `{m}`" for m in pendientes]]
    return "\n".join(texto) + "\n"


if __name__ == "__main__":
    raiz = Path(__file__).resolve().parents[2]
    (raiz / "changelog.md").write_text(generar(raiz), encoding="utf-8")
    print("changelog.md actualizado:", raiz / "changelog.md")
