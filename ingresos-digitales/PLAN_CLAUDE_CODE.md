# PLAN DE EJECUCIÓN — Ingresos digitales (KDP, X, Etsy, Pinterest)

> **Para Claude Code.** Este documento es el encargo completo. Léelo entero antes de empezar.
> Idioma: coordinación en español; código, nombres de archivos, variables y comentarios en inglés.
> Dueño del proyecto: Piero. Trabaja a turnos, tiene poco tiempo: todo debe quedar listo para que él solo **revise y apruebe**.

---

## ▶ EMPIEZA AQUÍ — Plan de acción desde el 18 de octubre de 2026

**Este orden manda sobre cualquier otro orden del documento.** Las prioridades se decidieron después de validar con datos reales de Amazon (ver sección 11).

### Prioridad 1 — Plan C: libro KDP Vol. 1 "Recuerdos de España" (objetivo: a la venta antes de noviembre, campaña de Navidad)

| Día | Quién | Tarea | Hecho cuando |
|---|---|---|---|
| Día 1 | Claude Code | Crear repo (sección 2, añadiendo `plan_c_kdp/`), `pyproject.toml`, tests base | El repo arranca y los tests pasan |
| Día 1 | Piero | Abrir cuenta en kdp.amazon.com y completar datos fiscales y de cobro (solo él puede) | Cuenta activa |
| Días 1-3 | Claude Code | `plan_c_kdp/wordsearch`: generador de sopas de letras con palabras en horizontal/vertical/diagonal, sin palabras rotas ni acentos que confundan (decidir y documentar si se usan mayúsculas sin tildes), con solución verificable automáticamente | Test que comprueba que cada palabra está en su cuadrícula y en la solución |
| Días 1-3 | Claude Code | `plan_c_kdp/themes`: ~100 temas de nostalgia (sección 11) con 12-18 palabras cada uno y una frase introductoria por tema. Sin letras de canciones ni textos con copyright | YAML revisable por Piero |
| Días 3-4 | Claude Code | `plan_c_kdp/interior`: PDF interior 8.5x11", letra muy grande, una sopa por página, soluciones al final. Verificar en la ayuda oficial de KDP los márgenes y sangrado vigentes antes de maquetar | PDF abre, fuentes incrustadas, márgenes correctos |
| Día 4 | Piero | Revisar el PDF: legibilidad y que los temas "suenen" a mayores españoles | Visto bueno o lista de cambios |
| Días 5-6 | Claude Code | `plan_c_kdp/cover`: portada completa (trasera + lomo + delantera) con la plantilla/calculadora de KDP según el nº de páginas; tipográfica o con imagen que aporte Piero (generada por él con ChatGPT, guardada en `assets/`) | PDF de portada al tamaño exacto |
| Día 6 | Claude Code | `plan_c_kdp/listing`: título, subtítulo, descripción, 7 palabras clave, categorías sugeridas y precio sugerido | `listing.md` listo para copiar |
| Día 7 | Piero | Subir a KDP a mano y marcar la declaración de IA que corresponda | Libro enviado a revisión |

### Prioridad 2 — Plan B: cuenta de X en inglés (en paralelo desde esta semana)

| Cuándo | Quién | Tarea |
|---|---|---|
| Semana 1 | Piero | Comprobar en la página de planes si el Premium de X incluye Grok Bot (la documentación de Cursor menciona una "X Subscription" con Premium que lo incluye). Contratar lo necesario. Crear la cuenta de X en inglés |
| Semana 1 | Piero | Crear el bot "Trend Scout" con el texto de la sección 5.2 (nichos iniciales: stories, fun facts, tech/AI, sports, true crime/news) y la Google Sheet |
| Semana 2 | Claude Code | `plan_b_x`: `ingest` → `drafts` (en inglés) → `review` → cron + aviso por Telegram |
| Semanas 2-3 | Piero | Publicar 3-5 posts/día revisados. Al final de la semana 3, elegir nicho con los datos |

### Prioridad 3 — después de lanzar el Vol. 1 (noviembre)

- Plan C: Vol. 2 "Años 60" reutilizando el generador; después Vol. 3 "Años 70" y Vol. 4 "Años 80".
- Plan A (Etsy) y Plan E (Pinterest): solo cuando lo anterior funcione sin supervisión.
- Plan D (stock): opcional.

### Revisiones con números

- **Finales de noviembre:** ventas del Vol. 1 (panel de KDP) y crecimiento en X (seguidores, impresiones).
- **Mediados de diciembre:** decidir si se duplica KDP (más volúmenes) y qué nicho se queda en X.

### Cosas que Claude Code NO necesita para empezar

