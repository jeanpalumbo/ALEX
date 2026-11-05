# Tablero de tareas

Reglas: cada agente solo edita lo suyo (ver README). Al terminar una tarea, cambia su estado y
añade la fecha y una línea de resultado. Las preguntas para el otro agente van en la sección final.
Estados: PENDIENTE · EN CURSO · HECHO · BLOQUEADO (con motivo).

## Grok Bot
| # | Tarea | Estado | Resultado |
|---|---|---|---|
| G1 | Investigación inicial en X (ver `investigacion/ENCARGO_G1.md`) | PENDIENTE | |
| G2 | Rutina "Vigía de origen" cada 15 min escribiendo en `data/senales.csv` | PENDIENTE | |
| G3 | Rutina de resultados cada 6 h (precio a 1 h y 24 h en `data/senales.csv`) | PENDIENTE | |
| G4 | Ranking semanal de fuentes en `data/callers.csv` (incluidos fracasos) | PENDIENTE | |
| G5 | Histórico: 200-500 posts de 3-4 bots de origen (todas sus CAs, también las muertas) con hora exacta, en `data/historico_bots.csv` | PENDIENTE | |

## Claude
| # | Tarea | Estado | Resultado |
|---|---|---|---|
| C1 | Estructura del proyecto y verificador de precios `radar/verify.py` | HECHO (5 nov) | Probado con token real: entrada, 1 h, máx 1 h y 24 h |
| C2 | Backtest del histórico G5 con deslizamiento y liquidez mínima | PENDIENTE (espera G5) | |
| C3 | Escáner de origen: stream de creación de pump.fun (PumpPortal) + filtros + aviso Telegram | PENDIENTE | |
| C4 | Primeras wallets compradoras por token y wallets repetidas antes de las calls | PENDIENTE | |
| C5 | Panel web con señales, ranking y resultado de la simulación | PENDIENTE | |
| C6 | Informe semanal en `informes/` y ajuste de la puntuación | PENDIENTE | |

## Preguntas entre agentes
- (vacío)
