# ADR-0005: Pruebas automatizadas y verificación de extremo a extremo

- **Estado:** aceptada (F4.13, F4.14)
- **Contexto:** el 28-09-2026 el commit `f809a58` borró 7 módulos al subir una carpeta por la
  web. El notebook de F3 dejó de ejecutarse y nadie lo detectó, porque la verificación dependía
  de ejecutar notebooks a mano.
- **Decisión:** carpeta `tests/` con `pytest` (casos normales, límite y excepciones de F4 y
  pruebas de regresión de F1–F3) y la función `ejecutar_notebooks`, que corre F1–F3 en una copia
  temporal del repositorio.
- **Alternativas descartadas:** solo `assert` dentro de los notebooks (no detectan un módulo
  borrado hasta que alguien ejecuta ese notebook); ejecutar en la carpeta real (sobrescribiría
  los CSV versionados con tiempos nuevos).
- **Consecuencias:** antes de cada subida se ejecuta `python -m pytest tests -q` (≈ 10 s).
