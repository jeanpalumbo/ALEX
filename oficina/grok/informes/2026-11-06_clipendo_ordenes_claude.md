# Clipendo — adopción órdenes Claude S1 · 2026-11-06 ~14:10 Europe/Madrid

Leído entero: `oficina/claude/revisiones/2026-11-06_S1_metricas_youtube.md`.

## Estado Buffer (cuenta-2, YT Clipendo `6ae3216b2f1f5ed6480cb269`)
- En cola **scheduled**: **5** (hoy: Knekro 14:30, Rubius 16:00, KaiCenat 17:30, IShowSpeed 19:00, Jynxzi 20:30 Madrid).
- **Sent hoy**: **1** (Spreen 13:00 Madrid).
- Draft viejo: 1 (caseoh, no programar).
- Objetivo día: **~10** Shorts. Hoy cubiertos 6 si salen los scheduled; faltan huecos noche → refill 21:00.
- Nota: cola actual mezcla US EN→ES (Kai/Speed/Jynxzi) y no Grefg; **a partir de ahora ≥7/10 Grefg+Rubius reacción**.

## Routines Lolo (clips)
| Nombre | Horario (Europe/Madrid) | Qué hace | Estado |
|---|---|---|---|
| Clips: refill Buffer queue | ~10:00, 12:00 y 21:00 (≈21 runs/semana en usage) | Busca/edita/sube Shorts a Buffer YT Clipendo hasta ~10/día | **Activa** (usage 7d) |
| Clipendo: resumen diario Piero | 21:05 (propuesto; no chocar con refill :00) | 1 línea a Piero: clips hoy, views ayer, mejor clip | **Pendiente crear** (UpdateRoutine solo en agente principal) |

PH y G8 routines ya borradas (Hunter/Gold).

## Reglas aplicadas al pipeline (próximos refills)
Ver store `clipendo/REGLAS_CLAUDE_2026-11-06.md`. S1 sigue EN CURSO (métricas Claude). No Studio.

## BLOQUEADO / NO COMPROBADO
- **BLOQUEADO (subagente):** no tengo UpdateRoutine aquí; el agente principal debe (1) actualizar el prompt de «Clips: refill Buffer queue» con las reglas S1 y (2) crear «Clipendo: resumen diario Piero».
- **NO COMPROBADO:** influencia de la hora de publicación (log 14 días).
