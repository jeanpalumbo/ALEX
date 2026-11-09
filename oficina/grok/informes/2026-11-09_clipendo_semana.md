# Informe semanal Clipendo — semana 3–9 nov 2026

Generado: lunes 2026-11-09 ~10:10 Europe/Madrid · Grok (Clipendo)

## Fuentes
- **Buffer** (MCP `user-Buffer--cuenta-2`, canal YouTube Clipendo `6ae3216b2f1f5ed6480cb269`): `list_posts` sent con métricas + `get_aggregated_post_metrics`. `metricsUpdatedAt` 2026-11-09 01:45 UTC = **02:45 Europe/Madrid 9-nov**. Las dos cifras cuadran: 27 posts, 60.532 views.
- **YouTube Analytics (Windsor, Claude)**: `oficina/shorts/metricas_2026-11-06_youtube_*.csv` y `oficina/claude/revisiones/2026-11-06_S1_metricas_youtube.md`. Solo cubre **29-oct → 3-nov**. Del 4 al 9-nov no hay datos YouTube en el repo.
- Diarios S4 (`oficina/shorts/diario/`) y revisiones de Claude del 6–8 nov.
- Las views de Buffer son un snapshot, no «views a 24 h». Los Shorts del 8-nov y 9-nov llevan menos de 24 h y **no son comparables**.

## Resumen
| Métrica | Valor |
|---|---|
| Shorts publicados (3–9 nov, fecha Madrid) | **27** (objetivo S1: ~10/día = 70) |
| Views Buffer, suma | **60.532** (media 2.242/Short) |
| Likes / comentarios | 820 / 10 |
| Eng. rate media Buffer | 1,37 % |
| Retención semanal | **NO COMPROBADO** (Windsor llega hasta 3-nov) |
| Suscriptores | **NO COMPROBADO** para la semana. Último dato: 20 suscriptores a 2026-11-06 (S1). El 3-nov el canal hizo +3 / −1 |
| Views YouTube de la semana | **NO COMPROBADO**. Solo hay Buffer |

### Por día (fecha Madrid de `sentAt`)
| Día | Shorts | Views Buffer (snapshot 9-nov 02:45) |
|---|---:|---:|
| 3-nov (lun) | 6 | 25.873 |
| 4-nov | 1 | 600 |
| 5-nov | 7 | 15.805 |
| 6-nov | 8 | 10.770 |
| 7-nov | 2 | 5.063 |
| 8-nov | 2 | 2.228 |
| 9-nov (hasta 00:00) | 1 | 193 (menos de 3 h) |

Las cifras de 6-nov y 7-nov son más altas que las de los S4 (5.979 y 3.276), porque ahora llevan más horas. Mejor del 7-nov: Rivers zoom 3.715, Auron reloj 1.348.

### Retención (solo 3-nov, YouTube real)
- Canal 3-nov: 17.829 views, 51 % engaged, retención media 83 %, 317 likes.
- Por Short, 3-nov, retención media más de 100 %: Rubius token 103 %, Grefg cofre 104 %.
- Retención 4–9 nov: **NO COMPROBADO**.

## Top 3 y peores 3 (views Buffer)
**Top 3**
| # | Short | Publicado (Madrid) | Views | Eng. |
|---|---|---|---:|---:|
| 1 | Rubius Se Queja en Fortnite por el TOKEN | 3-nov 22:00 | 14.202 | 1,94 % |
| 2 | Rubius REACCIONA mal en Fortnite | 5-nov 01:00 | 7.275 | 0,81 % |
| 3 | TheGrefg Abre un COFRE a la vez | 3-nov 15:30 | 4.673 | 0,92 % |

Los siguientes: Grefg «emociona» 4.059, Rivers zoom 3.715, Rubius gato 3.178.

**Peores 3** (dejo fuera los Shorts con menos de 24 h)
| # | Short | Publicado | Views |
|---|---|---|---:|
| 1 | Knekro TROLEA en WoW | 5-nov 22:00 | 120 |
| 2 | ElXokas alucina con un DESFASE en WoW | 5-nov 04:00 | 589 |
| 3 | Rubius Consigue el PIRATE Shop | 4-nov 13:00 | 600 |

