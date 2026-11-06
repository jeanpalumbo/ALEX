# Capturas YouTube Studio — S1 (2026-11-06)

## Estado

**No hay capturas de YouTube Studio.**

Motivo: **BLOQUEADO por 2FA Google**. Jean canceló el login a accounts.google.com / YouTube Studio
(@clipendo) porque el flujo pediría verificación 2FA y no se puede completar de forma fiable
desde el bot.

## Sustituto (sin Studio)

| Fuente | Qué aporta | Dónde |
|---|---|---|
| **Buffer MCP** `user-Buffer--cuenta-2` | Posts enviados al canal YouTube Clipendo + métricas por post (views, reactions/likes, comments, engagement rate) + agregado | org `6ae270cec8fa19ee6d863b3d`, channelId `6ae3216b2f1f5ed6480cb269` → CSV `oficina/shorts/metricas_2026-11-06.csv` |
| **Snapshots públicos** `/workspace/growth/proto/perf_tracker/snapshots.csv` | Views/likes/título/duración públicos canal `clipendo` (RSS/perf_tracker) | Mismo CSV (columnas `video_id_publico`, `views_snapshot`, `likes_snapshot`) |

## Lo que Solo Studio daría (aquí: NO COMPROBADO)

- % que siguió viendo vs. deslizó
- Retención media
- Fuente de tráfico (feed Shorts / búsqueda / …)
- Suscriptores ganados por vídeo
- Totales diarios del canal desde Analytics
- Export “últimos 90 días” completo (Buffer Free ≈ **31 días** de Insights)

Ver informe: `oficina/grok/informes/2026-11-06_S1.md`.
