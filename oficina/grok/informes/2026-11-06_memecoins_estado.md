# Estado Memecoin radar — traspaso (2026-11-06 ~12:55 Europe/Madrid)

**Autor:** Lolo (Grok Bot) · **Pedido:** Claude (oficina) / Piero · **Acción:** no se para nada hasta confirmación del bot nuevo.
**Corte verificado en disco/GitHub:** 2026-11-06 ~12:55 Europe/Madrid.

---

## 1. Qué corre ahora y dónde

### Procesos (verificado con `pgrep` / `ps`)
| Componente | Estado ahora | Evidencia |
|---|---|---|
| Watchdog G8 | **CAÍDO** | `/workspace/memecoin-radar-runtime/watchdog.pid` = `202604` pero `kill -0 202604` → No such process |
| `python -m radar.collector` | **CAÍDO** | Ningún proceso python de collector/radar/memecoin en `pgrep` |
| `.venv` del collector | **AUSENTE** | `memecoin-radar/.venv/bin/python` no existe en el checkout actual |

Único watchdog vivo en el box ahora: Price Hunter (`/workspace/price-hunter/watchdog.sh`, pid bash ~6191) — **no** es memecoin.

### Paths box
| Path | Rol |
|---|---|
| `/workspace/ALEX` | Checkout ALEX; rama actual de trabajo oficina = `grok/oficina` |
| `/workspace/ALEX/memecoin-radar/` | Código + data del radar (código `radar/` de Claude; Lolo escribe `data/*.csv` e `investigacion/`) |
| `/workspace/memecoin-radar-runtime/` | Runtime: `watchdog.sh`, `watchdog.pid`, `last_start.txt`, `watchdog.out` |
| `/workspace/memecoin-radar-g1/` | Paquete G1 (informes/CSV investigación; copia local) |
| `/workspace/call-hunter/` | Datos crudos origen G1/G6 (aún **no** subidos a `memecoin-radar/data/callhunter/`) |

### Watchdog
- Script: `/workspace/memecoin-radar-runtime/watchdog.sh`
- Lanza: `/workspace/ALEX/memecoin-radar/.venv/bin/python -m radar.collector --hours 0`
- Logs: `/workspace/ALEX/memecoin-radar/logs/watchdog.log` + `collector.log`
- `last_start.txt` contenido: `2026-11-06T01:18:48+01:00`
- `watchdog.log` solo tiene esa línea START; **no** hay línea EXIT (proceso cortado, no reinicio limpio)

### Ramas remotas
| Rama | HEAD | Notas |
|---|---|---|
| `origin/grok/memecoin-radar` | `c16c29f` — *G8: scope to 24h collection window (export ~7 nov 01:30)* | Rama de trabajo memecoin de Lolo |
| `origin/claude/new-session-akjsxp` | origen C3 collector (`5517886`) | Carpeta `memecoin-radar/` creada por Claude |
| `origin/grok/oficina` | oficina compartida | Este informe + TAREAS |

---

## 2. Routines y horarios

| Nombre (UI) | Folder | Trigger | Qué hace | Estado |
|---|---|---|---|---|
| **G8 collector: export a las 24 h** | `g8-collector-export-diario` | **Once** 7 Nov **01:30** Europe/Madrid | `python -m radar.collector --export` → subir `data/collector/*.csv.gz` a `grok/memecoin-radar` (**nunca** el `.db`) | Programada (aún no ejecutada) |
| Radar de callers: fuentes y resultados | (call-hunter) | Weekdays 9–19 hourly | Investigación callers X | **PAUSED** (secundario; no es el collector G8) |

No hay routine cron periódica del collector en sí: el 24/7 lo llevaba el watchdog local en el box. Solo hay la routine **once** de export.

---

## 3. Tareas M1/M2 y G6/G7/G8

### `oficina/grok/TAREAS.md` (rama `grok/oficina`)
| # | Estado tablero | Realidad verificada |
|---|---|---|
| **M1** (= G8 collector) | **PENDIENTE** en tablero oficina | G8 estuvo EN CURSO desde ~01:20; collector **caído** al corte de este informe |
| **M2** (= G6 + G7) | **PENDIENTE** | Sin avance nuevo hoy |
| **S1** | actualizado en este push a **EN CURSO (métricas las aporta Claude)** | Ya no se intenta YouTube Studio |

### `memecoin-radar/TAREAS.md` en `grok/memecoin-radar`
| # | Estado | Resultado / punto |
|---|---|---|
| G1 | HECHO (5 nov 2026) | Informe + 5 CSV en `investigacion/` |
| G2–G4 | PENDIENTE | Esperan (prioridad G8/G6/G7) |
| G5 | CANCELADA | Reenfocada a G7 |
| **G6** | **PENDIENTE** | Subir raw call-hunter → `data/callhunter/` (archivos existen en `/workspace/call-hunter/`: `upstream_sample.json`, `accounts.json`, `upstream/bots_summary.json`, `evals2.jsonl`, etc.) |
| **G7** | **PENDIENTE** | Muestra ≥100 tokens origen proyecto/narrativa → `data/origen_proyecto.csv` |
| **G8** | **EN CURSO (6 nov 2026)** en rama memecoin | Arranque ~01:20 Europe/Madrid; export programado ~01:30 del 7 nov; CSV parcial 71 tokens ya en rama |

### División de roles (vigente)
- Lolo: `data/*.csv`, `investigacion/`, ejecutar collector G8, routines.
- Claude: programa `radar/`.
- **Simulación solamente; nunca comprar.**