Sin contar el criterio de 24 h, el Xokas «guild» del 9-nov 00:00 tiene 193 views, pero es demasiado pronto para juzgarlo.

## Lectura
- **Grefg + Rubius ≥ 7/10:** la semana fue 12 de 27 = **44 % de los Shorts**, bajo el 70 %. Sí aportaron el **67 % de las views** (40.648 de 60.532). Los tres mejores Shorts son suyos. Lo que menos rinde es lo que no es suyo: WoW de Knekro y Xokas, y los EN→ES.
- **Volumen:** 27 de 70 posibles. El 4-nov hubo 1 Short. El 7-nov hubo 2 y el 8-nov hubo 2 (13:04 Rubius WoW, 22:00 IlloJuan), más 1 a las 00:00 del 9-nov. El día 8-nov y el 9-nov quedaron muy por debajo del objetivo. Causa: pool de top-clips Twitch agotado + uso semanal al 94–95 % (tope 95 %), según los ESTADO y S6.
- **Discrepancia a revisar:** los informes internos decían «0 publicados el 8-nov». Buffer muestra 2 `sent` el 8-nov en Madrid (13:04 y 22:00) y 1 a las 00:00 del 9-nov. Ver los IDs `6af05b8a…`, `6af0d8f4…`, `6af0d8f6…`.
- **S5:** el Short Rubius WoW del 8-nov (13:04) y el Xokas WoW del 9-nov 00:00 llevan contenido de WoW. S5 dejó fuera «Knekro y WoW». Hay que comprobar si se aplicó la regla a la rutina de refill (sigue pendiente de actualizar desde el chat principal).
- **CTAs:** todos los posts de la semana llevan una pregunta en el texto. Comentarios: 10 en 60.532 views, así que la pregunta aún casi no mueve comentarios. Desde el 7-nov se añadió «Cuéntalo en comentarios». Ese texto va con 2 posts: los 2 del 7-nov, con 0 comentarios entre los 2. Efecto: **NO COMPROBADO**.
- **Mejor eng. no es mejor views:** los 3 de eng. alto de los últimos días (Xokas guild 3,63 %, Auron reloj 2,52 %) tienen pocas horas o pocas views. No sacar conclusiones.

## Qué cambia la semana siguiente (reglas S1/S3/S5)
1. **≥ 7/10 TheGrefg + Rubius** (preferencia, no filtro que pare la cola): priorizar reacciones/risa/queja de Grefg y Rubius de directos/VOD de últimos 7 días. El hueco de Knekro/WoW va a Rubius, TheGrefg, AuronPlay o Spreen. Sin WoW, sin tertulia.
2. **Retención:** nada de Shorts con retención < 50 % en 48 h por creador nuevo = parar. Gancho en el segundo 0, clips de 15–30 s. Pedir a Claude la extracción de Windsor del 4–9 nov para medir retención y subs reales (hoy NO COMPROBADO).
3. **CTAs:** mantener pregunta en descripción y al final del clip. Usar «Cuéntalo en comentarios» y medir comentarios por 1.000 views frente a la base de esta semana (10 comentarios / 60.532 views). Series y «Parte 2» si > 3.000 views (candidatos: Rubius token, Rubius Fortnite, Grefg cofre).
4. **Uso:** semana cerrada al ~95 %; el reset es el **miércoles 11-nov 12:00 Europe/Madrid**. Hasta entonces, solo clips activos, objetivo 5/día (4 si falta buen material) en 13:00, 15:30, 17:30, 20:00, 21:00 Madrid, con una búsqueda diaria y reutilizando transcripciones. Tras el reset, decidir con Jean/Piero si se vuelve a 13/día; no se vuelve a 13 sin aviso.
5. **Fallos de producción:** si el día sigue por debajo del mínimo a las 12:00, avisar una sola vez (sin pings repetidos).
