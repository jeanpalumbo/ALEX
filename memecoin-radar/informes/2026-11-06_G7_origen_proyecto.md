# G7 — Muestra origen proyecto/narrativa (6 nov 2026)

Zona: Europe/Madrid. Solo lectura X / datos locales. Sin spam ni interacción.

## Entrega

- Archivo: `data/origen_proyecto.csv`
- Filas: **323** CAs únicas (≥100)
- Columnas pedidas: `ca,symbol,hora_creacion_utc,fuente_origen,tipo,min_desde_creacion,seguidores_cuenta,edad_cuenta_dias,menciones_x_primera_hora,notas`

## Método (sistemático)

1. **Fuente principal:** `collector.db` local (G8, tokens del **2026-11-06** UTC) — NO subido.
2. Candidatos: metadata `twitter_kind=tweet` con URL `/status/{id}` cuyo **snowflake** cae en ventana **[-2, +10] min** respecto a `created_utc` del token (permite tweet de narrativa justo antes del deploy).
3. Verificación: `x.get_posts_by_ids` (lotes) → `created_at` real + `public_metrics` del autor.
4. Excluidos handles de scanners conocidos (bitecong, SolanaMemesScan, AutorunAlert, PumpWatch1, solhousesignals, SolTokenScan, AiSolanaKols, dex_kolwatcher, SenatorLTD, Larpcheckbot).
5. **tipo:**
   - `narrativa` — tuit enlazado en metadata al crear (definición G1 “tweet de narrativa / metadata”).
   - `proyecto` — handle ≈ symbol, o ejemplos G1 DEMOSTRADO de cuenta de proyecto.
6. **Extras G1** (últimos 14 días, manual DEMOSTRADO): HIGH, INU, AMD, 1CALL, WEALTH — ver `investigacion/ejemplos_origen_cadena.csv` + informe G1.
7. `menciones_x_primera_hora`: **NO COMPROBADO** (haría falta 1 búsqueda X por CA; fuera de alcance en esta pasada).
8. Muestreo: **todos** los candidatos verificados del día de collector + G1; no se filtró por supervivencia (incluye los que mueren).

## Conteos

| Clase | N |
|---|---:|
| Total | 323 |
| tipo=narrativa | ~307 |
| tipo=proyecto | ~16 |
| Con followers vía X API | mayoría collector + 5 G1 |
| Tweet texto contiene **esta** CA | muy pocos (~4 en collector); el resto es narrativa_metadata sin CA en texto (anotado en `notas`) |
| Días cubiertos | 2026-11-03, 05, 06 (collector solo tiene ~6 nov) |

## Limitaciones / NO COMPROBADO

- **Ventana 14 días incompleta:** el recolector G8 solo cubre desde ~01:18 Europe/Madrid del 6 nov. No hay DB histórica de todos los pump.fun de 14 días → la masa de la muestra es **un día** (6 nov) + 5 casos G1 previos.
- La mayoría de `narrativa` son tuits de tema/meme **enlazados en metadata** en el minuto 0, no necesariamente posts que pegan la CA. G1 trata eso como origen “narrativa/metadata”; si Claude quiere solo posts con CA en texto, filtrar `notas` por `tweet_contains_this_ca=yes` o `G1 DEMOSTRADO`.
- `menciones_x_primera_hora` = NO COMPROBADO.
- Algunos status IDs devolvieron 404 (borrados); esos candidatos se omitieron.
- No se usaron bots de interacción ni se publicó nada en X.

## Fuentes

- `/workspace/ALEX/memecoin-radar/data/collector/collector.db` (local)
- X MCP `get_posts_by_ids` / `get_users_by_usernames`
- `investigacion/G1_informe.md`, `ejemplos_origen_cadena.csv`
- `data/callhunter/` (contexto; no aportó ≥100 orígenes proyecto no-bot ≤10 min por sí solo)

## Collector

No detenido. Watchdog/collector siguen vivos durante G7.