---

## 4. Últimos CSV / datos en GitHub

### En `origin/grok/memecoin-radar`
| Archivo | URL | Notas |
|---|---|---|
| Export parcial G8 | https://github.com/jeanpalumbo/ALEX/blob/grok/memecoin-radar/memecoin-radar/data/collector/tokens_2026-11-06.csv.gz | Commit `27ef7f8` (6 nov ~01:25 Europe/Madrid); **71 tokens** (blob ~7069 B) |
| G1 investigación | https://github.com/jeanpalumbo/ALEX/tree/grok/memecoin-radar/memecoin-radar/investigacion | `G1_informe.md` + 5 CSV |
| Templates | `data/senales.csv`, `data/callers.csv` | vacíos / plantilla |

### En disco box (más fresco que GitHub; **aún no pusheado**)
| Archivo | Tamaño / filas | Rango |
|---|---|---|
| `memecoin-radar/data/collector/collector.db` | 1 679 360 B · **1698 tokens** · **4664 snaps** · meta_ok 1660 | created_utc min **2026-11-06 01:18:13** → max **12:45:50** Europe/Madrid |
| `memecoin-radar/data/collector/tokens_2026-11-06.csv.gz` (local) | 101 318 B · **1015 filas de datos** (+ header) | Export local intermedio; **no** coincide con el de GitHub (71). El export oficial 24 h sigue previsto ~01:30 del 7 nov |

**Regla:** no subir `collector.db`.

---

## 5. Caídas / errores

1. **Caída dura del watchdog+collector (crítica):** proceso pid `202604` muerto; sin línea EXIT en `watchdog.log`. Último heartbeat útil en `collector.log`: `[11:45Z]` (= **12:45 Europe/Madrid**) con `created: 1699`. Mtimes del FS ~**12:46** Europe/Madrid → coherente con remount/reinicio del box que mató el proceso y dejó `.venv` ausente.
2. **No aguantó 24 h seguidas** (arranque ~01:18 → corte ~12:45 ≈ **11 h 27 min**). **Avisar a Jean/Claude** según encargo G8.
3. Errores recurrentes mientras corría (no fatales; el collector reconectaba):
   - `[stream] reconnecting after error: no close frame received or sent`
   - `keepalive ping timeout` / `sent 1011 (internal error)`
   - DexScreener: `The read operation timed out`; `SSL: UNEXPECTED_EOF_WHILE_READING`
4. No hay `restarts.log` en runtime (el script lo escribiría tras EXIT; no hubo reinicio controlado).

---

## 6. Cuentas / wallets / claves

**Solo nombres (sin valores):**
- El collector **no usa** API keys ni wallets: fuentes públicas hardcodeadas en `radar/collector.py`:
  - WebSocket PumpPortal: `wss://pumpportal.fun/api/data`
  - DexScreener: `https://api.dexscreener.com/tokens/v1/solana/`
  - IPFS gateway Pinata: `https://gateway.pinata.cloud/ipfs/`
- **No hay** `memecoin-radar/.env`.
- **No hay** wallet de trading / claves privadas asociadas a este proyecto (simulación).
- Variables de ejemplo del monorepo ALEX (`.env.example`, **no usadas por el collector**): `ANTHROPIC_API_KEY`, `OPENROUTER_API_KEY`, Shopify keys, etc.
- GitHub push: cuenta `gh` **jeanpalumbo** (scopes repo).
- X: lecturas públicas / conector X (G1 histórico; G2–G4 pendientes). call-hunter routine pausada.

---

## 7. Nota de traspaso

- **No se ha parado nada a propósito** en este corte: el collector ya estaba caído al inspeccionar.
- **No se ha reiniciado** el collector en este informe (traspaso pendiente; falta `.venv`).
- Routine `g8-collector-export-diario` (once 7 nov 01:30 Europe/Madrid) **sigue** programada.
- Cuando el bot nuevo diga que lo tiene, Lolo deja M1/M2/G8 y se queda en clips; hasta entonces el encargo sigue formalmente a cargo de Lolo (reinicio = decisión de Jean/Claude/bot nuevo).

### Checklist para el bot nuevo
1. Restaurar/crear `memecoin-radar/.venv` + `pip install websockets` (+ deps del proyecto).
2. Relanzar `/workspace/memecoin-radar-runtime/watchdog.sh` (o equivalente) apuntando al checkout correcto/`grok/memecoin-radar`.
3. Tomar routine folder `g8-collector-export-diario` (o recrearla) para export+push csv.gz sin `.db`.
4. Continuar G6 (copiar `/workspace/call-hunter/` → `data/callhunter/`) y G7.
5. Confirmar a Claude/Jean con la frase de toma de control acordada.

## Actualización post-informe (2026-11-06 ~12:55 Europe/Madrid)

- Causa caída: remount del box ~12:46 mató el watchdog; faltaba `.venv`.
- Hueco aproximado: último log collector ~11:45Z → reinicio 12:55 Europe/Madrid (~70 min sin capturar; anotar para G8).
- Acción Lolo: recreado `memecoin-radar/.venv` (`pip install websockets`) y relanzado `memecoin-radar-runtime/watchdog.sh`.
- Procesos vivos tras reinicio: watchdog bash + `python -m radar.collector --hours 0` (nada parado a propósito; se recuperó el servicio).
- Export routine `g8-collector-export-diario` 7 nov 01:30 Europe/Madrid intacta.
