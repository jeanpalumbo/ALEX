# call-hunter — investigación RETROSPECTIVA de cuentas que publican calls (Solana memecoins)

Corte de datos: 2026-11-05 ~19:20 UTC (20:20 Europe/Madrid). Investigación secundaria ("juego de azar"): nada aquí es recomendación de compra/operar.

## Qué es
Registro histórico de posts públicos de X con dirección de contrato (CA), de un lote semilla de 25 cuentas
descubiertas a partir de @Crypt_bencall1x (Ben) y de quienes publicaron las mismas CA. NO es un monitor prospectivo.

## Fuentes
- X (conector público `x`): `get_users_by_usernames`, `get_users_posts` (100 posts/página, sin RT; 2ª página para 8 cuentas), `search_posts_all` por CA exacta.
- Precios históricos: GeckoTerminal API pública v2 (`/networks/solana/tokens/{ca}/pools`, `/pools/{pool}/ohlcv/minute`), velas 1m, solo 2 pools por token y 1 página (1000 velas) por pool.
- DexScreener `latest/dex/tokens` solo como referencia (pairCreatedAt ≠ creación del token).
- Phanes docs: https://docs.phanes.bot/phanes/leaderboard y /dapp — Phanes registra cualquier coin consultado en un grupo TG/Discord; "Called at" = MC al consultarse en ESE grupo. Es tracking, no descubrimiento.

## Ficheros
- `raw/*.txt` respuestas crudas. `users.json` perfiles. `timeline_meta.json` next_token por cuenta (para continuar paginación).
- `calls.jsonl` una fila por (post, CA): post_id, url, author, created_at_utc, ca, chain, tipo (`mención_CA` | `resultado/reclamación` por heurística de texto), texto.
- `ohlcv/{ca}.json` velas 1m por pool + pool_created_at + fetched_at.
- `evals.jsonl` primera mención de cada autor por CA: rango entre observados, retraso vs primer observado, min desde primer pool, precio al post, ret_1h, ret_24h, max_1h, volumen 15m previo, estado EVALUABLE/NO EVALUABLE.
- `accounts.json` agregados por cuenta.
- Scripts: `build.py` (normaliza), `prices.py` (OHLCV), `analyze.py` (métricas).

## Definiciones
- Puntualidad: rango de la primera mención de la cuenta entre las cuentas OBSERVADAS (no primero global).
- Volumen: posts con CA y CAs únicas en la ventana revisada (ventana distinta por cuenta; ver `ventana_utc`).
- Acierto: precio (close 1m) a +1h / precio en el minuto del post ≥ 2 (umbral = hit rate de Phanes). Pérdida: ≤ 0.5.
  24h solo si ya transcurrieron. Precio sin slippage ni comisiones; en tokens con liquidez de pocos miles de USD el precio de ejecución real sería peor.
- Sin velas antes del post ⇒ NO EVALUABLE. Nunca se usa el "NX" del tweet ni el precio actual.

## Límites
- Índice de búsqueda de X incompleto (no devolvió un post de Ben que sí está en su timeline).
- 100–200 posts por cuenta ≈ 1–2 días: muestra pequeña. Posts borrados y Telegram privado invisibles.
- Lote semilla sesgado: cuentas encontradas por CAs ganadoras. Muchas cuentas comparten plantillas/hora → posible red coordinada.
- Heurística de `tipo` imperfecta.

## Reproducir / siguiente checkpoint
1. Añadir cuentas en `users.json` (get_users_by_usernames) y páginas con `pagination_token` de `timeline_meta.json`; guardar en `raw/`.
2. `python3 build.py && python3 prices.py && python3 analyze.py`.
3. Siguiente lote: paginar 3–5 páginas de los 5 candidatos con más "primero_entre_observados" para tener ≥30 calls evaluables por cuenta antes de comparar aciertos.

