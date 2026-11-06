# Informe Fase 1 — Producto ecommerce Europa
**Fecha:** 2026-11-06 (Europe/Madrid)  
**Autor:** Scout (Grok Bot)  
**Proyecto:** Ecommerce / dropshipping Piero — solo investigación  
**Alcance:** ≥5 candidatos nuevos + placa mascota (obligatoria) + Neonaled solo como referencia  
**Regla:** Cero cifras inventadas. Lo no verificado = `NO COMPROBADO`. Lo no accesible = `BLOQUEADO` + motivo.

---

## 1. Resumen ejecutivo

Se evaluaron **6 candidatos nuevos** más la **placa/chapa personalizada para mascota** (obligatoria) y **Neonaled** (solo referencia, sin ficha). Google Trends (API/HTML) y Meta Ad Library quedaron **BLOQUEADOS** por rate-limit (429) y challenge antibot, respectivamente; la demanda se apoya en proxies: volumen Etsy (RankHero), rankings/reseñas Amazon.es/.de y tiendas EU con precios públicos.

**Ganador propuesto: mapa estelar personalizado (print-on-demand UE)** — encaja en PVP 40–150 EUR (lámina ~45 EUR, enmarcado ~70–95 EUR), MOQ 1 vía Printful/Gelato, producción/envío UE en plazos compatibles con ≤10 días en muchos destinos EU, margen bruto teórico ≥40% en SKU lámina A3/A2 sin marco (con IOSS/arancel 0% CN 4911.91), nicho de un solo producto con fuerte ángulo emocional y vídeo corto.

**Runner-up: alfombrilla de escritorio XL premium (cuero regenerado / fieltro+corcho)** — PVP de mercado 74–119 EUR, calidad percibida alta, pero **proveedor dropshipping MOQ 1 con precio unitario y plazo a España = NO COMPROBADO** (Spocket devolvió 403 sin login; Eglooh/Oakywood son D2C, no mayoristas verificados).

La **placa mascota** se estudia y se **DESCARTA** para el brief actual: el mercado EU de Amazon está en ~4–16 EUR; un PVP 40–150 EUR haría sentir engañado al cliente europeo. Un proveedor POD (Printuz) acepta 1 unidad, pero el envío estándar a Europa es **8–15 días hábiles** (>10 días).

**No se ha comprado, pedido muestras, escrito a proveedores ni creado cuentas.**

---

## 2. Tabla comparativa

