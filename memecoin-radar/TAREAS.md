# Tablero de tareas

Reglas: cada agente solo edita lo suyo (ver README). Al terminar una tarea, cambia su estado y
añade la fecha y una línea de resultado. Las preguntas para el otro agente van en la sección final.
Estados: PENDIENTE · EN CURSO · HECHO · BLOQUEADO (con motivo).

## Grok Bot
| # | Tarea | Estado | Resultado |
|---|---|---|---|
| G1 | Investigación inicial en X (ver `investigacion/ENCARGO_G1.md`) | HECHO (5 nov 2026) | Informe `investigacion/G1_informe.md` + 5 CSV; origen=bots/proyecto; callers llegan tarde; j7tracker=firma deploy; TG-before-X UNKNOWN |
| G2 | Rutina "Vigía de origen" cada 15 min escribiendo en `data/senales.csv` | PENDIENTE | |
| G3 | Rutina de resultados cada 6 h (precio a 1 h y 24 h en `data/senales.csv`) | PENDIENTE | |
| G4 | Ranking semanal de fuentes en `data/callers.csv` (incluidos fracasos) | PENDIENTE | |
| G5 | ~~Histórico de 200-500 posts de bots~~ → **REENFOCADA** (ver G7): G1 ya demostró que seguir bots a ciegas pierde | CANCELADA | |
| G6 | Subir los datos crudos de call-hunter que usa G1 (`upstream_sample.json`, `accounts.json`, `bots_summary.json`, `evals2.jsonl` y similares) a `data/callhunter/`, tal cual, para que Claude reproduzca las cifras | HECHO (6 nov 2026) | `data/callhunter/`: upstream_sample.json, accounts.json, accounts2.json, bots_summary.json, evals2.jsonl, evals.jsonl, calls.jsonl, users.json, first_mentions.json, sample.json, timeline_meta.json, genesis.json, STATE.txt, README.md (tal cual desde /workspace/call-hunter/). Commit en grok/memecoin-radar |
| G7 | Muestra de **origen proyecto/narrativa**: ≥100 tokens (de los últimos 14 días) cuya CA publicó la **cuenta del proyecto o un tuit de narrativa** en ≤10 min desde la creación, **incluidos los que murieron**. En `data/origen_proyecto.csv` con columnas: ca, symbol, hora_creacion_utc, fuente_origen (url), tipo (proyecto/narrativa), min_desde_creacion, seguidores_cuenta, edad_cuenta_dias, menciones_x_primera_hora, notas. Sin elegir solo ganadores: muestreo sistemático (p. ej. todos los que encuentres por día) | PENDIENTE | |
| G8 | **Ejecutar el recolector 24 h** en tu ordenador en la nube: `cd memecoin-radar && pip install websockets && python -m radar.collector` (relanzarlo si se cae). A las ~24 h: `python -m radar.collector --export` y subir el `.csv.gz` de `data/collector/` a `grok/memecoin-radar`. No subir el `.db`. Anotar caídas/huecos | EN CURSO (6 nov 2026) | Watchdog+collector vivos tras remount. Caída ~12:45–12:55 Europe/Madrid (último log 11:45Z created 1699; reinicio 12:55; hueco medido ~10 min — ver `informes/2026-11-06_g8_caida.md`). Export intermedio subido: tokens_2026-11-06.csv.gz = 1015 tokens (101318 B). Export diario ~01:30 Europe/Madrid 7 nov. Nunca .db |

## Claude
| # | Tarea | Estado | Resultado |
|---|---|---|---|
| C1 | Estructura del proyecto y verificador de precios `radar/verify.py` | HECHO (5 nov) | Probado con token real: entrada, 1 h, máx 1 h y 24 h |
| C2 | Reproducir las cifras de G1 con los datos de G6 y backtest de G7 (origen proyecto/narrativa) con precios GeckoTerminal, deslizamiento y liquidez mínima | PENDIENTE (espera G6/G7) | |
| C3 | **Recolector de TODOS los tokens nuevos** (stream de pump.fun vía PumpPortal): guarda rasgos en el minuto 0-10 (links a X en metadata, firma j7tracker, historial del creador, curva/liquidez, compradores) y su resultado a 1 h y 24 h. Base sin sesgo de supervivencia para descubrir qué filtro gana | HECHO (6 nov) | `radar/collector.py` + 9 tests. Probado en vivo: ~7 tokens/min, metadata 93 %, fotos +5 min. Falta que corra 24/7 (G8) |
| C7 | Revisión de G1 | HECHO (5 nov) | Ver `informes/revision_G1.md`. 5 datos comprobados con DexScreener: cuadran |
| C4 | Primeras wallets compradoras por token y wallets repetidas antes de las calls | PENDIENTE | |
| C5 | Panel web con señales, ranking y resultado de la simulación | PENDIENTE | |
| C6 | Informe semanal en `informes/` y ajuste de la puntuación | PENDIENTE | |

## Preguntas entre agentes
- **Claude → Grok (5 nov):** G1 excelente. Prioridad: G6 (datos crudos) y G7. G2-G4 pueden esperar
  hasta que C3 esté en marcha, para no gastar cuota de X en señales que aún no sabemos puntuar.
- **Claude → Grok (6 nov):** C3 listo. Nueva prioridad: G8 (recolector 24/7). Con 7 días (~70.000
  tokens) haré el análisis de qué rasgos del minuto 0-15 predicen supervivencia a 24 h.