Nada de cuentas ni claves para la Prioridad 1: todo el libro se genera en local. Las imágenes, si hacen falta, las aporta Piero (ChatGPT) en `assets/`. Si no hay `ANTHROPIC_API_KEY`, Claude Code puede escribir los temas y textos directamente en la sesión y guardarlos en YAML/Markdown.

---

## 0. Reglas no negociables (aplican a todo el proyecto)

1. **Nada se publica solo.** Etsy: los anuncios se crean como **borrador** (draft). X: el sistema **nunca** publica; solo genera borradores para que Piero los publique o programe a mano desde la web de X.
2. **Nada de evadir detección de plataformas.** No simular comportamiento humano, no rotar IPs, no automatizar el navegador para publicar en X.
3. **Contenido original.** Prohibido copiar textos, imágenes o posts de otros. Las tendencias se usan como inspiración (tema, formato, gancho) y se reescriben desde cero.
4. **Ficción marcada como ficción** en X. No inventar hechos sobre personas reales, ni noticias falsas, ni datos médicos/financieros falsos.
5. **Sin propiedad intelectual ajena** en Etsy: nada de personajes Disney/Marvel, marcas, logos, canciones, ni temas tipo "Rapunzel quinceañera".
6. **Divulgación de IA en Etsy** obligatoria cuando el diseño use IA generativa (casilla en el formulario + línea en la descripción). Esto lo hace Piero al revisar el borrador; el sistema debe recordárselo en el checklist.
7. **Secretos** solo en `.env` (nunca en el repo, nunca en logs). Crear `.env.example` con todas las variables vacías.
8. **Coste controlado:** cada script que llame a una API de pago imprime al final cuántas llamadas hizo y el coste estimado.

---

## 1. Visión general

| | Plan A — Etsy | Plan B — Cuenta de X |
|---|---|---|
| Qué es | Tienda de plantillas digitales bilingües (inglés/español) para ceremonias católicas | Cuenta de X con contenido inspirado en lo que está en tendencia |
| Objetivo | ~100 €/mes netos (≈11 ventas/mes a ~12 $) | Crecer audiencia; monetizar más adelante |
| Automatización | Investigación → producto → textos → mockups → borrador en Etsy | Grok Bot detecta tendencias → este sistema genera borradores → Piero publica |
| Trabajo de Piero | Revisar borradores y pulsar publicar (~15 min por lote) | Revisar, retocar y programar posts (~15-20 min/día) |
| Coste fijo | 0 € (solo 0,20 $ por anuncio) | Suscripción con Grok Bot (desde ~20-30 $/mes) |

**Orden recomendado:** Plan A primero (semanas 1-3), Plan B en paralelo desde la semana 3, cuando Piero contrate Grok Bot.

**Planes adicionales** (secciones 9-13 al final): **E** pines de Pinterest que llevan tráfico gratis a Etsy y a enlaces de afiliado, **C** libros de actividades bilingües en Amazon KDP (reutiliza el nicho del Plan A), y **D** stock con IA (secundario). Orden global: **A → E → C → B → D**. La sección 9 lista todas las herramientas disponibles y para qué usar cada una.

---

## 2. Estructura del repositorio

```
ingresos-digitales/
├── README.md
├── .env.example
├── pyproject.toml            # Python 3.11+, deps gestionadas con uv o pip
├── shared/
│   ├── llm.py                # wrapper de Anthropic API (modelo, reintentos, coste)
│   ├── db.py                 # SQLite: data/app.db
│   └── config.py             # carga .env
├── plan_a_etsy/
│   ├── research/             # investigación de palabras clave
│   ├── catalog/              # definición de productos (YAML)
│   ├── generator/            # generación de DOCX/PDF editables
│   ├── copy/                 # títulos, etiquetas, descripciones bilingües
│   ├── mockups/              # imágenes del anuncio
│   ├── etsy_api/             # OAuth + creación de borradores
│   ├── review/               # informe HTML de revisión para Piero
│   └── cli.py                # comandos: research | build | upload | report
├── plan_b_x/
│   ├── ingest/               # lee el informe de tendencias de Grok Bot
│   ├── drafts/               # genera posts originales
│   ├── review/               # página HTML diaria con los borradores
│   └── cli.py                # comandos: ingest | draft | review
├── data/                     # app.db, salidas (en .gitignore)
└── tests/
```

`shared/llm.py`: usar el SDK oficial `anthropic`. Modelo por defecto `claude-sonnet-5-5` (configurable con `LLM_MODEL`). Reintentos con backoff, límite de tokens por llamada, y registro de tokens/coste en SQLite.

---

## 3. FASE 0 — Requisitos previos (tareas de Piero, Claude Code debe pedírselas)