| Candidato | PVP mercado observado (EUR) | Margen ≥40% (estim.) | MOQ 1 + ≤10 d a ES | Calidad percibida EU | Nicho 1 producto | Nota /10 | Veredicto |
|---|---|---|---|---|---|---|---|
| **Neonaled** (ref.) — letrero neón LED personalizado | ~70–200+ (Neonful desde ~70; Oh My Neon configs ~50–75+ sin IVA; The Neon Company desde ~194) | Variable; frágil + CE | MOQ 1 típico en makers; plazos NO COMPROBADO vs brief | Alta si hecho a mano ES/EU; electrónica | Sí | — | **Referencia solo** (Piero lo aparcó) |
| **Mapa estelar personalizado (POD UE)** | 9,99–69,90 lámina; ~45 The Night Sky; enmarcado Printful desde ~27–30+ envío | Sí en lámina A3/A2 (ver ficha) | Sí Printful/Gelato MOQ 0/1; UE 2–8 d hábiles típicos (fuentes POD) | Alta si papel museo / giclée | Excelente | **8,5** | **VALIDAR** |
| **Alfombrilla escritorio XL premium (cuero / fieltro+corcho)** | Eglooh 74 (50×35); Oakywood 83,30–119 (XL); Amazon PU barato 15–23 | Posible a PVP 79–99 si coste UE ≤35–45 — **coste proveedor NO COMPROBADO** | Dropship MOQ1 UE **NO COMPROBADO** | Alta en marcas EU | Buena | **6,0** | **VALIDAR CONDICIONAL** (falta proveedor) |
| **Espresso portátil manual (genérico / OEM)** | Wacaco Nanopresso ES 89,90 (2.664★); STARESSO SP200 69,90 (baristashop / Amazon.de ~80) | Posible a PVP 79–99 si coste+envío UE ≤35–40 — **OEM MOQ1 UE NO COMPROBADO** | Alibaba STARESSO MOQ 20; white-label MOQ1 **NO COMPROBADO**; China >10 d típico | Alta en marcas; genéricos variables | Buena | **5,5** | **DESCARTAR por ahora** (marca/MOQ/plazo) |
| **Placa/chapa mascota grabada** | Amazon.es ~3,89–10,99; UNIKTAG BE ~15,90; Printuz coste 2,79 USD + envío EU 6,50 USD | No a PVP 40–150 sin engaño de valor | Printuz MOQ 1 sí; plazo std **8–15 d** (>10). EU Etsy makers: precios NO COMPROBADO (timeout) | Media-alta en acero | Débil a PVP alto | **4,0** | **DESCARTAR** |
| **Elevador comedero mascota (acero/plástico)** | Petace Amazon.es 29,99 (940★, #2 raised bowls); Migosset bambú ~39,95 | Difícil: PVP mercado <40 | CJ/Spocket listados existen; precios/plazos SKU **NO COMPROBADO** | Media | Media | **4,5** | **DESCARTAR** (fuera de banda PVP) |
| **Tabla cortar madera grabada (POD)** | YourSurprise haya M 17,99 (1.607 rev.); oak EU ~25–50 | Apretado; PVP a menudo <40 | YourSurprise NL = competencia, no nuestro proveedor; Printful/Gelato wood board **NO COMPROBADO** en esta pasada | Alta | Media (regalo cocina) | **5,0** | **DESCARTAR** (PVP/contacto alimentario) |
| **Soporte portátil aluminio** | Amazon.es 8,39–23,99 (miles de reseñas) | No a 40–150 | Commodity China; plazos variables | Media (carrera a precio) | Débil | **3,0** | **DESCARTAR** |

---

## 3. Ficha completa — TOP 1: Mapa estelar personalizado (POD UE)

### 3.1 Qué es
Lámina / póster (opcionalmente enmarcado) que representa el cielo nocturno en una fecha, hora y lugar concretos, con texto personalizado (nombres, mensaje). Familia pequeña: lámina, lámina enmarcada, canvas.

### 3.2 Demanda
| Fuente | Hallazgo | Estado |
|---|---|---|
| Google Trends ES/DE/FR/IT 12 m | Consulta `trends.google.com` → **HTTP 429 Too Many Requests** | **BLOQUEADO** — rate-limit Google |
| Meta Ad Library ES | Página carga challenge JS (`/__rd_verify_…`) sin listado usable | **BLOQUEADO** — antibot Meta |
| RankHero Etsy keyword `star map` | **49.500** búsquedas/mes globales; **EU 3.600** (7%); competencia 26.162 listings; mediana precio ~26,98 USD; pico ene-2026 60.500 | Comprobado: https://www.rankhero.com/keywords/star-map |
| Competidores EU con ventas/reseñas | The Night Sky: **€45**, **4,8/5**, **3.951** opiniones, “envío rápido y gratuito” (claim sitio). Unicos ES: desde **9,99 €**, **4,7/5**, **99** reseñas, “45+ pedidos esta semana”, fabricado ES. Marcel et les Blondes: A4 19,90 → 70×100 69,90 € | Enlaces abajo |
| Estacionalidad proxy | RankHero: estable sep-2025–ago-2026; pico enero | Solo Etsy, no Google |

**Conclusión demanda:** Demanda real y sostenida en regalo emocional (aniversario, boda, nacimiento). Volumen Google ES/DE/FR/IT **no medido** (BLOQUEADO). Anuncios Meta/TikTok activos **NO COMPROBADO**.

### 3.3 Competencia (Europa)
| Tienda / vendedor | Precio | Reseñas / señal | Enlace |
|---|---|---|---|
| The Night Sky | €45 lámina | 4,8/5 · 3.951 opiniones | https://www.thenightsky.com/es/shop/star-map-print |
| Unicos (ES) | desde 9,99 € | 4,7 · 99; “fabricado en España”; 45+ pedidos/semana (claim) | https://unicos.com/es/poster-mapa-estelar-personalizado/ |
| Marcel et les Blondes | 19,90–69,90 € | 5,0 (claim sitio); impresión taller Estaing, envío 48 h (claim) | https://marceletlesblondes.com/en/products/personalised-star-map-birth-print |
| Lumistrate (glow + marco) | 49,95 € (antes 54,95) | Envío EU 3–7 días hábiles (claim) | https://lumistrate.com/products/star-map |
| Etsy ES listing ejemplo | desde ~24,75 € | 4,8 · 3 reseñas (dato búsqueda agregada) | https://www.etsy.com/listing/1642006136/unique-custom-star-map-personalised-star |
| Amazon.es líder “mapa estelar” | **NO COMPROBADO** en esta pasada (no se abrió ranking específico ASIN) | — | — |

**Posición vs Amazon:** El valor está en el **configurador** (fecha/lugar/preview) y marca emocional; Amazon compite mal en personalización profunda. Diferenciador: preview WYSIWYG + papel premium + opción enmarcado + historia de marca.

### 3.4 Proveedores (≥2) — MOQ 1, lectura pública
| Proveedor | Producto / precio base visto | MOQ | Envío / plazo | Calidad / notas | Enlace |
|---|---|---|---|---|---|
| **Printful** | Póster mate (cm): oferta schema **7,50 EUR** (tamaño por defecto en página ES). Enmarcado mate (cm): **27,25 EUR** (ES) / **30,12 USD** (EN). Envío UE 1er ítem (fuente PodVector may-2026): lámina **€5,49**; enmarcado **€14,99** | Sin mínimos (POD) | EU: Printful tiene facilities EU (p.ej. Letonia/España citadas en comparativas 2026); plazos totales EU típicos 5–12 d hábiles (listingboost) / A2 FR 6–8 d (lancemonshop, 6-jun-2026) | AggregateRating póster mate 4,5/223; enmarcado 4,5/22. Algunas reseñas negativas: marco frágil, tamaño mm fuera | https://www.printful.com/es/personalizables/decoracion-pared/posters/poster-mate-cm · https://www.printful.com/es/personalizables/decoracion-pared/todo/poster-mate-enmarcado-cm |
| **Gelato** | Red local 32 países; A3 base ~€5–8 (listingboost, approx.); A2 FR listado 14,47 USD + 11,98 USD envío (lancemonshop 6-jun-2026) | Sin mínimos | EU local: **2–6 días** totales (listingboost); garantía entrega 5 d hábiles en ES/DE/FR/IT (política Gelato) | Specialty papel; precio FR más alto que DE (dato lancemonshop) | https://www.gelato.com/products/posters-frames · https://listingboost.io/printful-vs-gelato-2026-which-is-better-for-etsy-sellers-in-europe/ |
| OwnStarMap (motor de diseño / reseller) | Guía integración Printful+Gelato para mapas estelares | N/A (software) | Depende del POD | Útil si se licencia el cálculo astronómico | https://ownstarmap.fr/en/reseller/guide/integrate-design-printful-gelato |

**Motor astronómico / licencia de cálculo de estrellas:** si no se usa OwnStarMap u otra lib con licencia clara → **NO COMPROBADO** (riesgo de precisión y de IP de datos). Hipparcos/IAU son catálogos públicos; la implementación propia requiere desarrollo o licencia.

### 3.5 Precio puesto en Europa — tabla de costes (escenario lámina A3 ~30×40 / equiv.)

**Hipótesis de PVP propuesto:** **49 EUR** (IVA incluido, alineado con The Night Sky 45 € y banda mid Etsy 25–50 USD).  
**SKU:** póster mate sin marco, producción Printful EU, envío a España.

| Concepto | Importe | Fuente / nota |
|---|---|---|
| Coste producto base | **7,50 EUR** | Schema Printful ES póster mate (tamaño exacto A3 en checkout = **NO COMPROBADO**; 7,50 es el offer price de la página) |
| Envío Printful EU (1º ítem) | **5,49 EUR** | PodVector may-2026 (tabla EU unframed) |
| Subtotal proveedor | **12,99 EUR** | |
| Arancel importación | **0 EUR** | CN/HS **4911.91** posters/fotos impresas: arancel erga omnes **0%** (celna24 / KleverKlimb). Con Printful EU el bien suele circular ya en UE → sin importación CN |
| IVA importación (IOSS) | **0 EUR adicional** si Printful factura/recauda IVA UE en origen EU; si se vende B2C ES a 21% IVA, el PVP 49 ya lo incluye → IVA repercutido **NO es coste de margen bruto** de la misma forma que un import CN. **Desglose IVA checkout Printful ES: NO COMPROBADO** sin cuenta |
| Comisión pago ~3% | **1,47 EUR** | 3% × 49 |
| Devoluciones estimadas | **1,47 EUR** | **Estimación marcada:** 3% del PVP (arte personalizado; no hay tasa propia medida) → **NO COMPROBADO empírico** |
| **Coste total variable** | **≈ 15,93 EUR** | |
| **PVP** | **49,00 EUR** | |
| **Margen bruto** | **≈ 33,07 EUR → 67,5%** | ≥40% **sí** en este escenario |

**Escenario enmarcado (PVP 89 EUR):**
| Concepto | Importe | Nota |
|---|---|---|
| Base enmarcado | 27,25 EUR | Printful ES schema |
| Envío enmarcado EU | 14,99 EUR | PodVector |
| Subtotal | 42,24 EUR | |
| Pago 3% | 2,67 EUR | |
| Devoluciones est. 5% | 4,45 EUR | Enmarcado más frágil; % **estimado NO COMPROBADO** |
| Coste total | ≈ 49,36 EUR | |
| Margen | ≈ 39,64 EUR → **44,5%** | Cumple ≥40% por poco; sensible a daños en tránsito |

**Advertencia:** Precios Printful/Gelato varían por tamaño exacto, plan Growth (−18–22%), y país de producción. Cifras de checkout en vivo con cuenta = **NO COMPROBADO** (no se creó cuenta).

### 3.6 Posicionamiento
- **A quién:** Parejas 25–45, regalos de aniversario/boda/nacimiento; ES/DE/FR/IT.
- **Por qué no Amazon:** Configurador con preview fiel, copy emocional, unboxing, opción marco premium, marca propia — no un ASIN genérico.
- **Ángulo de marca:** “La noche en que todo cambió” — objeto de recuerdo, no decoración barata.
- **3 ganchos vídeo:**
  1. Pareja introduce la fecha del primer beso → preview del cielo → unboxing lámina.
  2. “Amazon no sabe qué estrellas había el día que naciste” (demo configurador).
  3. Regalo a padres con fecha/hora/hospital del nacimiento + reacción.

### 3.7 Riesgos
| Riesgo | Detalle |
|---|---|
| Devoluciones | Personalizado: política de “no devolución salvo defecto” habitual; debe ser clara (derecho EU 14 d vs bienes personalizados — **asesoría legal NO COMPROBADA**) |
| Daños marco | Reseñas Printful: marcos doblados/rotos; presupuestar 2–4% (PodVector) |
| Precisión astronómica | Si el mapa es inexacto → reclamaciones; licencia motor **NO COMPROBADA** |
| Competencia saturada | Muchos sellers Etsy; diferenciación por UX + calidad papel + velocidad EU |
| Patentes | Mapas estelares como categoría: **NO COMPROBADO** patent thicket; marcas “Night Sky” etc. a evitar en naming |
| Normativa | Impresos: baja; enmarcado: seguridad embalaje |

### 3.8 Nota y veredicto
**8,5 / 10 — VALIDAR**  
Mejor encaje con brief (calidad, PVP, margen, MOQ 1, UE, nicho, vídeo). Siguiente paso (tras OK Piero): muestra Printful + Gelato del mismo diseño, checkout real a dirección ES, y decisión de motor astronómico — **sin comprar hasta aprobación**.

---

## 4. Ficha completa — TOP 2: Alfombrilla escritorio XL premium (cuero regenerado / fieltro+corcho)

### 4.1 Qué es
Desk mat / sous-main XL (aprox. 80×40 a 100×40 cm) en cuero regenerado con costura, o fieltro de lana merino + base corcho. Accesorio home-office premium.

### 4.2 Demanda
| Fuente | Hallazgo | Estado |
|---|---|---|
| Google Trends | Igual que arriba | **BLOQUEADO** (429) |
| Meta Ad Library | — | **BLOQUEADO** |
| RankHero `desk mat` | ~4.400 búsquedas/mes EU (síntesis búsqueda agregada; página no re-fetchada en detalle esta pasada) | **Parcial / verificar** https://www.rankhero.com/keywords/desk-mat |
| Señal Amazon / D2C | Eglooh 383 reseñas 4,6; Oakywood reviews mixtas ~3,8–3,9 en Amazon UK/BE; YSAGi PU 11.061★ a 14,99 € (commodity) | Demanda existe; premium vs low-cost muy distinto |

### 4.3 Competencia
| Vendedor | Precio | Reseñas | Enlace |
|---|---|---|---|
| Eglooh Mercurio (IT, Amazon.es) | **74,00 €** (50×35); hay 65×45, 80×50, 90×60 | 4,6 · **383** | https://www.amazon.es/Eglooh-Protector-Escritorio-Alfombrilla-Antideslizante/dp/B07RDLPG6V |
| Oakywood Felt&Cork XL | **83,30 €** (dto) / **119 €** | Sitio PL; Amazon BE 102,99 · 3,9 · 55 | https://oakywood.shop/en-de/products/felt-cork-desk-mat |
| CENNBIE PU 90×40 Amazon.de | **22,98 €** | 4,4 · 2.478 | https://www.amazon.de/-/en/CENNBIE-Leather-Extended-Waterproof-Non-Slip/dp/B0F65YP1S5 |
| YSAGi 80×40 Amazon.de | **14,99 €** | 4,6 · 11.061 | https://www.amazon.de/YSAGi-Schreibtischunterlage-Tischunterlage-Schreibunterlage-Multifunktionales/dp/B0CRQ7G6VD |

### 4.4 Proveedores
| Proveedor | Precio unitario | MOQ | Envío ES / plazo | Estado |
|---|---|---|---|---|
| Spocket listing “Rawlins Leather Desk Pads” | **NO COMPROBADO** | Spocket declara no-MOQ en marketing general | **BLOQUEADO** — HTTP **403** al fetch sin login | https://www.spocket.co/dropship/accessories/rawlins-leather-desk-pads-36x19-and-146x315-inches |
| Eglooh / Oakywood | N/A (D2C) | N/A | No son mayoristas dropship verificados | No contactar (regla) |
| CJDropshipping EU warehouse desk mat | Precio SKU | — | Búsqueda sin SKU concreto con precio+plazo ES | **NO COMPROBADO** |
| BigBuy categoría office | — | MOQ 1 claim BigBuy general | Catálogo sin precio de desk mat premium en resultados | **NO COMPROBADO** |

### 4.5 Precio puesto en Europa
**PVP propuesto tentativo:** **89 EUR** (entre Eglooh 74 y Oakywood 119).

| Concepto | Importe | Estado |
|---|---|---|
| Coste producto + envío UE | — | **NO COMPROBADO** |
| Arancel (si import CN, cuero/textil) | Depende HS (4205/5602/…) | **NO COMPROBADO** sin ficha proveedor |
| IVA/IOSS | Si stock ya en UE → sin IOSS import | — |
| Pago 3% | 2,67 EUR | sobre 89 |
| Devoluciones est. 5% | 4,45 EUR | estimación |
| **Margen ≥40%** | Requiere coste landed ≤ **≈ 46 EUR** (89×0,6 − pago − dev ≈ umbral) | **NO COMPROBADO** hasta tener oferta |

### 4.6 Posicionamiento
- **A quién:** Remotos, setups minimalistas, regalo home-office DE/NL/ES.
- **Por qué no Amazon:** Material UE (cuero regenerado IT / merino DE + corcho PT), garantía larga (Oakywood claim 5 años / 2 años), unboxing, marca “plastic-free desk”.
- **Ángulo:** Escritorio calmado, materiales naturales, anti-PU barato.
- **3 ganchos vídeo:**
  1. Side-by-side PU 15 € vs cuero regenerado (textura, olor, costura).
  2. Time-lapse setup desk → solo la mat como héroe.
  3. “Tu ratón merece algo que no sea plástico de 3 mm”.

### 4.7 Riesgos
- Competencia Amazon a 15 € destruye conversión si el anuncio no justifica premium.
- Boulochage en fieltro (Oakywood lo admite).
- Voluminoso → portes altos; devoluciones caras.
- Sin proveedor dropship verificado → **no se puede lanzar**.

### 4.8 Nota y veredicto
**6,0 / 10 — VALIDAR CONDICIONAL**  
Mercado y PVP encajan; **bloqueo real = proveedor MOQ 1 + plazo ≤10 d + coste** no verificado sin cuenta/contacto. Solo subir a VALIDAR pleno tras Piero autorizar registro Spocket/BigBuy o mayorista EU (sin pedido de muestra hasta OK).

---

## 5. Notas breves — resto de candidatos (no top 2)

### 5.1 Placa/chapa mascota grabada (OBLIGATORIA)
- **Amazon.it LYL:** 10,99 € · 4,6 · **19.584** reseñas — https://www.amazon.it/-/en/Stainless-Personalized-Double-Engraved-Different/dp/B07PDYR4X9  
- **Amazon.de KSZ:** 6,99 € · 4,6 · 1.020 — https://www.amazon.de/-/en/Stainless-Steel-Personalised-Pet-Engraving/dp/B07MYW3Q8T  
- **Amazon.es:** listings ~3,89–8,99 € (búsqueda “dog tags”).  
- **Printuz (POD):** 2,79 USD + Europe shipping 6,50 USD; MOQ **no minimums**; fulfillment avg 5–7 d + transporte std **8–15 business days** (4PX/Yun) → **incumple ≤10 días** en estándar; DHL 3–7 d pero +29,50 USD — https://printuz.com/product/personalized-laser-metal-alloy-dog-id-tag/  
- **Contradicción MOQ 50 vs “desde 1 pieza” (proveedor previo):** **NO COMPROBADO** en esta sesión (no se contactó; no se reidentificó el SKU exacto del historial). Otros con MOQ 1: Printuz sí; Etsy EU (MonIDTag FR, PAWFY ES, MaJe DE) — precios/MOQ exactos **NO COMPROBADO** (timeout Etsy).  
- **Veredicto: DESCARTAR** para brief 40–150 EUR / ≤10 d.

### 5.2 Espresso portátil manual
- Demanda fuerte (Wacaco Nanopresso Amazon.es **89,90 €**, 4,5 · **2.664** — https://www.amazon.es/-/en/WACACO-Nanopresso-Portable-Protective-Minipresso/dp/B0752XV66X). STARESSO SP200 **69,90 €** EU stock (baristashop.es).  
- **Problema:** Wacaco/STARESSO = marcas; OEM Alibaba STARESSO MOQ **20** (alibaba product detail); white-label MOQ 1 + almacén UE + CE food-contact **NO COMPROBADO**. Eléctrico = baterías (evitar).  
- **Veredicto: DESCARTAR por ahora.**

### 5.3 Elevador comedero
- Petace Amazon.es **29,99 €**, 4,8 · 940, #2 raised bowls — https://www.amazon.es/-/en/Elevated-Adjustable-Heights-Anti-Voracity-Non-Drip/dp/B0CP3GBRKJ  
- Bajo banda 40 EUR → **DESCARTAR**.

### 5.4 Tabla cortar grabada
- YourSurprise NL **17,99 €**, 9,4/10 · 1.607 — https://www.yoursurprise.eu/kitchen-and-dining/kitchen-gifts/personalised-chopping-boards/engraved-wooden-chopping-board  
- Contacto alimentario + PVP bajo → **DESCARTAR**.

### 5.5 Soporte laptop aluminio
- GRIFEMA Amazon.es **8,39 €**, 4,6 · 3.895, #1 Lapdesks — **DESCARTAR**.

### 5.6 Neonaled (referencia)
- Mercado letreros neón LED personalizados EU desde ~70 € (Neonful) hasta 190+ (The Neon Company). Electrónica CE, frágil, voluminoso relativo — coherente con aparcarlo.

---

## 6. Recomendación final

| Prioridad | Producto | Acción |
|---|---|---|
| **1 — Ganador** | **Mapa estelar personalizado (POD UE)** | Pedir OK a Piero para **VALIDAR** con muestras Printful + Gelato (fase con gasto = solo tras aprobación). Definir naming (evitar “Night Sky”), motor astronómico, PVP 49 € lámina / 89 € enmarcado. |
| **2 — Runner-up** | **Desk mat XL premium** | Solo si en paralelo se verifica (con OK de Piero para crear cuenta Spocket/BigBuy, **sin pedido**) un SKU MOQ 1, landed ≤46 €, ≤10 d a ES. |
| No lanzar | Placa mascota, elevador comedero, tabla cortar, laptop stand, espresso branded/OEM sin MOQ1 UE | — |

**Fase 2 (tienda Shopify):** no iniciar hasta que Piero apruebe el producto ganador.

---

## 7. Apéndice — BLOQUEADOS / NO COMPROBADOS críticos

### BLOQUEADO
1. **Google Trends** ES/DE/FR/IT — HTTP **429 Too Many Requests** (curl + trends API).  
2. **Meta Ad Library** — challenge JS antibot; sin conteo de anunciantes activos.  
3. **Spocket** ficha desk mat — HTTP **403** sin autenticación.  
4. **Etsy MonIDTag** — timeout al fetch.  
5. **Checkout en vivo Printful/Gelato** (precios por tamaño exacto A3/A2 a ES) — requiere cuenta; no creada por regla.  
6. **TikTok Creative Center / anuncios virales** — no consultado con datos cuantitativos esta pasada (equivalente a no verificado; si se exige cifra → tratar como no disponible).

### NO COMPROBADO
1. Contradicción **MOQ 50 vs desde 1 pieza** del proveedor previo de placas mascota (SKU no re-localizado; no contactado).  
2. Tasa real de devoluciones propia (se usaron % estimados marcados).  
3. Desglose IVA en factura Printful ES.  
4. Precio unitario A3 exacto Printful vs offer schema 7,50 EUR.  
5. Coste landed desk mat / espresso white-label MOQ 1 UE.  
6. Volumen Keyword Planner Google ES/DE/FR/IT.  
7. Líder Amazon.es “mapa estelar” (precio + nº reseñas).  
8. Permiso de uso de fotos de proveedor para fase 2.  
9. Patentes/marcas conflictivas en naming “star map” / equivalentes ES.  
10. Sunny Berlin hundemarke — URL devolvió **404**.

### Fuentes principales (lista corta)
- https://www.thenightsky.com/es/shop/star-map-print  
- https://unicos.com/es/poster-mapa-estelar-personalizado/  
- https://www.printful.com/es/personalizables/decoracion-pared/posters/poster-mate-cm  
- https://www.printful.com/es/personalizables/decoracion-pared/todo/poster-mate-enmarcado-cm  
- https://podvector.ai/articles/printful/costs-and-charges/printful-poster-pricing-full-breakdown-for-pod-sellers  
- https://listingboost.io/printful-vs-gelato-2026-which-is-better-for-etsy-sellers-in-europe/  
- https://www.rankhero.com/keywords/star-map  
- https://printuz.com/product/personalized-laser-metal-alloy-dog-id-tag/  
- https://www.amazon.es/-/en/WACACO-Nanopresso-Portable-Protective-Minipresso/dp/B0752XV66X  
- https://www.amazon.es/Eglooh-Protector-Escritorio-Alfombrilla-Antideslizante/dp/B07RDLPG6V  
- https://oakywood.shop/en-de/products/felt-cork-desk-mat  
- https://celna24.pl/en/customs-tariff/491191  

---

*Fin del informe. Scout — 2026-11-06, Europe/Madrid.*
