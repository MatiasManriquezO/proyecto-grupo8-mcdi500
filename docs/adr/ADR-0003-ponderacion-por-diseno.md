# ADR-0003: Estimar con el diseño muestral (linealización de Taylor)

- **Estado:** aceptada (F4.1, F4.3)
- **Contexto:** hasta F3 las cifras describían la muestra. El YRBS es una muestra estratificada
  por conglomerados con pesos; la decisión 2.6 dejó la ponderación para las fases finales.
- **Decisión:** implementar `DisenoMuestral` con linealización de Taylor (conglomerados con
  reemplazo), dominios con z = 0 fuera de la subpoblación, IC logit con *t* de
  (conglomerados − estratos) = 73 gl. La regresión usa IRLS y varianza sándwich por diseño.
- **Validación:** se reproducen al decimal las 6 prevalencias y los 6 IC publicados por el CDC
  (Verlenden et al., 2024; Young et al., 2024).
- **Alternativas descartadas:** promedio ponderado con error de muestreo aleatorio simple
  (subestima el error estándar entre 1,8 y 4,8 veces: `deff` 3–24); `statsmodels` (no calcula
  varianza por diseño; se usó solo para contrastar coeficientes).
- **Consecuencias:** nueva dependencia `scipy` (cuantil *t*). Toda cifra de resultados es
  poblacional; las muestrales se reportan al lado para comparar con F3.