Claude Code: antes de escribir código de integración, muestra esta lista a Piero y espera a que confirme cada punto. Empieza por lo que no depende de credenciales (generador de producto y textos).

### Para Plan A
- [ ] Abrir tienda en Etsy (idioma español, país España, moneda EUR). Configurar cobros.
- [ ] Crear una app en el portal de desarrolladores de Etsy → obtener **keystring** y **shared secret**. Registrar la URL de callback `http://localhost:3003/oauth/callback`.
- [ ] Clave de Anthropic API (`ANTHROPIC_API_KEY`).
- [ ] (Opcional) Cuenta de Canva gratuita, para versiones Canva en una fase posterior.
- [ ] Consultar con un gestor cómo declarar estos ingresos (Piero está empleado por cuenta ajena). Etsy informa a Hacienda a partir de 30 ventas o 2.000 € al año.

### Para Plan B
- [ ] Contratar acceso a Grok Bot (la vía más barata es un plan de pago de Cursor o SuperGrok; comprar desde web, no desde la app de iPhone, que es más cara).
- [ ] Cuenta de X para el proyecto (o dos, si se decide ir en dos idiomas).
- [ ] Una Google Sheet compartida donde Grok Bot dejará el informe diario de tendencias, y una cuenta de servicio de Google con acceso de lectura/escritura a esa hoja (`GOOGLE_SERVICE_ACCOUNT_JSON`, `TRENDS_SHEET_ID`).

`.env.example` debe incluir: `ANTHROPIC_API_KEY, LLM_MODEL, ETSY_KEYSTRING, ETSY_SHARED_SECRET, ETSY_SHOP_ID, ETSY_REDIRECT_URI, GOOGLE_SERVICE_ACCOUNT_JSON, TRENDS_SHEET_ID, X_ACCOUNT_LANG`.

---

## 4. PLAN A — Tienda Etsy de plantillas bilingües

### 4.1 Producto y nicho

**Nicho:** programas y papelería bilingüe (inglés + español) para ceremonias católicas. Comprador principal: familias hispanas en EE. UU.

Motivo (investigado oct 2026): las invitaciones de boda bilingües ya están saturadas (anuncios con miles de reseñas). Los programas de misa/ceremonia bilingües se venden pero con pocos competidores fuertes.

**Catálogo inicial (10 productos × 2-3 estilos = 20-30 anuncios):**

| # | Producto | Formato |
|---|---|---|
| 1 | Programa de misa de bautizo / Baptism program | Tarjeta plegada 5x7" |
| 2 | Programa de primera comunión / First Communion program | Tarjeta plegada 5x7" |
| 3 | Programa de misa de boda / Catholic wedding mass program | Librillo 8 págs |
| 4 | Programa de misa de quinceañera | Librillo 8 págs |
| 5 | Programa de funeral / Celebration of life (católico) | Tarjeta plegada 8.5x11" |
| 6 | Cronograma de boda / Wedding timeline | 5x7" |
| 7 | Cartel de bienvenida / Welcome sign | 18x24" y 24x36" |
| 8 | Tarjetas de mesa y menú bilingües | 4x6" |
| 9 | Recordatorio / Prayer card (bautizo, comunión, funeral) | 2.5x4.25" |
| 10 | Pack completo (bundle) de boda: programa + timeline + menú + welcome sign | ZIP |

Estilos visuales (sin IP ajena): minimal blanco/negro, floral acuarela, talavera/azulejo, verde eucalipto, dorado clásico.

### 4.2 Módulo `research` — validar palabras clave

- Usar Etsy Open API v3 `GET /v3/application/listings/active` con `keywords` (solo requiere la API key en formato `keystring:sharedsecret`, sin OAuth).
- Para cada palabra clave candidata guardar: `count` (nº de anuncios activos), distribución de precios (mín/mediana/máx), y `num_favorers` medio del top 25.
- Lista inicial de keywords (EN y ES) para cada producto del catálogo, p. ej. `bilingual baptism program`, `spanish english first communion program`, `programa de bautizo bilingue`, `catholic wedding program spanish english`.
- Puntuación: preferir `count < 5000` con precios medianos ≥ 8 $.
- Limitación conocida: la API v3 **no** da datos de ventas. Las ventas solo se estiman por reseñas visibles. No inventar cifras.
- Salida: `data/research_YYYYMMDD.csv` + tabla en SQLite. Comando: `python -m plan_a_etsy.cli research`.
- Respetar límites de la API (pausas entre llamadas, reintento ante 429).

**Criterio de aceptación:** CSV con ≥ 30 keywords puntuadas y una recomendación de las 10 mejores.

