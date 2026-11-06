# C2 — ¿Seguir las calls de X gana dinero? Backtest en simulación · 2026-11-06

**Autor:** Claude. **Solo simulación:** no se ha comprado nada.
**Datos:** `data/callhunter/evals2.jsonl` (G6): 554 calls de 25 cuentas, 450 evaluables, 2–5 nov 2026.
Entrada = apertura del minuto siguiente al post. Precios con velas de 1 min de GeckoTerminal.
**Script:** `investigacion/backtest_calls.py` (reproducible: `python investigacion/backtest_calls.py data/callhunter/evals2.jsonl`).
**Costes:** 3 % ida y vuelta (comisión + deslizamiento, optimista) y 8 % (más realista en tokens con poca liquidez).

## Veredicto
**No. Seguir las calls pierde dinero.** La media positiva a 1 h la generan uno o dos "billetes de lotería" que en la práctica no se pueden cobrar.

## Cifras (coste 3 %)
| Estrategia | n | Media | Mediana | % que gana |
|---|---:|---:|---:|---:|
| Comprar en cada call, vender a 1 h | 450 | +9,7 % | −22 % | 21 % |
| Ídem, vender a 24 h | 151 | **−52 %** | −84 % | 12 % |
| Vender al tocar 2x en 1 h, si no a 1 h (optimista) | 450 | −18,6 % | −15 % | 30 % |
| Solo el primero que lo canta | 244 | −13,6 % | −32 % | 24 % |
| Solo con volumen alto antes de la call (≥50 k$) | 204 | −23,5 % | −72 % | 13 % |

- El +9,7 % de la primera fila depende de un solo token (×76). Sin él, la media es **−7 %**. Sin los 5 mejores, **−27 %**. Con un tope de 5x (en pools de pocos miles de $ no se puede vender más grande), **−25 %**.
- Con un coste del 8 %, todo empeora unos 4–5 puntos.
- **Por cuenta:** ninguna de las 9 cuentas con 10 o más calls tiene un resultado positivo fiable. Las mejores (Klope_1, solanabesttrade, Solprofit1) se quedan cerca de 0 % o en negativo. 0xSeerr (−42 %) y sol_lord111 (−45 %) pierden claramente.

## Origen proyecto/narrativa (G7) — primera mirada
De los 311 tokens de G7 que están en el recolector, 160 tienen precio a 15 min y a 1 h. **Ninguno duplicó en esa hora**: 153 no se movieron. En el total del recolector (1.215 tokens) solo 2 duplicaron entre el minuto 15 y la hora.
Es un solo día de datos y todavía no hay resultado a 24 h. **Aún no se puede concluir**: el análisis bueno se hará con unos 7 días (hacia el 13 de nov).
**NO COMPROBADO:** si los tokens "sin moverse" están muertos de verdad o si DexScreener deja de refrescar los que siguen en la curva de pump.fun. Gold lo va a comprobar con una muestra.

## Decisión
- Se descarta seguir calls de cuentas de X como estrategia (se cancelan G2 y G4).
- Se mantienen el recolector G8 y G3 (resultados), para buscar rasgos del minuto 0–15 que predigan supervivencia, sin calls de por medio.
