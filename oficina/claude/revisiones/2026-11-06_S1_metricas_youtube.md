# S1 — Métricas reales de YouTube Shorts (Clipendo) · 2026-11-06

**Fuente:** YouTube Analytics API vía Windsor.ai (cuenta del canal Clipendo), sacado por Claude el
2026-11-06. **Periodo pedido:** últimos 28 días (2026-10-09 → 2026-11-05). **Datos disponibles:**
hasta 2026-11-03. YouTube Analytics va con 2–3 días de retraso, así que el 4 y el 5 de noviembre
todavía no salen. Antes del 2026-10-29 el canal tiene 0 views.

Este informe sustituye a la parte de YouTube Studio de S1. Lolo: no hace falta entrar en Studio.

## Archivos
| Archivo | Qué tiene |
|---|---|
| `oficina/shorts/metricas_2026-11-06_youtube_por_video.csv` | 1 fila por Short: id, título, fecha de publicación, views, engaged views, minutos vistos, duración media vista, retención media %, likes, comentarios, compartidos, subs ganados/perdidos (total del periodo) |
| `oficina/shorts/metricas_2026-11-06_youtube_diario.csv` | Total del canal por día: views, engaged views, minutos, retención, likes, comentarios, compartidos, subs ganados/perdidos |
| `oficina/shorts/metricas_2026-11-06_youtube_video_dia.csv` | Cada Short por día: views, engaged views, retención, likes, subs ganados |

## Glosario
- **views**: reproducciones de Shorts (desde marzo 2025 cuentan también las repeticiones, sin tiempo mínimo).
- **engaged_views**: views que pasan de los primeros segundos. Es lo más parecido a "se quedó en vez de deslizar". `engaged/views` ≈ % que **no** deslizó.
- **retencion_media_pct**: % medio del Short visto. Más de 100 % = la gente lo repite.

## Canal (foto a 2026-11-06)
- 20 suscriptores · 32 vídeos públicos · 66.689 views de por vida.
- En el periodo: **48.233 views**, 21.276 engaged views (44 %), 7.519 min vistos, 750 likes, 22 compartidos.
- Suscriptores: +20 / −4 = **+16 netos** (≈ 0,4 subs por cada 1.000 views).
- 23 Shorts tienen datos por vídeo y suman 43.678 views. Las ~4.555 views que faltan son de vídeos
  ya borrados (p. ej. los de estoicismo en inglés del 29-oct, que salen en Buffer pero ya no en YouTube).

## Por día (canal)
| Fecha | Views | Engaged | % engaged | Retención | Likes | Subs +/− |
|---|---:|---:|---:|---:|---:|---|
| 10-29 | 1.772 | 623 | 35 % | 54 % | 48 | +7 / 0 |
| 10-30 | 3.733 | 1.329 | 36 % | 87 % | 54 | +4 / 0 |
| 10-31 | 2.075 | 919 | 44 % | 55 % | 30 | 0 / 0 |
| 11-01 | 13.397 | 5.012 | 37 % | 55 % | 174 | +5 / −3 |
| 11-02 | 9.427 | 4.261 | 45 % | 78 % | 127 | +1 / 0 |
| 11-03 | 17.829 | 9.132 | 51 % | 83 % | 317 | +3 / −1 |

La tendencia sube: el 3-nov es el mejor día y además el de mejor "no deslizó" (51 %).

## Top 5 Shorts (views del periodo)
| Short | Views | % engaged | Retención | Likes |
|---|---:|---:|---:|---:|
| TheGrefg sobrevive con UNA vida 😂 | 6.397 | 53 % | 99 % | 139 |
| Rubius Se Queja en Fortnite por el TOKEN 😤 | 4.284 | 48 % | 103 % | 87 |
| Grefg Grita por una Pantalla de CARGA 😭 | 3.668 | 45 % | 82 % | 43 |
| TheGrefg Abre un COFRE a la vez 😂 | 2.557 | 45 % | 104 % | 18 |
| Este Gato Arañó a Rubius SIN Avisar 😾 | 2.529 | 40 % | 83 % | 25 |

## Peores 5 (views del periodo)
| Short | Views | % engaged | Retención |
|---|---:|---:|---:|
| ¿Quién No Tiene Netflix en 2026? Xokas Sobre la Velada 🤔 | 109 | 39 % | 63 % |
| Spreen Abandona a Todos por el Team Mafia en el Dedsafío 😱 | 134 | 37 % | 51 % |
| AuronPlay Se Pone una Cabeza CALVA 😂 | 1.103 | 60 % | 39 % |
| Grefg Gana Su Torneo de Clash Royale por Un Segundo | 1.113 | 44 % | 45 % |
| Nadie Le Gana a Westcol en el PvP del Dedsafío 😤 | 1.130 | 18 % | 49 % |

## Lo que dicen los datos (correlación, no causa demostrada)
1. **La retención manda.** Los 5 Shorts que más views tienen pasan del 80 % de retención. Los que
   se quedan por debajo del 50 % (Spreen Murder Mystery, Westcol Kings League, AuronPlay CALVA,
   Grefg Clash Royale) se paran en unas 1.100–1.400 views.
2. **Grefg y Rubius son lo que mejor va.** Ocupan los 5 primeros
   puestos. Los clips de "opinión/tertulia" (Xokas Velada/Netflix, Westcol Kings League) retienen
   peor.
3. **Westcol PvP Dedsafío:** solo el 18 % no desliza. El gancho del primer segundo falla.
4. **Casi nadie comparte ni comenta:** 22 compartidos y 4 comentarios en 48 mil views. Falta una
   llamada a comentar o una pregunta en el clip.
5. **Pocos suscriptores (0,4 por cada 1.000 views).** Para monetizar hacen falta 1.000 subs, así
   que hay que dar un motivo para suscribirse (serie, "parte 2", nombre de canal reconocible).
6. Hubo 2 clips publicados el 30-oct por la mañana (13:00 y 15:00 UTC) que se quedaron por debajo
   de 140 views, pero el de las 12:00 UTC del 3-nov hizo 1.773. **NO COMPROBADO** que la hora
   influya; hacen falta más días.

## Lo que no da esta fuente
- Las fuentes de tráfico por vídeo (feed de Shorts, búsqueda…) existen en la API, pero no se han
  sacado en esta pasada. Se pueden pedir si Lolo las necesita.
- La duración en segundos de cada vídeo: tomarla del CSV de Buffer (`metricas_2026-11-06.csv`).
- Los días 4 y 5 de noviembre: saldrán en la próxima extracción.

## Notas técnicas
- La suma por día de algunos vídeos difiere en 1–11 views del total por vídeo. Son ajustes de la
  propia API de YouTube, no un error de copia.
- Hay valores de retención por día por encima de 100 % (hasta 385 % con 7 views) y likes de −1 en
  algún día (likes retirados). Son datos reales de la API: con tan pocas views no son significativos.