### 4.3 Módulo `catalog`

- Un YAML por producto en `plan_a_etsy/catalog/` con: id, tipo, tamaño, páginas, secciones de texto (en EN y ES), estilos, precio objetivo.
- Los textos litúrgicos deben ser genéricos y de dominio público o redactados desde cero (estructura típica: entrada, liturgia de la palabra, lecturas, ritos, bendición final). **No copiar** textos de misales con copyright; usar marcadores editables como `[Primera lectura / First Reading]`.

### 4.4 Módulo `generator` — el producto descargable

Entregable por anuncio (ZIP):
1. **DOCX editable** (python-docx) — se abre en Word y Google Docs.
2. **PDF con campos rellenables** (AcroForm; reportlab o pypdf) para quien no tenga Word.
3. **PDF de instrucciones bilingüe** (cómo editar, imprimir, tamaños de papel, recomendaciones de imprenta).

Requisitos:
- Plantillas con Jinja2 + estilos por tema; tipografías con licencia libre para uso comercial (Google Fonts con OFL) incrustadas.
- Márgenes de sangrado/seguridad correctos para imprenta.
- Comando: `python -m plan_a_etsy.cli build --product baptism_program --style talavera`.
- Tests: el PDF abre, los campos son editables, el DOCX no tiene errores, el ZIP pesa < 20 MB.

**Criterio de aceptación:** 1 producto completo en 3 estilos que Piero valida abriéndolo en su PC.

### 4.5 Módulo `copy` — textos del anuncio

Con `shared/llm.py` generar por anuncio:
- **Título** (≤ 140 caracteres) con la keyword principal al inicio.
- **13 etiquetas** (≤ 20 caracteres cada una), mezcla EN/ES.
- **Descripción** bilingüe: qué incluye, formatos, tamaños, cómo se edita, "producto digital, no se envía nada físico", y la **línea de divulgación de IA** si aplica.
- Precio sugerido según el research.
- Validador: longitud, sin marcas registradas, sin promesas falsas.

### 4.6 Módulo `mockups` — imágenes del anuncio

- Hasta 10 imágenes por anuncio; mínimo 5: portada, detalle, todas las páginas, "qué incluye", instrucciones.
- Generación determinista con Pillow: renderizar páginas del PDF (pdf2image) y componerlas sobre fondos.
- Fondos/escenas: si en la sesión está disponible el conector de **Higgsfield**, úsalo para generar escenas de fondo (mesa de boda, iglesia desenfocada, flores) y reutilízalas. Si no está disponible, usar fondos lisos/texturas generadas con código.
- Formato 2000x1600 px aprox., JPG optimizado.

### 4.7 Módulo `etsy_api` — subida como borrador

Flujo verificado en la documentación oficial de Etsy (Listings Tutorial):
1. OAuth 2.0 Authorization Code con PKCE, scopes `listings_r listings_w shops_r`. Servidor local en el puerto 3003 para el callback. Guardar refresh token en `.env`/SQLite cifrado o en el keychain del sistema.
2. `POST /v3/application/shops/{shop_id}/listings` → **createDraftListing** con `type="download"`, `who_made`, `when_made`, `taxonomy_id` (obtener con seller-taxonomy), precio, título, descripción, etiquetas, `quantity`.
3. `POST .../listings/{listing_id}/images` → uploadListingImage (en orden).
4. `POST .../listings/{listing_id}/files` → uploadListingFile con el ZIP.
5. **No activar** el anuncio. Queda en borrador.

- Librería opcional: `etsyv3` o `etsy-python` (PyPI), o llamadas HTTP directas con `httpx`. Elegir la que funcione; verificar endpoints contra la referencia oficial antes de implementar.
- Coste: 0,20 $ por anuncio al publicarlo (lo cobra Etsy al activar).
- Comando: `python -m plan_a_etsy.cli upload --batch 2026-W43`.

### 4.8 Módulo `review` — lo que ve Piero

Página HTML local (`data/review_<batch>.html`) con, por anuncio: imágenes, título, etiquetas, descripción, precio, enlace al borrador en Etsy y **checklist**:
- [ ] Revisé el producto descargable
- [ ] Marqué "usé IA generativa" si aplica y elegí "Designed by"
- [ ] Sin marcas ni personajes ajenos
- [ ] Publicar

### 4.9 Ritmo y roadmap Plan A

| Semana | Entregable |
|---|---|
| 1 | Repo, `shared/`, `research` funcionando, top 10 keywords |
| 2 | `generator` + `copy` para 3 productos × 2-3 estilos; Piero valida calidad |
| 3 | `mockups` + `etsy_api` + `review`; primer lote de 5 borradores publicado por Piero |
| 4-8 | 5 anuncios nuevos por semana (no más: Etsy penaliza la producción en masa) |
| 8 | Revisión con datos (ver 4.10) |

