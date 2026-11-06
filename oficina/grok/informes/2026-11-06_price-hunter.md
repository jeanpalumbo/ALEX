# Price Hunter — take-over 2026-11-06

Fuente: take-over 2026-11-06 (Europe/Madrid). Bot responsable a partir de este corte: **Hunter** (Grok Bot); antes, Lolo. Solo nombres de variables; sin valores ni URLs de webhook.

## Resumen
- Bot responsable: **Hunter** (Grok Bot). Antes: Lolo.
- Código vivo: `/workspace/price-hunter/` en el box compartido de Grok Bot (origen repo privado `jeanpalumbo/socio-backup`). **No** está en ALEX.
- Monitor: `python3 run.py monitor` + `watchdog.sh` cada ~60 s (MAX_AGE 180 s).
- Estado al take-over: monitor vivo; `.webhook.env` apunta al webhook de Hunter (nombres de vars: `PH_WEBHOOK_URL`, `PH_WEBHOOK_KEY`; sin valores).

## Routines (Hunter)

| Nombre | Folder id | Trigger | Qué hace |
|---|---|---|---|
| **Price Hunter: alertas al chat** | `price-hunter-alertas-al-chat` | Webhook | Al recibir deals: ⚡ MIRA YA si ≥75 % o confianza alta; luego veredicto COMPRA / NO COMPRES / DUDOSO en el chat de Hunter (Jean/Piero). |
| **Price Hunter: refrescar X** | `price-hunter-refrescar-x` | Cada 30 min Europe/Madrid (±5 min) | Escribe JSON API v2 en `data/x_raw/`. Silencio si no hay COMPRA / MIRA YA. |

## Fuentes que lee el monitor

| Fuente | Intervalo aprox. | Notas |
|---|---|---|
| chollometro | 180 s | RSS + fichas |
| pepper_eu | 180 s | errores de precio UE |
| amazon_cm | 90 s | feeds Amazon |
| x_saved | 120 s | solo ficheros nuevos en `data/x_raw` |
| steam | 300 s | API Steam ES |
| camel_drops | 300 s | RSS desactivado; camel como ficha ASIN en refcheck |
| telegram | 300 s | canales; envío Telegram al chat aparcado |

Alertas al chat: casi solo **Amazon.es** (`amazon_only: true`).

## Filtros notifier (vigentes en `config.json`)
- `amazon_only`: true
- `min_discount` / `always_alert_min_discount`: 0.70 (≥70 % siempre avisa)
- `below_threshold_resale`: true — si <70 %: `below_threshold_min_discount` 0.50, `below_threshold_min_ref_eur` 100, `below_threshold_min_saving_eur` 40
- `device_promo` (Blink/Ring/Echo/Kindle/Fire TV): `device_promo_min_discount` 0.80
- levels: alta, media; `require_ref_status`: verificada, respaldada
- `max_total_eur` notifier: 200; `min_interval_s`: 900; `max_batch`: 5
- `purchase_policy`: mode `enforce`, `max_total_eur` 200, `free_shipping_only` true, `cap_exempt_discount` 0.75

## Cómo avisa
POST al webhook de la routine → chat de Hunter. Cola: `data/pending_webhook.jsonl`.

## Claves (solo nombres)
- `.webhook.env`: `PH_WEBHOOK_URL`, `PH_WEBHOOK_KEY`
- Opcional apagado: `X_BEARER_TOKEN` (se usa lectura pública de X en la routine)

## Criterio COMPRA (humano en routine)
Error real + vendedor fiable (ideal Amazon) + margen de reventa claro; ahorro ~20 € = NO COMPRES.
