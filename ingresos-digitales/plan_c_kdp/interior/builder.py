"""Interior PDF: 8.5x11 in, no bleed, one large-print puzzle per page, solutions at the end.

Page plan (page 1 is a right-hand page in print):
  title · copyright · how to play · index (2 pages) · blank
  puzzles (one per page) · "Soluciones" divider · blank · solutions (4 per page)
  closing page · padding to an even page count
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from pathlib import Path

from reportlab.lib.colors import Color, black, white
from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.pdfgen.canvas import Canvas

from plan_c_kdp import kdp_specs
from plan_c_kdp.fonts import BODY, BODY_BOLD, register_fonts
from plan_c_kdp.themes import Book, Theme
from plan_c_kdp.wordsearch import DIRECTIONS, Puzzle, generate, verify

INCH = kdp_specs.INCH
PAGE_W, PAGE_H = kdp_specs.TRIM_W_IN * INCH, kdp_specs.TRIM_H_IN * INCH

# Generous margins: above the KDP minimums for any page count up to 300.
INSIDE_IN, OUTSIDE_IN, TOP_IN, BOTTOM_IN = 0.75, 0.5, 0.55, 0.6

GRID_SIZE = 15
GRID_LETTER_PT = 24
WORD_LIST_PT = 18           # plan requires >= 16 pt for the word list
INTRO_PT = 14
TITLE_PT = 26
WORD_ROW_H = 0.32 * INCH

INK = black
SOFT = Color(0.35, 0.35, 0.35)
LINE = Color(0.78, 0.78, 0.78)
FAINT = Color(0.62, 0.62, 0.62)

FRONT_MATTER_PAGES = 6      # title, copyright, how-to, index x2, blank


@dataclass
class BookPuzzle:
    number: int
    theme: Theme
    puzzle: Puzzle
    page: int


def build_puzzles(book: Book) -> list[BookPuzzle]:
    result = []
    for i, theme in enumerate(book.themes, start=1):
        puzzle = generate(list(theme.words), size=GRID_SIZE, seed=f"{book.id}:{theme.id}")
        problems = verify(puzzle)
        if problems:
            raise RuntimeError(f"{theme.id}: {problems}")
        result.append(BookPuzzle(i, theme, puzzle, page=FRONT_MATTER_PAGES + i))
    return result


class Interior:
    def __init__(self, path: Path, book: Book):
        register_fonts()
        self.book = book
        self.c = Canvas(str(path), pagesize=(PAGE_W, PAGE_H), initialFontName=BODY)
        self.c.setTitle(f"{book.title} — {book.subtitle} (Vol. {book.volume})")
        self.c.setAuthor(book.author)
        self.c.setSubject("Interior")
        self.page = 1

    # ---- page frame -------------------------------------------------------
    @property
    def left(self) -> float:
        inside_on_left = self.page % 2 == 1  # odd pages are right-hand pages
        return (INSIDE_IN if inside_on_left else OUTSIDE_IN) * INCH

    @property
    def right(self) -> float:
        inside_on_left = self.page % 2 == 1
        return PAGE_W - (OUTSIDE_IN if inside_on_left else INSIDE_IN) * INCH

    @property
    def top(self) -> float:
        return PAGE_H - TOP_IN * INCH

    @property
    def bottom(self) -> float:
        return BOTTOM_IN * INCH

    @property
    def center_x(self) -> float:
        return (self.left + self.right) / 2

    def next_page(self, number: bool = True) -> None:
        if number:
            self.c.setFont(BODY, 12)
            self.c.setFillColor(SOFT)
            self.c.drawCentredString(self.center_x, 0.32 * INCH, str(self.page))
        self.c.showPage()
        self.page += 1

    # ---- helpers ----------------------------------------------------------
    def centered(self, text: str, y: float, font: str, size: float, color=INK) -> None:
        self.c.setFont(font, size)
        self.c.setFillColor(color)
        self.c.drawCentredString(self.center_x, y, text)

    def wrap(self, text: str, font: str, size: float, width: float) -> list[str]:
        lines, current = [], ""
        for word in text.split():
            trial = f"{current} {word}".strip()
            if stringWidth(trial, font, size) <= width:
                current = trial
            else:
                lines.append(current)
                current = word
        if current:
            lines.append(current)
        return lines

    def paragraph(self, text: str, y: float, font: str, size: float, leading: float,
                  width: float | None = None, centered: bool = False, color=INK) -> float:
        width = width or (self.right - self.left)
        self.c.setFont(font, size)
        self.c.setFillColor(color)
        for line in self.wrap(text, font, size, width):
            if centered:
                self.c.drawCentredString(self.center_x, y, line)
            else:
                self.c.drawString(self.center_x - width / 2, y, line)
            y -= leading
        return y

    # ---- front matter -----------------------------------------------------
    def title_page(self) -> None:
        b = self.book
        y = PAGE_H * 0.68
        self.centered(b.title.upper(), y, BODY_BOLD, 30)
        self.centered(b.subtitle, y - 0.7 * INCH, BODY_BOLD, 40)
        self.c.setStrokeColor(INK)
        self.c.setLineWidth(1.5)
        self.c.line(self.center_x - 1.5 * INCH, y - 1.05 * INCH,
                    self.center_x + 1.5 * INCH, y - 1.05 * INCH)
        self.centered(f"{len(b.themes)} sopas de letras en letra muy grande", y - 1.6 * INCH,
                      BODY, 20)
        self.centered("con soluciones", y - 2.0 * INCH, BODY, 20)
        self.centered(f"Volumen {b.volume}", y - 3.0 * INCH, BODY_BOLD, 20)
        self.centered(b.author, self.bottom + 0.6 * INCH, BODY, 16, SOFT)
        self.next_page(number=False)

    def copyright_page(self) -> None:
        b = self.book
        lines = [
            f"{b.title} — {b.subtitle}. Volumen {b.volume}.",
            f"© {b.year} {b.author}. Todos los derechos reservados.",
            "",
            "Queda prohibida la reproducción total o parcial de esta obra, por cualquier "
            "medio, sin el permiso previo y por escrito del autor.",
            "",
            "Los temas y las palabras de este libro se han elegido para evocar recuerdos "
            "compartidos. Los nombres propios aparecen solo como palabras del pasatiempo.",
            "",
            "Tipografía: Atkinson Hyperlegible (Braille Institute of America), "
            "licencia SIL Open Font License 1.1.",
        ]
        y = self.bottom + 3.2 * INCH
        for line in lines:
            if not line:
                y -= 10
                continue
            y = self.paragraph(line, y, BODY, 12, 17)
        self.next_page(number=False)

    def how_to_page(self) -> None:
        y = self.top - 0.4 * INCH
        self.centered("Cómo jugar", y, BODY_BOLD, 34)
        y -= 0.8 * INCH
        rules = [
            "Busque en la cuadrícula las palabras de la lista. Cuando encuentre una, "
            "rodéela y marque la casilla que tiene al lado.",
            "Las palabras pueden estar en horizontal (de izquierda a derecha), en vertical "
            "(de arriba abajo) o en diagonal. Ninguna está escrita al revés.",
            "Las palabras aparecen en mayúsculas y sin tildes. La Ñ se mantiene, "
            "como en ESPAÑA.",
            "Las soluciones están al final del libro.",
            "No hay prisa: cada sopa es un pequeño viaje a los recuerdos. "
            "¡Disfrute de cada página!",
        ]
        width = self.right - self.left - 0.4 * INCH
        for rule in rules:
            self.c.setFillColor(INK)
            self.c.circle(self.center_x - width / 2 - 0.05 * INCH, y + 6, 4, stroke=0, fill=1)
            y = self.paragraph(rule, y, BODY, 20, 28, width=width - 0.25 * INCH) - 16
        self._example(y - 0.3 * INCH)
        self.next_page(number=False)

    def _example(self, top: float) -> None:
        rows = ["SOLBM", "PUCNA", "REIOR", "NAZUE", "CTELA"]
        words = [(0, 0, 0, 2), (0, 4, 2, 4), (1, 0, 3, 2), (4, 1, 4, 4)]  # SOL MAR PEZ TELA
        cell = 0.5 * INCH
        self.centered("Ejemplo: SOL y TELA en horizontal, MAR en vertical, PEZ en diagonal.",
                      top, BODY, 14, SOFT)
        top -= 0.25 * INCH
        x0 = self.center_x - 2.5 * cell
        self.c.setStrokeColor(INK)
        self.c.setLineWidth(1.2)
        self.c.roundRect(x0, top - 5 * cell, 5 * cell, 5 * cell, 4)
        for r0, c0, r1, c1 in words:
            self._capsule(x0, top, cell, r0, c0, r1, c1)
        self.c.setFont(BODY, 22)
        self.c.setFillColor(INK)
        for r, row in enumerate(rows):
            for col, ch in enumerate(row):
                self.c.drawCentredString(x0 + (col + 0.5) * cell, top - (r + 0.5) * cell - 8, ch)

    # ---- index ------------------------------------------------------------
    def index_pages(self, puzzles: list[BookPuzzle]) -> None:
        per_column = 25
        for start in (0, 50):
            y0 = self.top - 0.4 * INCH
            self.centered("Índice de temas", y0, BODY_BOLD, 28)
            col_w = (self.right - self.left - 0.4 * INCH) / 2
            for col in range(2):
                chunk = puzzles[start + col * per_column: start + (col + 1) * per_column]
                x = self.left + col * (col_w + 0.4 * INCH)
                y = y0 - 0.7 * INCH
                for bp in chunk:
                    self.c.setFont(BODY, 13)
                    self.c.setFillColor(INK)
                    label = f"{bp.number}. {bp.theme.title}"
                    self.c.drawString(x, y, label)
                    self.c.drawRightString(x + col_w, y, str(bp.page))
                    lw = stringWidth(label, BODY, 13)
                    self.c.setStrokeColor(LINE)
                    self.c.setDash(1, 3)
                    self.c.line(x + lw + 4, y + 2, x + col_w - 22, y + 2)
                    self.c.setDash()
                    y -= 0.33 * INCH
            self.next_page()

    # ---- puzzles ----------------------------------------------------------
    def puzzle_page(self, bp: BookPuzzle) -> None:
        assert self.page == bp.page, (self.page, bp.page)
        y = self.top - 0.3 * INCH
        self.c.setFillColor(INK)
        self.c.setFont(BODY_BOLD, 16)
        self.c.drawString(self.left, y + 4, f"Nº {bp.number}")
        self.centered(bp.theme.title, y, BODY_BOLD, TITLE_PT)
        y -= 0.42 * INCH
        y = self.paragraph(bp.theme.intro, y, BODY, INTRO_PT, 19,
                           width=self.right - self.left - 0.6 * INCH, centered=True,
                           color=SOFT)
        grid_top = y - 0.12 * INCH

        width = self.right - self.left
        list_rows = math.ceil(len(bp.puzzle.words) / 3)
        list_h = 0.38 * INCH + list_rows * WORD_ROW_H
        cell = min(width / GRID_SIZE, (grid_top - self.bottom - list_h) / GRID_SIZE,
                   0.47 * INCH)
        grid_w = cell * GRID_SIZE
        x0 = self.center_x - grid_w / 2
        self._grid(bp.puzzle, x0, grid_top, cell, GRID_LETTER_PT)
        self._word_list(bp.puzzle, grid_top - grid_w - 0.4 * INCH)
        self.next_page()

    def _grid(self, puzzle: Puzzle, x0: float, top: float, cell: float, font_size: float,
              solution: bool = False) -> None:
        size = puzzle.size
        c = self.c
        c.setLineWidth(0.4)
        c.setStrokeColor(LINE)
        for i in range(1, size):
            c.line(x0 + i * cell, top, x0 + i * cell, top - size * cell)
            c.line(x0, top - i * cell, x0 + size * cell, top - i * cell)
        c.setLineWidth(1.6 if not solution else 1)
        c.setStrokeColor(INK)
        c.roundRect(x0, top - size * cell, size * cell, size * cell, 4)
        if solution:
            for p in puzzle.placements:
                (r0, c0), (r1, c1) = p.cells()[0], p.cells()[-1]
                self._capsule(x0, top, cell, r0, c0, r1, c1)
        in_word = {cell_rc for p in puzzle.placements for cell_rc in p.cells()}
        baseline = font_size * 0.36
        for r, row in enumerate(puzzle.grid):
            for col, ch in enumerate(row):
                if solution:
                    highlighted = (r, col) in in_word
                    c.setFont(BODY_BOLD if highlighted else BODY, font_size)
                    c.setFillColor(INK if highlighted else FAINT)
                else:
                    c.setFont(BODY, font_size)
                    c.setFillColor(INK)
                c.drawCentredString(x0 + (col + 0.5) * cell, top - (r + 0.5) * cell - baseline, ch)

    def _capsule(self, x0, top, cell, r0, c0, r1, c1) -> None:
        cx0, cy0 = x0 + (c0 + 0.5) * cell, top - (r0 + 0.5) * cell
        cx1, cy1 = x0 + (c1 + 0.5) * cell, top - (r1 + 0.5) * cell
        length = math.hypot(cx1 - cx0, cy1 - cy0)
        angle = math.degrees(math.atan2(cy1 - cy0, cx1 - cx0))
        h = cell * 0.78
        c = self.c
        c.saveState()
        c.translate(cx0, cy0)
        c.rotate(angle)
        c.setStrokeColor(INK)
        c.setLineWidth(0.9)
        c.roundRect(-h / 2, -h / 2, length + h, h, h / 2, stroke=1, fill=0)
        c.restoreState()

    def _word_list(self, puzzle: Puzzle, top: float) -> None:
        words = puzzle.words
        cols = 3
        rows = math.ceil(len(words) / cols)
        width = self.right - self.left
        col_w = width / cols
        row_h = WORD_ROW_H
        box = 11
        for i, word in enumerate(words):
            col, row = divmod(i, rows)
            x = self.left + col * col_w + 0.15 * INCH
            y = top - row * row_h
            self.c.setStrokeColor(INK)
            self.c.setLineWidth(1)
            self.c.rect(x, y - 1, box, box)
            self.c.setFont(BODY, WORD_LIST_PT)
            self.c.setFillColor(INK)
            self.c.drawString(x + box + 8, y - 1, word)

    # ---- back matter ------------------------------------------------------
    def divider(self, title: str, subtitle: str) -> None:
        self.centered(title, PAGE_H / 2 + 20, BODY_BOLD, 44)
        self.centered(subtitle, PAGE_H / 2 - 30, BODY, 18, SOFT)
        self.next_page(number=False)

    def solutions(self, puzzles: list[BookPuzzle]) -> None:
        width = self.right - self.left
        gap = 0.35 * INCH
        slot_w = (width - gap) / 2
        cell = slot_w / GRID_SIZE
        for start in range(0, len(puzzles), 4):
            chunk = puzzles[start:start + 4]
            slot_h = (self.top - self.bottom) / 2
            for i, bp in enumerate(chunk):
                col, row = i % 2, i // 2
                x0 = self.left + col * (slot_w + gap)
                top = self.top - row * slot_h - 0.1 * INCH
                self.c.setFont(BODY_BOLD, 13)
                self.c.setFillColor(INK)
                label = f"Nº {bp.number} · {bp.theme.title}"
                while stringWidth(label, BODY_BOLD, 13) > slot_w and len(label) > 10:
                    label = label[:-2].rstrip() + "…"
                self.c.drawString(x0, top, label)
                self._grid(bp.puzzle, x0, top - 0.18 * INCH, cell, 10.5, solution=True)
            self.next_page()

    def closing_page(self, book: Book) -> None:
        y = PAGE_H * 0.62
        self.centered("¡Enhorabuena!", y, BODY_BOLD, 40)
        y -= 0.8 * INCH
        text = (f"Ha llegado al final de las {len(book.themes)} sopas de letras de "
                f"«{book.subtitle}». Esperamos que cada página le haya traído un buen recuerdo.")
        y = self.paragraph(text, y, BODY, 20, 28, width=self.right - self.left - 0.8 * INCH,
                           centered=True)
        y -= 0.4 * INCH
        text = ("Si le ha gustado este libro, una opinión sincera en Amazon nos ayuda mucho "
                "a seguir preparando nuevos volúmenes.")
        self.paragraph(text, y, BODY, 16, 23, width=self.right - self.left - 1.2 * INCH,
                       centered=True, color=SOFT)
        self.next_page(number=False)

    def save(self) -> int:
        if (self.page - 1) % 2:
            self.next_page(number=False)  # blank page: KDP prints in sheets of 2
        self.c.save()
        return self.page - 1


def build_interior(book: Book, out_path: Path) -> tuple[int, list[BookPuzzle]]:
    """Write the interior PDF. Returns (page count, puzzles with their page numbers)."""
    puzzles = build_puzzles(book)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    doc = Interior(out_path, book)
    doc.title_page()
    doc.copyright_page()
    doc.how_to_page()
    doc.index_pages(puzzles)
    doc.next_page(number=False)  # blank, so puzzle 1 starts on page 7 (right-hand)
    for bp in puzzles:
        doc.puzzle_page(bp)
    doc.divider("Soluciones", "Las palabras encontradas aparecen rodeadas.")
    doc.next_page(number=False)
    doc.solutions(puzzles)
    doc.closing_page(book)
    pages = doc.save()
    kdp_specs.min_inside_margin_in(pages)  # raises if out of KDP range
    if INSIDE_IN < kdp_specs.min_inside_margin_in(pages):
        raise RuntimeError(f"inside margin {INSIDE_IN} in is too small for {pages} pages")
    return pages, puzzles