### 4.10 Métricas y decisión

`python -m plan_a_etsy.cli report` (requiere scope `transactions_r` si se quieren ventas vía API; si no, Piero introduce las ventas a mano): anuncios activos, visitas, favoritos, ventas, ingresos netos.

Cuentas de referencia (no garantía): precio ~12 $ → ~9 € netos tras comisiones (0,20 $ anuncio + 6,5 % transacción + 4 % + 0,30 € pago + 0,88 % regulatoria). 100 €/mes ≈ 11 ventas/mes.

Umbrales sugeridos para decidir en la semana 8 (ajustables):
- ≥ 5 ventas acumuladas → duplicar catálogo en los productos que venden.
- 1-4 ventas → mejorar fotos/títulos de los anuncios con más visitas y seguir 4 semanas.
- 0 ventas con visitas → problema de anuncio (fotos/precio). 0 ventas sin visitas → problema de nicho/keywords → volver a `research`.

### 4.11 Tráfico gratis (fase posterior, semana 5+)

- **Pinterest:** un pin por anuncio. Ojo: con acceso "Trial" de la API, los pines creados solo los ve el dueño de la app; para que sean públicos hace falta acceso "Standard", que exige enviar un vídeo de demostración y esperar revisión manual. Hasta entonces: el sistema genera las imágenes y textos de los pines, y Piero los sube a mano (o con un programador como Postiz).
- Imágenes/vídeos de pin: con Higgsfield si está disponible.

---

## 5. PLAN B — Cuenta de X con tendencias

### 5.0 Decisiones de público (18 oct 2026)

- **Idioma: inglés, público de EE. UU.** Motivo: EE. UU. es el mayor público de X (~105 M de usuarios en 2026, frente a ~16,6 M en México) y X solo paga por visualizaciones de usuarios Premium, que previsiblemente se concentran ahí (deducción, no dato publicado). Claude escribe los posts en inglés nativo; Piero revisa y publica.
- **Nicho: se decide con datos.** Las 2 primeras semanas Trend Scout vigila 5 nichos a la vez (historias, curiosidades, tecnología/IA, deporte, sucesos). Después se elige el que más crezca y la cuenta se centra en una promesa clara.
- **Requisitos para cobrar (programa Original Content Rewards):** Premium activo, 18+, 500 seguidores verificados y 500.000 visualizaciones verificadas en el Home Timeline en 90 días (sin contar respuestas). Paga solo por visualizaciones de usuarios Premium en posts originales; no paga por likes. El contenido reproducido no cuenta y pedir likes/reposts de forma repetida expulsa del programa. X no publica la tarifa por visualización.

### 5.1 Flujo

```
Grok Bot (rutina diaria)  →  Google Sheet "trends"  →  plan_b_x (este repo)  →  página de revisión  →  Piero publica/programa en X
     detecta tendencias          informe estructurado        genera posts originales      borradores listos        a mano
```

Por qué Grok Bot: tiene conector nativo de X y de Google Sheets, y corre en la nube 24/7. Este repo no lee X directamente.

### 5.2 Configuración de Grok Bot (lo hace Piero, Claude Code le entrega este texto listo para pegar)

**Nombre del Bot:** Trend Scout
**Descripción/rol (pegar en Grok Bot):**
```
You are Trend Scout. Your only job is to find what is taking off on X right now in these niches: {NICHES}, in {LANGUAGE}.

Every day at 08:00 Europe/Madrid:
1. Search X for posts from the last 24h in the niches above with unusually high engagement relative to the author's normal posts.
2. Pick the 15 best. For each one, append a row to the Google Sheet "{SHEET_NAME}", tab "trends", with columns:
   date | niche | topic | format (thread/single/image/video/poll) | hook_pattern (describe the hook style, do NOT copy text) | why_it_works | post_url | views | likes | reposts | lang
3. Never copy the full text of any post into the sheet. Describe the pattern instead.
4. Do not post, like, follow, reply or DM on X. Read only.
5. If X or the Sheet is unavailable, write one row with niche="ERROR" and the reason, then stop.
```
**Rutina:** diaria 08:00 Europe/Madrid, en horario acotado para no gastar cuota (cada ejecución consume uso aunque no haya novedades).

### 5.3 Módulo `ingest`
- Leer filas nuevas de la pestaña `trends` (Google Sheets API, cuenta de servicio). Guardar en SQLite. Ignorar duplicados por `post_url`.

