"""listing.md: everything Piero copies into the KDP form, plus an upload checklist."""

from __future__ import annotations

from pathlib import Path

from plan_c_kdp import kdp_specs as kdp
from plan_c_kdp.themes import Book

KEYWORDS = [
    "sopa de letras letra grande adultos mayores",
    "pasatiempos para personas mayores",
    "regalo para abuelos y abuelas",
    "libro de actividades para ancianos",
    "juegos de memoria y nostalgia de España",
    "sopas de letras letra muy grande",
    "estimulación cognitiva tercera edad",
]
CATEGORIES = [
    "Juegos y actividades > Sopas de letras (Games & Activities > Word Search)",
    "Juegos y actividades > Rompecabezas (Games & Activities > Puzzles)",
    "Salud, familia y desarrollo personal > Envejecimiento (Health > Aging)",
]
PRICE_EUR = 9.99
PRICE_USD = 9.99


def title_and_subtitle(book: Book) -> tuple[str, str]:
    title = f"{book.title}: {book.subtitle}"
    subtitle = (f"{len(book.themes)} pasatiempos en letra muy grande con temas de "
                f"nostalgia y soluciones. Un regalo para padres y abuelos. Vol. {book.volume}")
    return title, subtitle


def description_html(book: Book) -> str:
    sample = ", ".join(t.title.lower() for t in book.themes[:6])
    return f"""<p><b>Un regalo lleno de recuerdos para nuestros mayores.</b></p>
<p>{len(book.themes)} sopas de letras en letra muy grande con temas que traen a la memoria la España de su juventud: {sample} y muchos más.</p>
<p>Cada sopa ocupa una página entera e incluye una breve introducción al tema, para que buscar palabras sea también una ocasión para recordar y charlar en familia.</p>
<ul>
<li>Letra muy grande y cuadrículas amplias de 15 × 15, fáciles de leer.</li>
<li>Palabras en horizontal, vertical y diagonal; ninguna escrita al revés.</li>
<li>Palabras en mayúsculas y sin tildes, tal y como aparecen en la cuadrícula.</li>
<li>Soluciones al final del libro.</li>
<li>Formato grande: 21,6 × 27,9 cm, en papel blanco.</li>
</ul>
<p>Ideal para regalar en Navidad, cumpleaños o el Día de los Abuelos, y para mantener la mente activa disfrutando de los buenos recuerdos.</p>"""


def write_listing(book: Book, pages: int, out_path: Path, paper: str = "white") -> None:
    title, subtitle = title_and_subtitle(book)
    assert len(title) + len(subtitle) <= 200, "KDP limit: title + subtitle <= 200 chars"
    kw = book.keywords or tuple(KEYWORDS)
    assert len(kw) == 7 and all(len(k) <= 50 for k in kw), "KDP: 7 keywords, max 50 chars"
    width, height = kdp.cover_size_in(pages, paper)
    cost_eur, cost_usd = kdp.printing_cost(pages, "EUR"), kdp.printing_cost(pages, "USD")
    themes_list = "\n".join(f"{i}. {t.title}" for i, t in enumerate(book.themes, 1))
    keywords = "\n".join(f"{i}. {k}" for i, k in enumerate(kw, 1))
    categories = "\n".join(f"- {c}" for c in CATEGORIES)
    out_path.write_text(f"""# Ficha KDP — {title} (Vol. {book.volume})

> Generado por `python -m plan_c_kdp.build`. Revisar y copiar a mano en kdp.amazon.com.

## 1. Detalles del libro

| Campo | Valor |
|---|---|
| Idioma | Español |
| Título | {title} |
| Subtítulo | {subtitle} |
| Serie | Sopa de letras para mayores — Volumen {book.volume} |
| Autor | {book.author} |
| Contenido para adultos | No |

### Descripción (pegar en el editor de KDP; admite estas etiquetas HTML)

```html
{description_html(book)}
```

### 7 palabras clave

{keywords}

### Categorías sugeridas (confirmar en el selector de KDP, los nombres cambian)

{categories}

## 2. Contenido

| Campo | Valor |
|---|---|
| ISBN | Usar el ISBN gratuito de KDP |
| Tinta y papel | Negro y blanco ({'papel blanco' if paper == 'white' else 'papel crema'}) |
| Tamaño | 8.5 × 11 in (21,59 × 27,94 cm) |
| Sangrado | Sin sangrado (interior) |
| Acabado de cubierta | Brillo (recomendado para colores vivos) |
| Interior | `{book.id}_interior.pdf` — {pages} páginas |
| Cubierta | `{book.id}_cover.pdf` — {width:.3f} × {height:.3f} in (con sangrado) |

### Declaración de IA (obligatoria)

- **Texto: SÍ, generado con IA.** Los temas, las palabras y las introducciones los redactó
  Claude; Piero los revisó y editó. Las cuadrículas las genera un programa (no es IA generativa),
  pero el texto del libro sí lo es.
- **Imágenes: NO** si se usa la portada tipográfica tal cual. **SÍ** si se añade una
  ilustración hecha con ChatGPT u otra herramienta de IA.
- **Traducción: NO.**

## 3. Precio

| Mercado | Coste de impresión | Precio sugerido | Regalía estimada |
|---|---|---|---|
| Amazon.es (EUR) | {cost_eur:.2f} € | {PRICE_EUR:.2f} € | {kdp.royalty(PRICE_EUR, pages, 'EUR'):.2f} € |
| Amazon.com (USD) | ${cost_usd:.2f} | ${PRICE_USD:.2f} | ${kdp.royalty(PRICE_USD, pages, 'USD'):.2f} |

- En euros, 9,99 € es el umbral del 60 % de regalía (a 9,98 € o menos baja al 50 %).
  Confirmar en la calculadora de KDP antes de publicar.
- Antes de fijar el precio, mirar el precio de 3-4 títulos del ranking medido
  (sección 11 del plan). No hay datos de precios de la competencia en este informe.
- Distribución ampliada: no activar al principio (paga 40 % antes del coste de impresión).

## 4. Checklist antes de enviar a revisión

- [ ] Abrí el PDF interior y leí al menos 10 sopas (legibilidad, temas "de mayores españoles").
- [ ] Revisé `plan_c_kdp/themes/vol1_recuerdos_de_espana.yaml` (palabras e introducciones).
- [ ] El nombre de autor es el que quiero usar (real o seudónimo).
- [ ] Vista previa de KDP sin errores de márgenes ni de texto fuera de zona.
- [ ] Declaración de IA marcada (texto: sí).
- [ ] Pedí una copia de prueba (opcional, recomendado antes de la campaña de Navidad).

## Temas del volumen

{themes_list}
""", encoding="utf-8")
