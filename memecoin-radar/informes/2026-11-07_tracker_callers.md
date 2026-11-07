# Tracker de callers de X (Ben y otros): ¿se gana entrando en la call y saliendo a X minutos? · 2026-11-07

**Autor:** Claude. **Solo simulación.**
**Datos:** las calls que recogió Grok Bot (`data/callhunter/calls.jsonl`): 548 calls (primer post de cada cuenta con cada token), 26 cuentas, 307 tokens, del 2 al 5 de nov. 541 tienen precios.
**Precios:** GeckoTerminal, velas de 1 min (curva de pump.fun + pool tras graduarse) y velas de 15 min para la ventana de 24 h.
**Reglas probadas:**
- entrar 0, 1, 2 o 5 min después del tuit;
- salir a 5, 15, 30 o 60 min, a 4 h o a 24 h;
- o salir con take-profit / stop-loss (×1,2/×0,9 en 15 min; ×1,3/×0,8 en 30 min; ×1,5/×0,7 y ×2/×0,6 en 60 min).

Coste: 5 % ida y vuelta. Una combinación cuenta como "ganadora" solo si gana en las DOS mitades por separado (2–3 nov y 4–5 nov) con al menos 8 calls en cada una.
**Scripts:** `investigacion/velas_calls.py`, `investigacion/analisis_callers.py`.

## Resultado
**Ninguna combinación de cuenta + ventana + retraso gana en las dos mitades. 0 de cientos probadas.**

- **Ben (@Crypt_bencall1x), 32 calls:** entrando en el tuit y saliendo a los 15 min, la media es +26 %. Pero solo ganan 7 de 32 (22 %) y la mediana es −25 %. Toda la media sale de un token del 3 nov a las 21:43 que hizo ×18 en 15 min. Sin ese token, la media es −29 %. El 2–3 nov da +300 %; el 4–5 nov da −25 %. Es una lotería, no un patrón.
- **Las cuentas más activas:** con su mejor ventana (casi siempre 5 min), APE_ORACLE1 queda en −1 % (gana el 30 %), sol_lord111 en −1 %, DegenFlow_ en −6 %, Solprofit1 en −6 % y 0xSeerr en −15 %.
- **Comprar solo lo que una cuenta publica primero:** −3 % de media, gana el 32 %.
- **Take-profit / stop-loss:** las mejores reglas quedan entre −3 % y 0 %.

## La "matriz" (quién publica primero y quién copia)
- Los que más veces publican primero un token que luego publican otros: APE_ORACLE1 (23), DegenFlow_ (20), 0xSeerr (17), sol_lord111 (11), Ben (7).
- Cadenas que se repiten (A publica, B lo repite; veces; minutos de retraso típicos):
  - DegenFlow_ → Solprofit1: 14 veces, ~64 min.
  - Solprofit1 → solanabesttrade: 13 veces, ~10 min.
  - DegenFlow_ → itsmeflow18: 11 veces, ~18 min.
  - 0xSeerr → APE_ORACLE1: 9 veces, ~7 min.
  - APE_ORACLE1 → sol_lord111: 9 veces, ~10 min.
  - APE_ORACLE1 → Ben: 7 veces, ~44 min.
- Ben publica primero en 23 de sus 32 tokens dentro de este grupo, pero algunos los repite de APE_ORACLE1 unos 44 min después.
- Las calls llegan de media 46 min después de que el token empieza a cotizar. En la media hora previa el precio ya ha subido un 7 % (mediana).

## Límites
- Solo 3–4 días y entre 7 y 78 calls por cuenta. Con más días podría aparecer algo, pero hoy no hay ninguna regla que se repita.
- Grok Bot solo sacó 100–200 posts por cuenta (1–2 días de cada una). Para ampliar hay que paginar más hacia atrás (cuesta cuota de X).