### 5.4 Módulo `drafts`
Para cada tendencia seleccionada (top 5-8 por día), generar con `shared/llm.py`:
- 1 post original siguiendo el **patrón** (gancho, formato), con tema y texto nuevos. Nunca reutilizar frases del original.
- Variantes: corta (≤ 280 caracteres) y, si el formato es hilo, hilo de 4-7 posts.
- Si es una historia inventada: añadir marcador de ficción (p. ej. "Relato" / "Story") y no atribuirla a personas reales.
- Si `X_ACCOUNT_LANG=both`: versión ES y EN adaptadas (no traducción literal), para dos cuentas separadas.
- Sugerencia de hora de publicación (según la hora de las tendencias más fuertes).
- Validador: sin datos personales de terceros, sin afirmaciones de hecho sin fuente, sin contenido sensible (salud, finanzas, política) presentado como verdad.

### 5.5 Módulo `review`
- `data/x_review_YYYYMMDD.html`: tarjetas con el borrador, botón "copiar", contador de caracteres, la tendencia de origen (enlace) y por qué debería funcionar.
- Piero copia, retoca y **programa él mismo** desde la web de X. Este sistema no tiene ni pedirá credenciales de publicación en X.
- Escribir también los borradores en la pestaña `drafts` de la misma Sheet, para verlos desde el móvil.

### 5.6 Ejecución programada
- Cron diario a las 08:30 (después de Grok Bot) en el VPS de Piero o en su PC: `python -m plan_b_x.cli ingest && python -m plan_b_x.cli draft && python -m plan_b_x.cli review`.
- Al terminar, enviar un aviso (Telegram, que Piero ya usa) con el enlace a la Sheet `drafts`.

### 5.7 Roadmap Plan B

| Semana | Entregable |
|---|---|
| 3 | Piero contrata Grok Bot y crea Trend Scout; prueba manual de 1 día |
| 3 | `ingest` + `drafts` + `review` funcionando con datos reales |
| 4 | Cron + aviso por Telegram; Piero publica 3-5 posts/día |
| 4-7 | Ajustar nichos según lo que funcione |
| 8 | Revisión con datos |

### 5.8 Métricas y decisión
- Piero apunta semanalmente (o se lee del panel de X a mano): seguidores, impresiones, posts publicados.
- A las 4 semanas: quedarse con los 1-2 nichos que más impresiones por post den y eliminar el resto.
- Monetización: los programas de pagos de X excluyen el contenido creado o publicado por medios automatizados; por eso Piero debe **retocar** cada post. No contar con esos pagos hasta confirmar elegibilidad. Uso alternativo seguro de la audiencia: llevar tráfico a la tienda de Etsy (Plan A).

---

## 6. Orden de trabajo para Claude Code

1. Crear repo, `pyproject.toml`, `.env.example`, `shared/`, tests base.
2. Mostrar a Piero la checklist de la Fase 0 y preguntar qué tiene ya.
3. Plan A sin credenciales: `catalog` → `generator` → `copy` → `mockups` (con datos de ejemplo). Entregar a Piero 1 producto en 3 estilos para validar.
4. Plan A con credenciales: `research` (API key) → `etsy_api` (OAuth) → `review`. Primer lote de 5 borradores.
5. Plan B: entregar a Piero el texto de Trend Scout; cuando confirme que Grok Bot escribe en la Sheet, construir `ingest` → `drafts` → `review` → cron.
6. Al final de cada paso: resumen corto en español de qué funciona, qué falta y qué necesita de Piero.

## 7. Presupuesto

| Concepto | Coste |
|---|---|
| Etsy | 0,20 $ por anuncio + comisiones por venta |
| Anthropic API | céntimos por lote (registrar coste real) |
| Grok Bot | desde ~20-30 $/mes (solo Plan B) |
| Higgsfield | créditos que Piero ya tiene; opcional |
| Canva, fuentes, Python | 0 € |

## 8. Riesgos conocidos

- Etsy endurece las normas sobre IA y producción en masa → ritmo de 5/semana, calidad alta, divulgación de IA.
- Endpoints de Etsy/Pinterest pueden cambiar → verificar en la documentación oficial antes de implementar.
- Grok Bot es beta: cuotas no publicadas → rutina una vez al día, sin bucles.
- X: no automatizar publicación ni interacción; contenido original.

---

## 9. Herramientas disponibles y para qué usar cada una

Claude Code: comprueba al empezar cuáles de estos conectores están activos en tu sesión. Si uno no está, usa la alternativa indicada; no te bloquees.