## Resultado pasada 1 (corte 2026-11-05 19:20 UTC)
751 posts con CA, 159 CAs, 23 cuentas principales; 202/341 primeras menciones evaluables a 1h.
Mediana del ratio de precio a 1h: 0.74 (mención_CA), 0.65 (primer observado). Solo 3 ≥2x; 73 ≤0.5x. Nadie coronado.
Page: https://cursor.com/canvas/store-9c222b49-9492-4efa-b4a2-f1d02b91961c/6973f4c5-d0a7-488d-a5c2-0440534716d5

## Pasada 2 (corte 2026-11-05 ~20:15 UTC = 21:15 Madrid) — retrospectiva + génesis
- X: 21 lecturas de timeline (3–4 páginas extra para 6 candidatos) + 15 búsquedas por CA exacta (antes del primer post observado). ~36 lecturas.
- OHLCV: `prices2.py` para TODAS las CAs Solana de los 6 candidatos (incluye CAs de un solo autor = fracasos), 2 pools, hasta 3 páginas; guarda base/quote del pool (se descartan pools donde el token no es base).
- `analyze2.py` (auditado):
  - Entrada = OPEN de la primera vela 1m que empieza tras el post (≤5 min); si no hay trades, último close ≤30 min antes (marcado). Evita lookahead del minuto del post.
  - Salida = close de la última vela que termina ≤ post+H. Si post+H > fin de cobertura descargada ⇒ NO EVALUABLE (nunca 0).
  - Se separa ret punto a punto, máximo y mínimo intrahora (`max_1h`, `min_1h`) y minutos sin velas al final.
  - Sin slippage, comisiones, ni liquidez histórica (GeckoTerminal solo da liquidez actual) ⇒ no es PnL real.
- Génesis: `genesis.py` (RPC público Solana, firma más antigua del mint). Confirmado on-chain en 2 tokens (1CALL 06:36:44Z, AMD 14:40:18Z) = `pool_created_at` del pool pump-fun en GeckoTerminal; INU/george truncados (>60k firmas). `pairCreatedAt` de DexScreener y pools PumpSwap NO son creación.
- `upstream_sample.json`: 7 tokens con cadena creación → primer post upstream (proyecto/narrativa/bot) → primer candidato.
- Ficheros nuevos: evals2.jsonl, accounts2.json, upstream_sample.json, genesis.json, info/*.json (metadata GeckoTerminal: twitter/web del token).

## Pasada 3 (corte 2026-11-05 ~20:45 UTC = 21:45 Madrid) — bots upstream, histórico
- X: 17 lecturas (perfiles + 4 páginas de 25 posts × 4 bots, end_time 2026-11-04T18:55Z para que 24h estén cumplidas). 400 posts, 337 primeras menciones (bot, CA).
- Muestra aleatoria (seed 42) de 45 primeras menciones por bot = 180 (158 CAs); OHLCV GeckoTerminal 1m, 2 pools, ≤2 páginas. `upstream/prices.py`, `upstream/evaluate.py`.
- Slippage: solo modelable en curva pump.fun (reservas virtuales 30 SOL / 1.073e9 tokens, comisión supuesta 1%/lado, graduación ~115 SOL virtuales; SOL/USD horario de GeckoTerminal). Fuera de curva (PumpSwap/otros AMM) NO estimable: se reporta bruto.
- Bootstrap 5000 para IC95 de la media del ratio de precio.
- Ficheros: upstream/posts.jsonl, first_mentions.json, sample.json, evals.jsonl, bots_summary.json, solusd.json.
- Resultado: bitecong y SolanaMemesScan media 1h 0.47 y 0.66 (IC95 < 1) ⇒ seguirlos a ciegas habría perdido (bruto). AutorunAlert 0.82 (IC 0.59–1.09) y PumpWatch1 1.13 (IC 0.68–1.66, depende de 3 outliers ~6×; sin el mayor ≈0.99) ⇒ no determinable.
