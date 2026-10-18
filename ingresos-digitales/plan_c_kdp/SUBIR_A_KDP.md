# Cómo subir los libros a KDP (paso a paso)

Archivos de cada volumen en `build/volN/`: `volN_interior.pdf`, `volN_cover.pdf` y `listing.md`
(con todos los textos para copiar). Hazlo **desde un ordenador** (desde el móvil KDP da problemas
al subir PDFs).

Orden recomendado: **Vol. 1 hoy, Vol. 2 al día siguiente.** KDP permite hasta 3 libros con IA
al día, pero escalonarlos queda más natural y, si algo falla en el primero, lo corriges en el segundo.

## 1. Crear el libro

kdp.amazon.com → **+ Crear** → **Tapa blanda**.

## 2. Pestaña "Detalles"

| Campo | Qué poner |
|---|---|
| Idioma | Español |
| Título / Subtítulo | Copiar de `listing.md` |
| Serie | Activar → crear serie **"Sopa de letras para mayores"** (en el Vol. 2, elegir la misma serie, nº 2) |
| Edición | Dejar vacío |
| Autor | El nombre elegido (ahora pone "Piero Palumbo"; puede ser distinto del de la cuenta) |
| Colaboradores | Nada |
| Descripción | Pegar el bloque HTML de `listing.md` |
| Derechos de publicación | "Soy el propietario de los derechos de autor" |
| Contenido principal | Para adultos: No. Libro de bajo contenido: **No** (tiene introducciones y temas) |
| Palabras clave | Las 7 de `listing.md`, una por casilla |
| Categorías | Elegir 3 en el selector, buscando "sopas de letras", "rompecabezas", "envejecimiento" |
| Contenido explícito | No |

Guardar y continuar.

## 3. Pestaña "Contenido"

1. **ISBN:** "Obtener un ISBN gratuito de KDP".
2. **Fecha de publicación:** dejar vacía.
3. **Opciones de impresión:**
   - Tinta y papel: **Tinta negra y papel blanco**.
   - Tamaño: **21,59 × 27,94 cm (8,5 × 11 in)**.
   - Sangrado: **Sin sangrado**.
   - Acabado de la cubierta: **Brillo**.
4. **Manuscrito:** subir `volN_interior.pdf`.
5. **Cubierta:** "Subir un archivo PDF listo para imprimir" → `volN_cover.pdf`.
6. **Contenido generado con IA:** **Sí**.
   - Texto: "Generado por IA" (Claude), con edición tuya. Indicar que lo revisaste.
   - Imágenes: **No** (la portada es tipográfica, hecha por código).
   - Traducciones: **No**.
7. **Vista previa del libro:** abrirla y revisar que no salgan avisos rojos. Si sale algún aviso
   de márgenes o de texto, haz una captura y mándamela.
8. **Copia de prueba:** opcional; si la pides, llega en 1-2 semanas.

Guardar y continuar.

## 4. Pestaña "Derechos y precios"

- Territorios: **Todos los territorios**.
- Mercado principal: **Amazon.es**.
- Precio: **9,99 €** (umbral del 60 %). KDP calcula los demás mercados; en Amazon.com
  ajustar a **9,99 $**.
- Distribución ampliada: **No**.
- **Publicar tu libro en tapa blanda.**

Amazon tarda hasta 72 horas en revisarlo. Te llegará un correo cuando esté a la venta.

## 5. Después de publicar

- Pásame el enlace de Amazon de cada libro: lo uso en la descripción del otro volumen
  ("de la misma serie") y en los posts de "build in public".
- No pidas reseñas a familiares que compartan cuenta o dirección contigo: Amazon las borra
  y puede penalizar el libro.

## Agenda 2027 (`build/agenda2027/`)

Mismo proceso que los libros, con estas diferencias:

- **Serie:** ninguna (no es parte de "Sopa de letras para mayores").
- **Título y subtítulo, descripción y palabras clave:** los de `build/agenda2027/listing.md`.
- **Categorías:** buscar "agendas", "calendarios" o "planificadores", y una de "pasatiempos".
- **Prioridad:** súbela la primera si puedes. Se vende sobre todo de noviembre a enero.
- Los festivos nacionales ya están comprobados con el BOE del 13 de octubre de 2026.

Regenerar: `python -m plan_c_kdp.agenda`.