| Herramienta | Para qué en este proyecto | Alternativa si no está |
|---|---|---|
| **Anthropic API** (`shared/llm.py`) | Textos bilingües, títulos, etiquetas, borradores de X, análisis | — (obligatoria) |
| **Etsy Open API v3** | Research de keywords, borradores, subida de imágenes y del ZIP | Subida manual |
| **Higgsfield** (conector) | Fondos para mockups, vídeos cortos de producto, vídeos para pines y TikTok | Fondos generados con código |
| **Adobe for creativity** (conector) | Diseño de portadas/pines con Adobe Express, fuentes, utilidades de PDF (comprimir, combinar, convertir a imagen) | Pillow + reportlab |
| **Insightpins Pin Generator** (conector) | Pines verticales 1000x1500 a partir de la URL del anuncio de Etsy (`extract_url` → `render_pin`). Cada render gasta cuota diaria; el enlace de la imagen caduca a los 7 días | Pillow con plantilla propia |
| **JuzPost** / **Postiz** | Programar publicaciones en redes (comprobar con `list_accounts`/`get_platform_limits` qué plataformas admite la cuenta de Piero). Para Pinterest solo si la plataforma está conectada; nunca para publicar en X | Subida manual |
| **HarborRank** (conector) | Volumen y dificultad de palabras clave en Google para Pinterest/KDP y SEO | Etsy research + autocompletado |
| **Shopify** (conector) | Canal secundario: vender las mismas plantillas como producto digital en la tienda que Piero ya tiene (`create-digital-product`, `upload-digital-product-file`). Solo cuando Etsy ya venda | — |
| **Gmail** | Avisos y resumen semanal a Piero | Telegram |
| **Grok Bot** | Solo Plan B: detectar tendencias en X y escribirlas en la Google Sheet | — |

Regla para todos: ninguna herramienta publica sin revisión de Piero, salvo que él lo autorice explícitamente para un caso concreto.

---

## 10. PLAN E — Pinterest: tráfico gratis para Etsy + enlaces de afiliado

**Por qué:** Pinterest funciona como un buscador, no como un muro: un pin bueno sigue trayendo clics durante meses. Tenía unos 640 millones de usuarios mensuales a mediados de 2026. Es la fuente de tráfico sin anuncios más natural para Etsy y para bodas/bautizos/eventos.

**Normas verificadas (oct 2026):**
- Pinterest permite enlaces de afiliado directamente en los pines si se cumple: una sola cuenta auténtica, contenido original que aporte valor, transparencia sobre el carácter comercial y uso moderado.
- Prohíbe publicar el mismo contenido de afiliado en volumen repetitivo y bloquea muchos acortadores de enlaces (no usar bit.ly ni similares).
- Las nuevas Normas de la comunidad entran en vigor el **12 de noviembre de 2026**: releerlas en esa fecha antes de escalar.
- API: con acceso "Trial" los pines creados por API solo los ve el dueño de la app; para publicar por API hace falta acceso "Standard" (vídeo de demostración + revisión manual). Hasta tenerlo, Piero sube los pines a mano.

**Programas de afiliado candidatos** (Piero se da de alta; verificar que aceptan tráfico desde Pinterest): Amazon Associates, Etsy Affiliates (vía Awin).

**Módulo `plan_e_pinterest/`:**
1. `pins`: para cada anuncio publicado en Etsy, generar 3 pines distintos (no repetidos) con Insightpins (`extract_url` del anuncio → `render_pin`) o Pillow. Texto del pin bilingüe, con la keyword principal.
2. `affiliate`: tableros temáticos del mismo nicho (p. ej. "Bautizo bilingüe: ideas", "Boda católica latina") con productos complementarios de Amazon/Etsy (velas, ropones, recordatorios). Máximo 20-30 % de pines de afiliado; el resto, contenido útil propio (ideas, checklists, timelines).
3. `schedule`: exportar un CSV/carpeta diaria con imagen + título + descripción + enlace + tablero, listo para subir. Ritmo sugerido: 3-5 pines/día.
4. Toda descripción con enlace de afiliado incluye divulgación ("enlace de afiliado / affiliate link").

**Roadmap:** semana 4 cuenta de empresa en Pinterest + tableros; semana 5 primeros pines; semanas 5-12 constancia diaria. Revisar clics a Etsy a las 8 semanas.

---

## 11. PLAN C — Libros de actividades bilingües en Amazon KDP

**Por qué:** Amazon imprime y envía bajo demanda y su buscador pone el tráfico. Mismo público y misma ventaja de idioma que el Plan A.

