# Gold takeover — Memecoin radar (6 nov 2026)

Zona horaria: **Europe/Madrid** (UTC+1). Solo simulación: no compras, no wallets, no gasto.

## Quién

- Agente: **Gold** (Grok Bot), toma de control desde Lolo.
- Repo: `jeanpalumbo/ALEX`
- Ramas: código/datos radar → `grok/memecoin-radar`; informes oficina → `grok/oficina`
- Checkout box: `/workspace/ALEX` (working tree puede estar en `grok/oficina` o `grok/memecoin-radar`; el collector lee el árbol de archivos bajo `memecoin-radar/`)

## Procesos vivos (comprobado al takeover)

| Rol | Comando / path | PID al takeover |
|---|---|---|
| Watchdog G8 | `bash /workspace/memecoin-radar-runtime/watchdog.sh` | 9659 |
| Collector G8 | `/workspace/ALEX/memecoin-radar/.venv/bin/python -m radar.collector --hours 0` | 9662 |

- Runtime dir: `/workspace/memecoin-radar-runtime/` (`watchdog.sh`, `watchdog.pid`, `last_start.txt`, `restarts.log`)
- Venv: `/workspace/ALEX/memecoin-radar/.venv` (incluye `websockets`)
- Logs: `/workspace/ALEX/memecoin-radar/logs/` (`collector.log`, `watchdog.log`) — el watchdog recrea el dir si falta
- DB local (NO subir a GitHub): `/workspace/ALEX/memecoin-radar/data/collector/collector.db`
- Export CSV: `/workspace/ALEX/memecoin-radar/data/collector/tokens_*.csv.gz`

**No matar** watchdog ni collector salvo instrucción explícita de Claude/oficina.

## Routines / horarios

| Qué | Cuándo (Europe/Madrid) | Acción |
|---|---|---|
| Export diario G8 | **01:30** | `cd /workspace/ALEX/memecoin-radar && .venv/bin/python -m radar.collector --export` → subir solo `data/collector/*.csv.gz` a `origin/grok/memecoin-radar`. **Nunca** `collector.db` |
| Watchdog | continuo | Relanza collector si sale; sleep 5s entre reintentos |
| Caídas | cada incidente | Anotar hora + hueco en informe bajo `memecoin-radar/informes/` y/o `oficina/grok/informes/` |

Nota: la routine formal de export diario la crea Gold (pendiente de alta en el sistema de routines del bot); hasta entonces el export de las ~01:30 del 7 nov se ejecuta manualmente o vía routine cuando Gold la registre.

## Estado de tareas

| ID | Estado | Evidencia |
|---|---|---|
| G8 / M1 | **EN CURSO** | Collector+watchdog vivos. Caída remount ~12:45–12:55 Europe/Madrid (último log 11:45Z `created: 1699`; reinicio 12:55; hueco medido ~10 min). Detalle: `memecoin-radar/informes/2026-11-06_g8_caida.md` en `grok/memecoin-radar` |
| G6 / M2 (parte G6) | **HECHO** (6 nov 2026) | `data/callhunter/` en commit `1274ed0` rama `grok/memecoin-radar` |
| G7 / M2 (parte G7) | PENDIENTE | `data/origen_proyecto.csv` ≥100 tokens — aún no |
| Export intermedio | **HECHO** | `tokens_2026-11-06.csv.gz` = **1015** tokens / 101318 B (antes 71 tokens en GitHub). Commit `1274ed0` |

### URLs commit memecoin-radar

- Commit: https://github.com/jeanpalumbo/ALEX/commit/1274ed0e00c0836c0d182bab45bcfeb9d71adbd3
- CSV blob: https://github.com/jeanpalumbo/ALEX/blob/grok/memecoin-radar/memecoin-radar/data/collector/tokens_2026-11-06.csv.gz
- Callhunter: https://github.com/jeanpalumbo/ALEX/tree/grok/memecoin-radar/memecoin-radar/data/callhunter

## Reglas operativas

1. Solo simulación / investigación de reglas de entrada.
2. Código `radar/` lo escribe Claude; Gold ejecuta, recoge datos e investiga.
3. **Nunca** subir `collector.db` ni `*.db*`.
4. Datos reales con fuente; si no está comprobado → `NO COMPROBADO`; si bloqueado → `BLOQUEADO` + motivo exacto.
5. Normas de X: nada de spam ni bots de interacción.

## Call-hunter crudo (origen box)

Fuente local: `/workspace/call-hunter/` → copiado tal cual a `memecoin-radar/data/callhunter/` (G6).

## Mensaje a Lolo

Cuando todo lo anterior esté estable: decir exactamente **«lo tengo»**.
