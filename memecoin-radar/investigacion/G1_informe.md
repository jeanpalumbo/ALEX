# G1 — Informe de investigación (origen memecoins Solana en X)

**Autor:** Grok Bot (rama destino `grok/memecoin-radar`)  
**Corte de datos:** 2026-11-05 ~22:45 UTC (23:45 Europe/Madrid)  
**Alcance:** solo lectura pública (X conector `x`, DexScreener, GeckoTerminal, docs j7tracker/Phanes/GMGN-Photon-Axiom).  
**No** se compró, publicó ni interactuó con cuentas.  
**Método de etiquetas:** **DEMOSTRADO** = dato reproducible con enlace; **INDICIO** = patrón repetido sin N suficiente o sin reloj independiente; **HIPÓTESIS** = plausible sin prueba directa; **UNKNOWN** = no comprobado en esta pasada.

Fuentes previas reutilizadas (misma máquina / call-hunter, corte 2026-11-05): `upstream_sample.json`, `accounts2.json`, `bots_summary.json`, `evals2.jsonl`. CSVs nuevos en esta carpeta.

---

## 1. Fuentes de origen (primeros minutos)

### DEMOSTRADO — bots/scanners que publican CAs muy pronto

| Cuenta | Followers (5 nov) | Posts ~7d | Frecuencia | Automático |
|---|---:|---:|---|---|
| [bitecong](https://x.com/bitecong) | 38 517 | ~2 162 | ~290–360/día | Sí — plantilla fija `🤖 AI Signal (SOL) $TICKER` + edad en minutos ([ej.](https://x.com/bitecong/status/2118473019765219821)) |
| [SolanaMemesScan](https://x.com/SolanaMemesScan) | 4 322 | ~1 055 | ~130–170/día | Sí — `CTO PING` / `MIGRATION PING` / `PUMP AMM BREAKOUT` ([ej.](https://x.com/SolanaMemesScan/status/2118473599879086344)) |
| [AutorunAlert](https://x.com/AutorunAlert) | 8 121 | ~1 063 | ~120–200/día | Sí — `New token! Check the ANALYSIS! (Screenshot)` + promo depósito Pumpfun ([ej.](https://x.com/AutorunAlert/status/2118473506417414318)) |
| [PumpWatch1](https://x.com/PumpWatch1) | 2 376 | ~125 | ~9–32/día | Sí — `👁️ PUMP WATCH` con Age/MC/Top10/Dex Paid ([ej.](https://x.com/PumpWatch1/status/2118472906694930678)) |
| [solhousesignals](https://x.com/solhousesignals) | 3 099 | ~1 561 | ~200–250/día | Sí (INDICIO fuerte) — plantilla MC/Liq/Vol ([ej. $HIGH](https://x.com/solhousesignals/status/2117683432964702679)) |

**Retraso mediano vs creación del pool (muestra call-hunter upstream, n≈36–43/bot, ventana ~28 oct–4 nov UTC):** bitecong **3.0 min**, AutorunAlert **6.0**, PumpWatch1 **5.8**, SolanaMemesScan **9.3**. Fuente: `call-hunter/upstream/bots_summary.json`.

**Seguir a ciegas a estos bots NO es edge:** bitecong media ret1h **0.47** (69 % ≤0.5×); SolanaMemesScan **0.66**; AutorunAlert **0.82**; PumpWatch1 media **1.13** pero IC amplio y depende de outliers (mediana **0.64**). Misma fuente.

### DEMOSTRADO — lista ampliada (más allá de los 5 conocidos)

| Cuenta | Rol | Evidencia |
|---|---|---|
| [SolTokenScan](https://x.com/SolTokenScan) | scanner (~1 043 posts/7d) | [PAID DEXSCREENER SIGNAL](https://x.com/SolTokenScan/status/2118473072588017669) con Age/Bundlers/Holders |
| [AiSolanaKols](https://x.com/AiSolanaKols) | whale/KOL alerts (~1 096/7d) | [PAID DEXSCREENER](https://x.com/AiSolanaKols/status/2118470343971254780) Bundlers=188 |
| [dex_kolwatcher](https://x.com/dex_kolwatcher) | Dex paid detector | Aparece a ~8 min de create en WEALTH ([post](https://x.com/dex_kolwatcher/status/2118360724296908960)) |
| [Larpcheckbot](https://x.com/Larpcheckbot) | chequeo de narrativa | Responde menciones; **no** discovery primario ([ej.](https://x.com/Larpcheckbot/status/2118349351332331653)) |
| [SenatorLTD](https://x.com/SenatorLTD) | radar bajo followers | Plantilla `NEW MEMECOIN FOUND` Age: 2m ([ej.](https://x.com/SenatorLTD/status/2118468857111171516)) |

Detalle tabular: `fuentes_origen.csv`.

### DEMOSTRADO — el “origen” no es solo bots

En la muestra de 7 tokens (`upstream_sample.json` + HIGH):

1. **Cuenta del proyecto** (p.ej. [AMemeDemocrats](https://x.com/AMemeDemocrats/status/2118353508827361405) AMD a +3 min de genesis on-chain; [Higherdotfun_](https://x.com/Higherdotfun_/status/2117667255484026947) HIGH “We are now live” a +2 min del pool Gecko).
2. **Tweet de narrativa / metadata** (RunnerLivePF en 1CALL; genyrational en BenBen).
3. **Bot scanner** 0.5–4+ min (bitecong, SolanaMemesScan…).
4. **Apes orgánicos** en WEALTH ~3 min post-pair ([yarodegen](https://x.com/yarodegen/status/2118359485324378232) 15:07:13Z; pair DexScreener 15:04:33Z).

Cadena completa: `ejemplos_origen_cadena.csv`.

### INDICIO

- Varios bots publican el **mismo ticker con CAs distintas** en el mismo minuto (HABIBINALD: [PumpWatch1](https://x.com/PumpWatch1/status/2118472906694930678) vs [bitecong](https://x.com/bitecong/status/2118473013285077022)) → riesgo de copiar ticker sin CA.
- `solhousesignals` no tuvo backtest independiente en la pasada 3 de call-hunter.

### HIPÓTESIS / UNKNOWN

- Cuántos bots adicionales existen en TG/Discord **sin** espejo en X: UNKNOWN (Phanes demuestra el mecanismo, no el inventario).
- Correlación exacta “primer bot en X ⇒ mejor EV” ya **refutada** en bruto por medias <1 (ver arriba).

---

## 2. Herramientas de lanzamiento (“Deployed using j7tracker.io”)

### DEMOSTRADO — significado

Según docs oficiales j7tracker:

- j7tracker es un **deployer / tracker** multi-plataforma (pump, bonk, bags, …) con API `POST …/submit` `type=create_token` ([docs](https://docs.j7tracker.io/docs/create-token), [home](https://j7tracker.io/): reclama 1.35M+ tokens desplegados).
- El texto **"Deployed using j7tracker.io"** es la **descripción por defecto** en metadata del token.
- Se omite si `private_desc: true` ([docs Deploy API](https://docs.j7tracker.io/docs/deploy)).
- La misma API expone flags de **bundle / sniper / auto_sell / multi_deploy** ([docs](https://docs.j7tracker.io/docs/create-token)) → la firma j7 **no** implica token “limpio”; implica uso de tooling de deploy profesional (a menudo sniper-friendly).

### DEMOSTRADO — quién la usa

- Cualquier wallet que despliega vía j7tracker (API, extensión o UI). Visible en páginas pump.fun (ej. resultados de búsqueda web 2026 mostrando la frase en description).
- En X, [bitecong](https://x.com/bitecong/status/2118453657041879401) describe tokens cuya description “only says it was deployed using a tracker site” (CA `5w5uSLRd9m5Md7abHNFy3mwMvp3eKHquHs1ct461pump` $BUY; también [dump](https://x.com/bitecong/status/2118334165674496395) `Bu3h78FY2fsWVZ1MdyQVpFTvv5XsRotWX6VjszQTpump`).

### INDICIO — correlación winners vs rugs

- Tokens con description **solo** firma de tracker aparecen en señales bitecong de edad 1–3 min **sin tema** (BUY, dump, Hedgecat, McDonald, ACTII en timeline 5 nov) → tipicamente **spam de deploy tooling**, no narrativa.
- **No** hay muestra N≥30 con etiqueta j7 sí/no × ret24h en esta pasada.

### HIPÓTESIS

- j7tracker **ni predice** 10× ni rug por sí solo; es un **proxy de “deployer técnico”** (puede ser sniper bundle o proyecto serio). Hace falta cruzar con holders/dev sell/bundles (datos GMGN/on-chain), no solo la string.

### UNKNOWN

- Firma análoga exacta de otras tools en metadata pump.fun esta semana (padre/bloom/bags default strings): búsqueda X de “Deployed using” devolvió casi solo ruido + menciones bitecong; sin crawl sistemático de pump.fun API (403 desde el box).

---

## 3. Telegram / KOLs vs X

### DEMOSTRADO — infraestructura TG (no un grupo concreto)

- [Phanes](https://docs.phanes.bot/) es bot **gratis** de tracking de calls en grupos TG/Discord: registra quién pegó la CA primero, `/fc`, `/calls`, leaderboard, DApp. “Called at” = MC cuando se consultó **en ese grupo** (no discovery global). Docs: [leaderboard](https://docs.phanes.bot/phanes/leaderboard), [dapp](https://docs.phanes.bot/phanes/dapp).
- Varios callers de X **venden** acceso TG en posts públicos:
  - [Crypt_bencall1x](https://x.com/Crypt_bencall1x/status/2118107112991821985): “My Tg frens will always get it first” + DM entry.
  - [sol_lord111](https://x.com/sol_lord111/status/2117721649034432825): “dm now to subscribe”; bio “dm for promo”.
  - [bullstreetxx](https://x.com/bullstreetxx/status/2118353678973182254): precio público “Just 0.35 SOL for PREMIUM alphas”.

### INDICIO — “Premium/VIP call” en X **después** del movimiento

- [solanavipcalls](https://x.com/solanavipcalls) (~30k followers) publica updates del tipo “Nx From Premium call” con CA (ej. [george 5x](https://x.com/solanavipcalls/status/2118417665455005825) 18:58Z 5-nov; [HIGH 57x](https://x.com/solanavipcalls/status/2118323796960768450); [ABTC 24x](https://x.com/solanavipcalls/status/2118212237433401512)).
- [A33on_](https://x.com/A33on_/status/2117589461311582593) / [Shdow_Sol](https://x.com/Shdow_Sol/status/2117592518640697846) “from my tg call” **post-facto**.

### UNKNOWN / BLOQUEO — prueba de horas TG **antes** que X

**No demostrado** en esta pasada: no hay acceso a historial de canales TG privados ni export Phanes de un grupo concreto con timestamps comparables al primer post X.  
Cualquier afirmación “TG cantó a HH:MM antes que X” sin captura del mensaje TG + reloj = **no válida**.

### HIPÓTESIS

- Parte de los “callers” de X son **espejos con retraso** de alpha TG/Phanes; explicarían plantillas similares y retrasos 3–62 min vs origen X (ya DEMOSTRADO en muestra de 7).

---

## 4. Patrones de rug (<1 h / muerte rápida)

Ejemplos concretos: `rugs_ejemplos.csv`.

### DEMOSTRADO

1. **Llegar tarde al pico:** AMD `Eq8UZ5oadKvLtiDnPrb41dwDwU4BuB2tFXRT8rw8pump` — genesis 14:40:18Z; callers 15:48–16:23Z con **ret1h ≈ 0.004–0.006** tras **max1h ≈ 1.1–1.6** (evals2). DexScreener **ch24 = −96 %**, fdv residual ~1.7k ([pair data](https://api.dexscreener.com/latest/dex/tokens/Eq8UZ5oadKvLtiDnPrb41dwDwU4BuB2tFXRT8rw8pump)).
2. **Spike → death en minutos:** TSLA `F6jHbE6XNfZ8DpmvDj4JbJxVFg4UbzSPnyiJkDHDpump` — 0xSeerr **max1h = 154** luego sol_lord/APE **ret1h ≈ 0.01**; DexScreener ch24 **−94 %**.
3. **Segundo caller muere:** WI `6nMwojSDbXBpJR4JHPmANSPQiJJhGpJGRcSroVv5pump` — APE ret1h 7.74; sol_lord +56 min ret1h **0.0048**.
4. **TAPE** `7xP2r4Vtjy5opBZjbPcCc4N7BkRhhQddqsFQDpDopump` — ret1h ~0.007 para DegenFlow_/0xSeerr; fdv ~1.8k.
5. Entre 256 CAs con ret1h en evals2, **84** tienen al menos un observador con ret1h ≤ 0.2.

### INDICIO

- **Top10 holders extremos:** PumpWatch1 marca HABIBINALD Top10 **83 %** a Age 2m ([post](https://x.com/PumpWatch1/status/2118472906694930678)).
- **Bundlers altos** en signals AiSolanaKols (NEARFUN Bundlers=188) — señal de riesgo, no prueba de rug por sí sola.
- **Narrativa / ticker copiado:** dos “AMD” distintos (DDmGnu… vs Eq8UZ5…); múltiples iMeme/HABIBINALD CAs el mismo día.
- **Description vacía salvo deploy tool** (BUY/dump) — ver §2.

### HIPÓTESIS

- Bundles + auto_sell de deployers (j7tracker flags) explican parte de los spikes max1h enormes con ret1h≈0 para el siguiente caller. Requiere C4 (wallets) de Claude.

---

## 5. Patrones de éxito (≥10× en 24 h esta semana)

### DEMOSTRADO — ≥10× a **1 h** (call-hunter evals2, no siempre sobrevive 24 h)

| CA | Symbol | Evidencia | Primeros ~10 min | Nota fracaso |
|---|---|---|---|---|
| `8Mi9E1V2bdPeAaRkR5yxUsAvpzP6UBUEEUrYmgKNpump` | WEALTH | solblender99 ret1h **79.3** max1h **82.5**; DexScreener ch24 **+225 %** fdv~149k | Pair 15:04:33Z; apes 15:07+ ([yarodegen](https://x.com/yarodegen/status/2118359485324378232), [VOLTIXSOL](https://x.com/VOLTIXSOL/status/2118359735682638038)); narrativa USELESS/@redsol23 amplificada ~17:07 ([BitcoinIntelX](https://x.com/BitcoinIntelX/status/2118389794044776720)) | 24h OHLCV incompleto al corte eval |
| `J8xUfMeWDE2VsmMvDVr5Qyvxn7C5Hv3zAWB6QpHwpump` | 1CALL | RunnerLivePF ret1h **17.4** max1h **23.4** | Narrativa proyecto +3 min genesis | DexScreener ch24 **−95 %** — **éxito 1h ≠ 24h** |
| `DDmGnuvroxVrb7CSyjYcezFU8gnAfhKasg4ZZezmpump` | AMD (win) | Ben ret1h **27.5** ret24h **8.36** (<10) | Social en DexScreener | No cumple umbral 10× a 24h |

### DEMOSTRADO / INDICIO — candidatos ≥10× 24 h con evidencia mixta

- **HIGH** `7ymF66Z6VhgNiwadtVhjTtT6U7iQRpSxeiRrhfufhigh`: origen proyecto [Higherdotfun_](https://x.com/Higherdotfun_/status/2117667255484026947) 17:16:32Z; FDV ~**2.08M** y liq ~120k el 5-nov (DexScreener). Reclamo VIP 57× es **INDICIO** (post-facto). **UNKNOWN** el múltiplo exacto open→+24h sin OHLCV propio aquí.
- **ABTC / PIRATE / RICO**: reclamos solanavipcalls (**INDICIO**); DexScreener confirma liquidez/FDV vivos en ABTC/PIRATE; RICO ya en drawdown fuerte (−69 % 24h al corte).

CSV: `exitos_10x.csv`.

### Patrones repetidos en los que **sí** hubo corrida fuerte (INDICIO consolidado)

1. **Origen = proyecto o narrativa con account X** en ≤5 min (HIGH, 1CALL, AMD proyecto), no solo bot silencioso.
2. **Liquidez y volumen** visibles pronto (WEALTH: posts tempranos citan vol/mcap; HIGH liq 24k→120k).
3. **Comunidad / lore** (USELESS team → WEALTH; Higher.fun live).
4. Callers X llegan **después**; el edge está en origen, no en el caller mediano (1CALL: caller APE ret1h 0.09 tras upstream 17×).

### UNKNOWN

- Lista exhaustiva de todos los ≥10× 24h Solana pump.fun 29-oct→5-nov: requiere G5 histórico + C2 backtest, no solo search X.

---

## 6. Herramientas y comunidades de investigación

### DEMOSTRADO — qué dan en público (docs / comparativas 2026)

| Tool | Forma | Datos públicos típicos | Estado / nota |
|---|---|---|---|
| **GMGN** ([@gmgnai](https://x.com/gmgnai), gmgn.ai) | Web + TG | Smart money / KOL tags, first buyers, rug history del creator, snipers/insiders/bundles, copy trade | Activo; fee ~1% |
| **Axiom** ([@AxiomExchange](https://x.com/AxiomExchange)) | Web | Pulse (new / final stretch / migrated), wallet tracker, X monitor (umbral vol documentado), MEV modes, perps HL | Activo |
| **Photon** | Web (+TG hist.) | Memescope pump.fun, mint/LP/top10/deployer checks, limit/DCA | Activo; cuenta X `photon_sol` **suspended** al lookup 5-nov |
| **BullX** | Web+TG | Neo Vision / holders / sniper | Trading **suspendido 1 jun 2026** (fuentes MemeTools/comparativas); `bullxneo` suspended en X |
| **Trojan / BonkBot / Padre(Terminal)** | TG/Web | Ejecución + a veces copy; Padre citado como terminal en UI pump.fun | Operativos según reviews 2026 |
| **DexScreener** ([@dexscreener](https://x.com/dexscreener)) | Web/API | pairs, priceChange, liquidity, socials, pairCreatedAt (**≠** creación token) | Usado en este informe |
| **GeckoTerminal** | API | pools OHLCV 1m, pool_created_at | Usado en call-hunter |
| **Phanes** | TG/Discord bot | Quién llamó primero **en un grupo**, MC al call, leaderboards | Docs oficiales |
| **PumpWatch1 / bitecong / scanners X** | X | Filtros Age, Top10, Dex paid, AI text | Ver §1 |

Comparativas consultadas: [Belphor](https://www.belphor.com/learn/gmgn-vs-axiom-vs-photon-vs-bullx.html), [MemeTools Oct 2026](https://memetools.io/news/solana-trading-terminals-compared), [GMGN blog 2026](https://gmgn.ai/blog/best-meme-coin-trading-platforms-2026/).

### INDICIO

- Traders “serios” en X **combinan** GMGN (riesgo/wallets) + Axiom/Photon (ejecución) + Phanes (reputación de callers TG), no un solo bot de alerts.

### UNKNOWN

- Winrate real de copy-trade GMGN / wallet trackers específicos: no medido aquí.

---

## 7. Callers — lista ampliada y clasificación

Base: 26 cuentas en `call-hunter/accounts.json` + amplificación X (solanavipcalls, bullstreetxx, Massivepumpmast, solblender99, _coinchic, Higherdotfun_ como origen no caller, etc.).

### DEMOSTRADO — 6 candidatos principales (evals2)

| Caller | med_min desde create | % ret1h ≤0.5 | % ≥2× | med_ret1h | vs origen |
|---|---:|---:|---:|---:|---|
| APE_ORACLE1 | 36.1 | **51 %** | 5.6 % | 0.39 | Después |
| Solprofit1 | **276.6** | 5 % | 1.8 % | 0.996 | Muy tarde |
| DegenFlow_ | 120.8 | 24 % | **0 %** | 0.89 | Después |
| sol_lord111 | 27.3 | **65 %** | 2.7 % | 0.20 | Después cercano |
| 0xSeerr | 17.0 | **64 %** | 1.6 % | 0.27 | Después cercano |
| Crypt_bencall1x | 37.0 | 50 % | 9.4 % | 0.46 | Después |

Nadie “corona” con edge claro a 1h; la mayoría de calls **mueren o diluyen**. Muestra sesgada a CAs compartidas / survival de seed Ben.

### DEMOSTRADO — promo / pago

| Cuenta | Prueba |
|---|---|
| sol_lord111 | Bio “dm for promo” + [post subscribe](https://x.com/sol_lord111/status/2117721649034432825) |
| Crypt_bencall1x | Serie de posts “join my private Tg” / DM entry ([ej.](https://x.com/Crypt_bencall1x/status/2118107112991821985)) |
| bullstreetxx | [0.35 SOL PREMIUM](https://x.com/bullstreetxx/status/2118353678973182254) precio en claro |

### INDICIO — promo no facturada on-chain

- solanavipcalls “Premium call”, Massivepumpmast/solblender99 “DM private TG”, APE/0xSeerr bios con TG.

CSV: `callers_clasificacion.csv`.

---

## Límites y sesgos (obligatorio)

1. Índice de búsqueda X incompleto (ya visto en call-hunter: posts en timeline no siempre en search).
2. Muestra callers **sesgada** a cuentas que compartieron CAs “calientes”.
3. Telegram privado = caja negra sin Phanes export del grupo.
4. `pairCreatedAt` DexScreener ≠ genesis mint (usar RPC/Gecko pool pump-fun).
5. Precios sin slippage ni comisiones salvo modelos upstream curva.
6. Quota X del día: ~883/1000 restantes al cerrar lecturas; no se paginó archivo completo de todos los bots.

## Archivos entregados

- `investigacion/G1_informe.md` (este)
- `investigacion/fuentes_origen.csv`
- `investigacion/ejemplos_origen_cadena.csv`
- `investigacion/rugs_ejemplos.csv`
- `investigacion/exitos_10x.csv`
- `investigacion/callers_clasificacion.csv`
- `SUMMARY.md` (raíz del paquete para Lolo)
