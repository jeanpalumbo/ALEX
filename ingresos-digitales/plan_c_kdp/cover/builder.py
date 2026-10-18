"""Full-wrap paperback cover (back + spine + front) sized with the KDP formula.

Typographic design in CMYK only (KDP asks not to mix colour spaces). An optional
illustration supplied by Piero (e.g. made with ChatGPT and saved in assets/) can be
placed on the front; it is converted to CMYK before embedding.
"""

from __future__ import annotations

import random
from pathlib import Path

from reportlab.lib.colors import CMYKColor
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.pdfgen.canvas import Canvas

from plan_c_kdp import kdp_specs as kdp
from plan_c_kdp.fonts import BODY, BODY_BOLD, DISPLAY, register_fonts
from plan_c_kdp.themes import Book

INCH = kdp.INCH

CREAM = CMYKColor(0.02, 0.06, 0.18, 0.0)
INK = CMYKColor(0.0, 0.0, 0.0, 1.0)
DARK = CMYKColor(0.30, 0.70, 0.75, 0.55)   # warm dark brown for body text
WHITE = CMYKColor(0, 0, 0, 0)

# (main band colour, accent colour) per volume.
PALETTES = {
    "terracotta": (CMYKColor(0.10, 0.78, 0.85, 0.12), CMYKColor(0.05, 0.28, 0.90, 0.0)),
    "teal": (CMYKColor(0.88, 0.25, 0.45, 0.12), CMYKColor(0.0, 0.62, 0.62, 0.0)),
    "mustard": (CMYKColor(0.05, 0.38, 0.95, 0.05), CMYKColor(0.70, 0.30, 0.10, 0.05)),
    "plum": (CMYKColor(0.55, 0.85, 0.35, 0.25), CMYKColor(0.05, 0.28, 0.90, 0.0)),
}

DEFAULT_BLURB = (
    "{n} sopas de letras pensadas para personas mayores, con temas que traen a la "
    "memoria la España de nuestra juventud: los juegos de la calle, la cocina de la "
    "abuela, las verbenas del pueblo, las tardes de radio, la mili, las bodas de antes "
    "y mucho más."
)
BACK_BULLETS = [
    "Letra muy grande y cuadrículas amplias, fáciles de leer.",
    "Una sopa por página, con una breve introducción a cada tema.",
    "Palabras en horizontal, vertical y diagonal. Ninguna al revés.",
    "Soluciones al final del libro.",
    "Formato grande: 21,6 × 27,9 cm.",
]
BACK_CLOSING = ("Un regalo ideal para padres y abuelos: entretiene, mantiene la mente "
                "activa y da pie a compartir historias en familia.")