**Normas verificadas (2026):**
- KDP permite contenido generado con IA pero hay que **declararlo** (texto, imágenes y traducciones por separado) al publicar. Desde abril de 2026 retiran sin aviso los títulos no declarados y la reincidencia puede suspender la cuenta.
- Límite de **3 libros con IA al día** por cuenta. Los libros casi idénticos activan filtros de calidad/duplicados.
- El "contenido bajo" de mínimo esfuerzo ya no funciona; los que venden son libros de **contenido medio**: actividades, pasatiempos, cuadernos de trabajo.

**Producto (VALIDADO 18 oct 2026 con datos reales de Amazon):** libros de **sopas de letras y pasatiempos en letra grande para mayores, con temática de nostalgia**, en español. Mercado principal Amazon.es; después Amazon.com (público hispano de EE. UU.).

Datos medidos (puesto en el ranking de toda la categoría Libros):
- Amazon.es: "Pasatiempos para personas mayores" nº 805 · "Memorias de España – pasatiempos para mayores en letra grande" nº 1.243 · "Sopa de letras para mayores letra muy grande Vol. 1" nº 1.489 · "Pasatiempos llenos de recuerdos" nº 1.760 · "Sopa de letras XXL Recuerdos de los años 60" nº 7.721 · "Años 70" nº 11.492.
- Amazon.com: sopas de letras en español en letra grande entre nº 5.725 y nº 35.000.
- Descartado por datos: sudokus en español (mayoría con ranking muy bajo), diarios de embarazo en español.
- Comprador real: hijos y nietos que lo regalan (varios títulos usan "regalo para personas mayores"). Campaña fuerte: Navidad.

**Concepto del libro:** las sopas de letras siguen siendo el núcleo, pero las palabras y los temas son **recuerdos de la juventud del lector** (lo que diferencia a los más vendidos). Cada sopa con un título temático y una breve introducción nostálgica. Ejemplos de temas: canciones y cantantes de los 60/70 (solo nombres y títulos, nunca letras de canciones), películas y actores, juegos de la infancia (la peonza, las chapas, la goma), oficios de antes (el afilador, el sereno), refranes, comidas de la abuela, la escuela de antes, electrodomésticos y objetos antiguos, fiestas y tradiciones.

**Formato:** 8.5x11", letra muy grande (≥ 16 pt en las palabras de la lista, cuadrícula grande), una sopa por página, soluciones al final, ~100 sopas. Opcional "mixto": añadir crucigramas sencillos y "completa el refrán".

**Serie planificada:** Vol. 1 "Recuerdos de España" (mixto de temas) → Vol. 2 "Años 60" → Vol. 3 "Años 70" → Vol. 4 "Años 80". Primero publicar el Vol. 1 antes de Navidad.

**Restricciones:** no reproducir letras de canciones ni textos con copyright; los nombres de artistas/películas solo como palabras de la sopa. Diseño de portada propio, sin fotos de personas famosas.

**Módulo `plan_c_kdp/`:**
1. `research`: palabras clave con HarborRank y autocompletado de Amazon; evitar temas con marcas/personajes.
2. `interior`: generar el PDF interior con reportlab (tamaño y sangrado según las especificaciones de KDP vigentes; verificarlas en la ayuda de KDP antes de maquetar). Contenido generado y revisado: sopas de letras con solucionario, vocabulario ilustrable, actividades.
3. `cover`: portada completa (contraportada + lomo + portada) según la calculadora de KDP para el nº de páginas; arte con Higgsfield o Adobe Express.
4. `listing`: título, subtítulo, descripción bilingüe y 7 palabras clave.
5. **Subida manual** por Piero en el panel de KDP, marcando la declaración de IA que corresponda. No hay API de subida verificada; no automatizar con navegador.

**Ritmo:** 1-2 libros por semana, cada uno distinto de verdad. Revisar ventas a las 8 semanas.

---

## 12. PLAN D — Stock con IA (secundario)

- Adobe Stock acepta imágenes y vídeos hechos con IA siempre que se marquen como generados con IA al subirlos.
- El pago por descarga del contenido con IA es bajo; solo compensa con volumen y no hay cifras fiables de ganancias. Usarlo solo para aprovechar créditos de Higgsfield sobrantes.
- Temática que reaprovecha el resto: fondos y escenas de bodas/bautizos latinos, papel picado, talavera (diseños propios, sin copiar obras existentes).
- Sin código específico al principio: Piero sube a mano desde el portal de colaborador.

---

## 13. Principio general (de foros, para no perder tiempo)

Una persona que probó durante 6 meses los "ingresos pasivos" populares y lo contó en r/sidehustle concluyó que la mayoría están exagerados o exigen mucho más trabajo del que se dice, y que **lo aburrido y constante gana a lo llamativo y viral**. Aplicarlo aquí: pocos productos buenos, ritmo fijo semanal, medir a las 8 semanas y doblar solo lo que funcione.
