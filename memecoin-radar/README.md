# memecoin-radar

Sistema para encontrar entradas a memecoins de Solana **en su origen**, no tarde detrás de los callers.
Lo desarrollan dos agentes sobre este mismo directorio:

- **Grok Bot (xAI):** vigila X 24/7 (bots de origen, narrativas, callers), investiga y escribe datos.
- **Claude (Anthropic):** programa el escáner, la verificación de precios, el simulador y el panel,
  y analiza los datos.
- **Piero:** decide. Nada compra solo. Dinero real solo si la simulación cumple los criterios.

> Ojo: el repositorio ALEX es **público**. No subir nunca claves, carteras privadas ni datos personales.

## Lo que ya sabemos (Radar de callers de Grok Bot, 2-5 nov 2026)
- El primer post público de una CA lo hace la **cuenta del proyecto**, el **tuit de narrativa** enlazado
  en la metadata del token o un **bot scanner público** (bitecong, SolanaMemesScan, AutorunAlert,
  PumpWatch1, solhousesignals), entre **0,5 y 4 min** después de crear el token.
- Los callers observados (APE_ORACLE1, Solprofit1, DegenFlow_, sol_lord111, 0xSeerr, Crypt_bencall1x)
  publican entre **3 y 62 min** después. Entrar en el origen habría sido **1,7×-4,6× más barato**.
- Ningún caller es fiable por sí solo. Muestra pequeña (7 tokens) y con **sesgo de supervivencia**.
- Los escáneres antiguos de Piero (`meme-hot`, `dexscreener-meme-scanner`) llegaban tarde por diseño:
  exigían +20-30 % en 1 h, revisaban cada 5-20 min y sus workflows estaban en una carpeta incorrecta.

## Estructura
| Ruta | Dueño | Qué es |
|---|---|---|
| `TAREAS.md` | ambos | Tablero de tareas: quién hace qué, estado, fecha |
| `data/senales.csv` | Grok Bot | Una fila por token detectado (ver cabecera) |
| `data/callers.csv` | Grok Bot | Ranking semanal de fuentes y callers |
| `data/verificacion.csv` | Claude | Comprobación independiente de precios de cada señal |
| `investigacion/` | Grok Bot | Informes de investigación en X, con fuentes |
| `informes/` | Claude | Análisis semanal y decisiones |
| `radar/` | Claude | Código Python |

## Fuentes de datos accesibles (comprobado 5 nov 2026)
GeckoTerminal API (precios, velas, pools) · RPC público de Solana · Rugcheck API · DexScreener API ·
PumpPortal (stream de creación de tokens de pump.fun).

## Uso
```bash
cd memecoin-radar
python -m radar.verify      # verifica las señales nuevas de data/senales.csv
python -m pytest -q         # tests
```

## Criterios para pasar a dinero real (fijados antes de empezar)
Con ≥ 100 señales verificadas por `radar.verify`:
- retorno medio a 1 h > +20 % tras restar 10 % de deslizamiento y comisiones, y
- menos del 50 % de las señales pierde más del 50 %.
Si se cumple: tickets fijos de 10-20 €, máx. 3 posiciones, stop −50 %, vender la mitad a +100 %.

## Proyectos de código abierto de referencia (sin revisar a fondo, no ejecutar sin leerlos)
- vladiclick/pumpfun-monitor: monitor de lanzamientos de pump.fun con filtro anti-rug.
- FLOCK4H/Dexter: ranking de creadores de pump.fun por rendimiento de sus tokens.
- mostronton-commits/tracced: primeras wallets de cada token y top traders.
- nathanliow/pumpscope: stream de creaciones y trades vía Helius.
- TaroYamada08/coin-monitoring: framework de bots de Telegram para pump.fun.
Ninguno cruza X/callers con la creación on-chain: ese es el hueco que cubre este proyecto.