class Cover:
    def __init__(self, path: Path, book: Book, pages: int, paper: str):
        register_fonts()
        self.book = book
        self.pages = pages
        self.spine = kdp.spine_width_in(pages, paper)
        self.width_in, self.height_in = kdp.cover_size_in(pages, paper)
        self.c = Canvas(str(path), pagesize=(self.width_in * INCH, self.height_in * INCH),
                        initialFontName=BODY)
        self.c.setTitle(f"{book.title} — {book.subtitle} (cover)")
        self.c.setAuthor(book.author)
        self.main, self.accent = PALETTES[book.palette]
        # x positions (inches) of the panels, measured from the left bleed edge.
        self.back_x0 = kdp.BLEED_IN
        self.back_x1 = self.back_x0 + kdp.TRIM_W_IN
        self.spine_x1 = self.back_x1 + self.spine
        self.front_x0 = self.spine_x1
        self.front_x1 = self.front_x0 + kdp.TRIM_W_IN
        self.trim_y0 = kdp.BLEED_IN
        self.trim_y1 = kdp.BLEED_IN + kdp.TRIM_H_IN

    def rect_in(self, x0, y0, x1, y1, color) -> None:
        self.c.setFillColor(color)
        self.c.rect(x0 * INCH, y0 * INCH, (x1 - x0) * INCH, (y1 - y0) * INCH, stroke=0, fill=1)

    def text_center(self, text, x_in, y_in, font, size, color) -> None:
        self.c.setFont(font, size)
        self.c.setFillColor(color)
        self.c.drawCentredString(x_in * INCH, y_in * INCH, text)

    def fit_size(self, text, font, size, max_width_in) -> float:
        while stringWidth(text, font, size) > max_width_in * INCH and size > 6:
            size -= 0.5
        return size

    # ---- panels -----------------------------------------------------------
    def background(self) -> None:
        self.rect_in(0, 0, self.width_in, self.height_in, CREAM)
        band_h = 3.0
        # Terracotta band across the top of the front panel and the whole spine.
        self.rect_in(self.front_x0, self.height_in - band_h, self.width_in, self.height_in,
                     self.main)
        self.rect_in(self.back_x1, 0, self.spine_x1, self.height_in, self.main)
        # Thin mustard rule under the band, and on the back panel top.
        self.rect_in(self.front_x0, self.height_in - band_h - 0.12, self.width_in,
                     self.height_in - band_h, self.accent)
        self.rect_in(0, self.height_in - 0.9, self.back_x1, self.height_in, self.main)
        self.rect_in(0, self.height_in - 1.02, self.back_x1, self.height_in - 0.9, self.accent)

    def front(self, image: Path | None) -> None:
        cx = (self.front_x0 + self.front_x1) / 2
        usable = kdp.TRIM_W_IN - 2 * 0.5
        top = self.trim_y1
        size = self.fit_size("SOPA DE LETRAS", DISPLAY, 80, usable)
        self.text_center("SOPA DE LETRAS", cx, top - 1.45, DISPLAY, size, WHITE)
        self.text_center("PARA MAYORES", cx, top - 2.35, BODY_BOLD, 44, CREAM)

        subtitle = self.book.subtitle
        sub_size = self.fit_size(subtitle, DISPLAY, 54, usable)
        self.text_center(subtitle, cx, top - 3.95, DISPLAY, sub_size, self.main)

        if image:
            self._front_image(image, cx, top - 4.4, 4.6)
        else:
            self._front_grid(cx, top - 4.45)

        # Selling points at the bottom.
        self.text_center("LETRA MUY GRANDE", cx, self.trim_y0 + 1.55, BODY_BOLD, 34, INK)
        self.text_center(f"{len(self.book.themes)} pasatiempos con soluciones", cx,
                         self.trim_y0 + 1.0, BODY, 24, DARK)
        self._volume_badge(self.front_x1 - 1.05, self.trim_y0 + 1.3)

    def _front_grid(self, cx: float, top: float) -> None:
        word = self.book.cover_word
        cols, rows, cell = len(word), 6, 0.68
        x0 = cx - cols * cell / 2
        rng = random.Random(f"cover-grid:{self.book.id}")
        filler = "AEIOULNRSTCDMPBG"
        letters = [[rng.choice(filler) for _ in range(cols)] for _ in range(rows)]
        word_row = 2
        letters[word_row] = list(word)
        c = self.c
        c.setLineWidth(1.2)
        for r in range(rows):
            for col in range(cols):
                x = (x0 + col * cell) * INCH
                y = (top - (r + 1) * cell) * INCH
                c.setFillColor(WHITE)
                c.setStrokeColor(DARK)
                c.roundRect(x + 2, y + 2, cell * INCH - 4, cell * INCH - 4, 5, stroke=1, fill=1)
        # Highlight capsule around the hidden word.
        y_mid = top - (word_row + 0.5) * cell
        c.setFillColor(self.accent)
        c.roundRect((x0 + 0.06) * INCH, (y_mid - 0.3) * INCH, (cols * cell - 0.12) * INCH,
                    0.6 * INCH, 0.3 * INCH, stroke=0, fill=1)
        for r in range(rows):
            for col in range(cols):
                ch = letters[r][col]
                highlighted = r == word_row
                c.setFont(BODY_BOLD, 30)
                c.setFillColor(INK if highlighted else DARK)
                c.drawCentredString((x0 + (col + 0.5) * cell) * INCH,
                                    (top - (r + 0.5) * cell) * INCH - 11, ch)

    def _front_image(self, image: Path, cx: float, top: float, height: float) -> None:
        from PIL import Image

        img = Image.open(image).convert("CMYK")
        ratio = img.width / img.height
        width = min(height * ratio, kdp.TRIM_W_IN - 1.2)
        height = width / ratio
        dpi = img.width / width
        if dpi < 300:
            print(f"warning: cover image is {dpi:.0f} DPI at this size; KDP asks for 300+")
        x = cx - width / 2
        self.c.drawImage(ImageReader(img), x * INCH, (top - height) * INCH,
                         width * INCH, height * INCH)
        self.c.setStrokeColor(DARK)
        self.c.setLineWidth(3)
        self.c.rect(x * INCH, (top - height) * INCH, width * INCH, height * INCH)

    def _volume_badge(self, cx: float, cy: float) -> None:
        c = self.c
        c.setFillColor(self.accent)
        c.circle(cx * INCH, cy * INCH, 0.62 * INCH, stroke=0, fill=1)
        self.text_center("VOL.", cx, cy + 0.12, BODY_BOLD, 16, INK)
        self.text_center(str(self.book.volume), cx, cy - 0.33, BODY_BOLD, 34, INK)

    def spine_text(self) -> None:
        if self.pages <= kdp.SPINE_TEXT_MIN_PAGES:
            return
        max_h = self.spine - 2 * kdp.SPINE_TEXT_CLEARANCE_IN
        size = min(12.0, max_h * INCH * 0.95)
        text = (f"SOPA DE LETRAS PARA MAYORES  ·  {self.book.subtitle}  ·  "
                f"Vol. {self.book.volume}")
        cx = (self.back_x1 + self.spine_x1) / 2
        cy = self.height_in / 2
        c = self.c
        c.saveState()
        c.translate(cx * INCH, cy * INCH)
        c.rotate(-90)  # reads top-to-bottom, as on Spanish/English spines
        c.setFont(BODY_BOLD, size)
        c.setFillColor(WHITE)
        c.drawCentredString(0, -size * 0.35, text)
        c.restoreState()

    def back(self) -> None:
        left = self.back_x0 + 0.75
        width = kdp.TRIM_W_IN - 1.5
        cx = left + width / 2
        self.text_center("Un regalo lleno de recuerdos", cx, self.trim_y1 - 0.62, BODY_BOLD,
                         26, WHITE)
        y = self.trim_y1 - 1.75
        y = self._wrapped((self.book.blurb or DEFAULT_BLURB).format(n=len(self.book.themes)), left, y, width,
                          BODY, 17, 0.33, DARK)
        y -= 0.3
        for bullet in BACK_BULLETS:
            self.c.setFillColor(self.main)
            self.c.circle((left + 0.1) * INCH, (y + 0.08) * INCH, 4.5, stroke=0, fill=1)
            y = self._wrapped(bullet, left + 0.35, y, width - 0.35, BODY_BOLD, 16, 0.31, INK)
            y -= 0.12
        y -= 0.25
        y = self._wrapped(BACK_CLOSING, left, y, width, BODY, 17, 0.33, DARK)
        self._theme_sample(left, y - 0.35, width)
        # Bottom-right stays empty: KDP prints the barcode there.

    def _theme_sample(self, left: float, top: float, width: float) -> None:
        self.c.setFont(BODY_BOLD, 17)
        self.c.setFillColor(self.main)
        self.c.drawString(left * INCH, top * INCH, "Algunos de los temas:")
        titles = [t.title for t in self.book.themes]
        picks = [titles[i] for i in range(0, len(titles), max(1, len(titles) // 12))][:12]
        col_w = width / 2
        rows = (len(picks) + 1) // 2
        barcode_top = self.trim_y0 + kdp.BARCODE_EDGE_IN + kdp.BARCODE_H_IN + 0.15
        for i, title in enumerate(picks):
            col, row = divmod(i, rows)
            y = top - 0.42 - row * 0.32
            assert y > barcode_top or col == 0, "theme list would touch the barcode area"
            self.c.setFont(BODY, 15)
            self.c.setFillColor(DARK)
            self.c.drawString((left + col * col_w) * INCH, y * INCH, f"·  {title}")

    def _wrapped(self, text, x, y, width, font, size, leading, color) -> float:
        self.c.setFont(font, size)
        self.c.setFillColor(color)
        line = ""
        for word in text.split():
            trial = f"{line} {word}".strip()
            if stringWidth(trial, font, size) <= width * INCH:
                line = trial
            else:
                self.c.drawString(x * INCH, y * INCH, line)
                y -= leading
                line = word
        if line:
            self.c.drawString(x * INCH, y * INCH, line)
            y -= leading
        return y

    def save(self) -> None:
        self.c.showPage()
        self.c.save()


def build_cover(book: Book, pages: int, out_path: Path, paper: str = "white",
                image: Path | None = None) -> tuple[float, float]:
    """Write the cover PDF and return its size in inches (width, height)."""
    out_path.parent.mkdir(parents=True, exist_ok=True)
    cover = Cover(out_path, book, pages, paper)
    cover.background()
    cover.front(image)
    cover.spine_text()
    cover.back()
    cover.save()
    return cover.width_in, cover.height_in
