"""Agenda 2027 para mayores: week-to-view planner with one seasonal word search per week.

Page plan (8.5x11 in, page 1 is a right-hand page):
  1 title · 2 copyright · 3 how to use · 4 personal & medical details · 5 phone numbers
  6 birthdays · 7-8 year at a glance · 9 holidays
  then one spread per week: week planner on the left (even page), puzzle on the right
  solutions (4 per page) · closing page
"""

from __future__ import annotations

import calendar
from dataclasses import dataclass
from datetime import date, timedelta
from pathlib import Path

import yaml
from reportlab.lib.colors import Color
from reportlab.pdfbase.pdfmetrics import stringWidth

from plan_c_kdp.interior.builder import (BODY, BODY_BOLD, INCH, INK, LINE, PAGE_H, SOFT,
                                          BookPuzzle, Interior, build_puzzles)
from plan_c_kdp.themes import Book

FIRST_MONDAY = date(2026, 12, 28)   # week 1 contains 1 January 2027
YEAR = 2027
FRONT_PAGES = 9

MONTHS = ["enero", "febrero", "marzo", "abril", "mayo", "junio", "julio", "agosto",
          "septiembre", "octubre", "noviembre", "diciembre"]
WEEKDAYS = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
SHADE = Color(0.90, 0.90, 0.90)


def easter(year: int) -> date:
    """Gregorian Easter Sunday (anonymous algorithm)."""
    a, b, c = year % 19, year // 100, year % 100
    d, e = b // 4, b % 4
    f = (b + 8) // 25
    g = (b - f + 1) // 3
    h = (19 * a + b - d - g + 15) % 30
    i, k = c // 4, c % 4
    l = (32 + 2 * e + 2 * i - h - k) % 7
    m = (a + 11 * h + 22 * l) // 451
    month = (h + l - 7 * m + 114) // 31
    day = (h + l - 7 * m + 114) % 31 + 1
    return date(year, month, day)


def last_sunday(year: int, month: int) -> date:
    d = date(year, month, calendar.monthrange(year, month)[1])
    return d - timedelta(days=(d.weekday() - 6) % 7)


def holidays(year: int) -> dict[date, str]:
    """National public holidays (fiestas nacionales) common to all of Spain."""
    e = easter(year)
    return {
        date(year, 1, 1): "Año Nuevo",
        date(year, 1, 6): "Epifanía del Señor (Reyes)",
        e - timedelta(days=2): "Viernes Santo",
        date(year, 5, 1): "Fiesta del Trabajo",
        date(year, 8, 15): "Asunción de la Virgen",
        date(year, 10, 12): "Fiesta Nacional de España",
        date(year, 11, 1): "Todos los Santos",
        date(year, 12, 6): "Día de la Constitución",
        date(year, 12, 8): "Inmaculada Concepción",
        date(year, 12, 25): "Navidad",
    }


def common_holidays(year: int) -> dict[date, str]:
    """Holidays common to all of Spain. A national holiday that falls on a Sunday is not one:
    each region decides whether to move it (e.g. 15 Aug 2027 -> Mon 16 Aug in several).
    Checked against the BOE resolution of 8 Oct 2026 (BOE 13 Oct 2026) for 2027."""
    return {d: t for d, t in holidays(year).items() if d.weekday() != 6}


def notable_days(year: int) -> dict[date, str]:
    """Other dates worth showing; not public holidays everywhere."""
    e = easter(year)
    first_may_sunday = date(year, 5, 1) + timedelta(days=(6 - date(year, 5, 1).weekday()) % 7)
    entries = [
        (e - timedelta(days=47), "Martes de Carnaval"),
        (date(year, 2, 14), "San Valentín"),
        (date(year, 3, 19), "San José · Día del Padre"),
        (e - timedelta(days=7), "Domingo de Ramos"),
        (e - timedelta(days=3), "Jueves Santo (festivo en casi toda España)"),
        (e, "Domingo de Pascua"),
        (e + timedelta(days=1), "Lunes de Pascua (festivo en algunas comunidades)"),
        (last_sunday(year, 3), "Adelantar el reloj 1 hora"),
        (date(year, 4, 23), "Día del Libro"),
        (first_may_sunday, "Día de la Madre"),
        (date(year, 5, 15), "San Isidro"),
        (date(year, 6, 24), "San Juan"),
        (date(year, 7, 25), "Santiago Apóstol"),
        (date(year, 7, 26), "Día de los Abuelos"),
        (last_sunday(year, 10), "Atrasar el reloj 1 hora"),
        (date(year, 12, 22), "Sorteo de la Lotería de Navidad"),
        (date(year, 12, 24), "Nochebuena"),
        (date(year, 12, 28), "Santos Inocentes"),
        (date(year, 12, 31), "Nochevieja"),
    ]
    for d, text in holidays(year).items():
        if d.weekday() == 6:
            entries.append((d, f"{text} (cae en domingo)"))
            entries.append((d + timedelta(days=1), "Festivo en varias comunidades"))
    labels: dict[date, str] = {}
    for d, text in entries:  # two events on one day (e.g. Easter and the clock change)
        labels[d] = f"{labels[d]} · {text}" if d in labels else text
    return labels


def day_labels() -> dict[date, tuple[str, bool]]:
    """Label for every marked day in the agenda's range: (text, is_public_holiday)."""
    labels: dict[date, tuple[str, bool]] = {}
    for year in (YEAR - 1, YEAR, YEAR + 1):
        for d, text in notable_days(year).items():
            labels[d] = (text, False)
        for d, text in common_holidays(year).items():
            labels[d] = (text, True)
    return labels


@dataclass
class Week:
    number: int
    monday: date

    @property
    def days(self) -> list[date]:
        return [self.monday + timedelta(days=i) for i in range(7)]


def weeks(count: int) -> list[Week]:
    return [Week(i + 1, FIRST_MONDAY + timedelta(weeks=i)) for i in range(count)]


def long_date(d: date) -> str:
    return f"{d.day} de {MONTHS[d.month - 1]} de {d.year}"


def range_text(w: Week) -> str:
    a, b = w.days[0], w.days[-1]
    if a.year != b.year:
        return f"Del {long_date(a)} al {long_date(b)}"
    if a.month != b.month:
        return f"Del {a.day} de {MONTHS[a.month - 1]} al {b.day} de {MONTHS[b.month - 1]} de {b.year}"
    return f"Del {a.day} al {b.day} de {MONTHS[a.month - 1]} de {a.year}"


class AgendaInterior(Interior):
    number_label = "Semana"

    def __init__(self, path: Path, book: Book, refranes: list[str]):
        super().__init__(path, book)
        self.c.setTitle(book.title)
        self.refranes = refranes
        self.labels = day_labels()

    # ---- front matter -----------------------------------------------------
    def agenda_title_page(self) -> None:
        y = PAGE_H * 0.66
        self.centered("AGENDA", y, BODY_BOLD, 64)
        self.centered(str(YEAR), y - 1.1 * INCH, BODY_BOLD, 80)
        self.centered("para mayores, en letra grande", y - 1.7 * INCH, BODY, 24)
        self.centered(f"Semana a la vista y {len(self.book.themes)} sopas de letras",
                      y - 2.4 * INCH, BODY, 20, SOFT)
        self.centered("Esta agenda pertenece a:", self.bottom + 1.6 * INCH, BODY, 18)
        self.c.setStrokeColor(INK)
        self.c.line(self.center_x - 2.5 * INCH, self.bottom + 1.0 * INCH,
                    self.center_x + 2.5 * INCH, self.bottom + 1.0 * INCH)
        self.next_page(number=False)

    def agenda_copyright_page(self) -> None:
        b = self.book
        lines = [
            f"{b.title}. © {b.year} {b.author}. Todos los derechos reservados.",
            "",
            "Festivos: se indican las fiestas nacionales comunes a toda España. Cada comunidad "
            "autónoma y cada municipio añade sus propios festivos; consúltelos en su "
            "ayuntamiento o en el boletín oficial de su comunidad.",
            "",
            "Los refranes son tradicionales y de dominio público.",
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

    def how_to_use_page(self) -> None:
        y = self.top - 0.4 * INCH
        self.centered("Cómo usar esta agenda", y, BODY_BOLD, 32)
        y -= 0.8 * INCH
        rules = [
            "Cada semana ocupa dos páginas: a la izquierda, los siete días con espacio para "
            "apuntar; a la derecha, una sopa de letras con un tema de esa época del año.",
            "Los festivos nacionales aparecen en un recuadro gris. Otras fechas señaladas, "
            "como el Día de la Madre o el cambio de hora, se indican debajo del día.",
            "En las sopas de letras, las palabras van en horizontal, en vertical o en "
            "diagonal, nunca al revés, y sin tildes. Las soluciones están al final.",
            "Al principio encontrará páginas para sus datos médicos, los teléfonos "
            "importantes y los cumpleaños de la familia.",
            "Cada semana trae un refrán de los de siempre. ¡Que tenga un feliz 2027!",
        ]
        width = self.right - self.left - 0.4 * INCH
        for rule in rules:
            self.c.setFillColor(INK)
            self.c.circle(self.center_x - width / 2 - 0.05 * INCH, y + 6, 4, stroke=0, fill=1)
            y = self.paragraph(rule, y, BODY, 19, 27, width=width - 0.25 * INCH) - 18
        self.next_page()

    def _field_lines(self, fields: list[tuple[str, int]], y: float, size: float = 17) -> None:
        for label, lines in fields:
            self.c.setFont(BODY_BOLD, size)
            self.c.setFillColor(INK)
            self.c.drawString(self.left, y, label)
            y -= 0.42 * INCH
            for _ in range(lines):
                self.c.setStrokeColor(SOFT)
                self.c.setLineWidth(0.7)
                self.c.line(self.left, y, self.right, y)
                y -= 0.42 * INCH
            y -= 0.05 * INCH

    def personal_page(self) -> None:
        self.centered("Mis datos", self.top - 0.4 * INCH, BODY_BOLD, 32)
        fields = [("Nombre y apellidos", 1), ("Dirección", 1), ("Teléfono", 1),
                  ("En caso de urgencia, avisar a (nombre y teléfono)", 1),
                  ("Médico de cabecera y centro de salud", 1),
                  ("Número de tarjeta sanitaria", 1), ("Grupo sanguíneo y alergias", 1),
                  ("Medicación habitual", 3)]
        self._field_lines(fields, self.top - 1.2 * INCH)
        self.next_page()

    def phones_page(self) -> None:
        self.centered("Teléfonos importantes", self.top - 0.4 * INCH, BODY_BOLD, 32)
        y = self.top - 1.2 * INCH
        name_w = (self.right - self.left) * 0.6
        self.c.setFont(BODY_BOLD, 17)
        self.c.drawString(self.left, y, "Nombre")
        self.c.drawString(self.left + name_w + 0.2 * INCH, y, "Teléfono")
        y -= 0.5 * INCH
        self.c.setFont(BODY, 17)
        self.c.drawString(self.left, y + 6, "Emergencias")
        self.c.drawString(self.left + name_w + 0.2 * INCH, y + 6, "112")
        rows = 15
        for i in range(rows):
            self.c.setStrokeColor(SOFT)
            self.c.setLineWidth(0.7)
            self.c.line(self.left, y, self.left + name_w, y)
            self.c.line(self.left + name_w + 0.2 * INCH, y, self.right, y)
            y -= 0.52 * INCH
        self.next_page()

    def birthdays_page(self) -> None:
        self.centered("Cumpleaños y fechas importantes", self.top - 0.4 * INCH, BODY_BOLD, 28)
        top = self.top - 1.0 * INCH
        col_w = (self.right - self.left - 0.3 * INCH) / 2
        box_h = (top - self.bottom) / 6
        for m in range(12):
            col, row = m // 6, m % 6
            x = self.left + col * (col_w + 0.3 * INCH)
            y = top - row * box_h
            self.c.setStrokeColor(INK)
            self.c.setLineWidth(1)
            self.c.roundRect(x, y - box_h + 0.1 * INCH, col_w, box_h - 0.15 * INCH, 6)
            self.c.setFont(BODY_BOLD, 17)
            self.c.setFillColor(INK)
            self.c.drawString(x + 0.12 * INCH, y - 0.32 * INCH, MONTHS[m].capitalize())
            for k in range(2):
                ly = y - 0.75 * INCH - k * 0.42 * INCH
                self.c.setStrokeColor(LINE)
                self.c.line(x + 0.12 * INCH, ly, x + col_w - 0.12 * INCH, ly)
        self.next_page()

    def year_pages(self) -> None:
        hol = common_holidays(YEAR)
        for half in (0, 1):
            title = f"Calendario {YEAR}" + (" · enero a junio" if half == 0 else " · julio a diciembre")
            self.centered(title, self.top - 0.35 * INCH, BODY_BOLD, 26)
            top = self.top - 0.9 * INCH
            col_w = (self.right - self.left - 0.4 * INCH) / 2
            box_h = (top - self.bottom - 0.4 * INCH) / 3
            for i in range(6):
                m = half * 6 + i + 1
                col, row = i % 2, i // 2
                x = self.left + col * (col_w + 0.4 * INCH)
                y = top - row * box_h
                self._month(m, x, y, col_w, hol)
            self.c.setFont(BODY, 13)
            self.c.setFillColor(SOFT)
            self.c.drawString(self.left, self.bottom + 0.05 * INCH,
                              "Los días rodeados con un círculo son festivos nacionales.")
            self.next_page()

    def _month(self, month: int, x: float, top: float, width: float, hol: dict) -> None:
        cell = width / 7
        self.c.setFont(BODY_BOLD, 18)
        self.c.setFillColor(INK)
        self.c.drawCentredString(x + width / 2, top - 0.1 * INCH, MONTHS[month - 1].capitalize())
        self.c.setFont(BODY_BOLD, 13)
        for i, name in enumerate("LMXJVSD"):
            self.c.drawCentredString(x + (i + 0.5) * cell, top - 0.45 * INCH, name)
        row_h = 0.36 * INCH
        for week_i, week in enumerate(calendar.Calendar().monthdatescalendar(YEAR, month)):
            for i, d in enumerate(week):
                if d.month != month:
                    continue
                cx = x + (i + 0.5) * cell
                cy = top - 0.8 * INCH - week_i * row_h
                if d in hol:
                    self.c.setStrokeColor(INK)
                    self.c.setLineWidth(1.3)
                    self.c.circle(cx, cy + 5, 11, stroke=1, fill=0)
                self.c.setFont(BODY_BOLD if i >= 5 or d in hol else BODY, 15)
                self.c.drawCentredString(cx, cy, str(d.day))

    def holidays_page(self) -> None:
        self.centered(f"Festivos nacionales {YEAR}", self.top - 0.4 * INCH, BODY_BOLD, 30)
        y = self.top - 1.2 * INCH
        for d, text in sorted(common_holidays(YEAR).items()):
            self.c.setFont(BODY_BOLD, 18)
            self.c.setFillColor(INK)
            self.c.drawString(self.left, y, f"{WEEKDAYS[d.weekday()]} {d.day} de {MONTHS[d.month - 1]}")
            self.c.setFont(BODY, 18)
            self.c.drawString(self.left + 3.4 * INCH, y, text)
            y -= 0.4 * INCH
        y -= 0.3 * INCH
        y = self.paragraph("El 15 de agosto cae en domingo: varias comunidades lo pasan al "
                           "lunes 16. Además, cada comunidad y cada pueblo tiene sus propios "
                           "festivos. Apúntelos aquí:", y, BODY, 17, 24)
        for _ in range(4):
            y -= 0.3 * INCH
            self.c.setStrokeColor(SOFT)
            self.c.line(self.left, y, self.right, y)
            y -= 0.12 * INCH
        self.next_page()

    # ---- weeks ------------------------------------------------------------
    def week_page(self, week: Week, refran: str) -> None:
        assert self.page % 2 == 0, "week pages must be left-hand (even) pages"
        y = self.top - 0.25 * INCH
        self.centered(f"Semana {week.number}", y, BODY_BOLD, 24)
        y -= 0.33 * INCH
        self.centered(range_text(week), y, BODY, 17, SOFT)

        refran_h = 0.9 * INCH
        area_top = y - 0.2 * INCH
        area_bottom = self.bottom + refran_h + 0.15 * INCH
        block = (area_top - area_bottom) / 7
        date_w = 1.55 * INCH
        for i, d in enumerate(week.days):
            top = area_top - i * block
            label, is_holiday = self.labels.get(d, ("", False))
            if is_holiday:
                self.c.setFillColor(SHADE)
                self.c.rect(self.left, top - block, self.right - self.left, block, stroke=0, fill=1)
            self.c.setStrokeColor(INK)
            self.c.setLineWidth(1.2)
            self.c.line(self.left, top, self.right, top)
            self.c.setFillColor(INK)
            self.c.setFont(BODY_BOLD, 17)
            self.c.drawString(self.left + 0.08 * INCH, top - 0.3 * INCH, WEEKDAYS[d.weekday()])
            self.c.setFont(BODY_BOLD, 30)
            self.c.drawString(self.left + 0.08 * INCH, top - 0.75 * INCH, str(d.day))
            self.c.setFont(BODY, 14)
            day_w = stringWidth(str(d.day), BODY_BOLD, 30)
            self.c.drawString(self.left + 0.08 * INCH + day_w + 5, top - 0.75 * INCH,
                              MONTHS[d.month - 1][:3])
            x_lines = self.left + date_w
            if label:
                font = BODY_BOLD if is_holiday else BODY
                text = f"Festivo: {label}" if is_holiday else label
                size = 16.0
                while stringWidth(text, font, size) > self.right - x_lines - 4 and size > 11:
                    size -= 0.5
                self.c.setFont(font, size)
                self.c.drawString(x_lines, top - 0.28 * INCH, text)
            n_lines = 2
            for k in range(n_lines):
                ly = top - block * (k + 1) / (n_lines + 1) - (0.1 * INCH if label else 0)
                self.c.setStrokeColor(LINE)
                self.c.setLineWidth(0.6)
                self.c.line(x_lines, ly, self.right - 0.1 * INCH, ly)
        self.c.setStrokeColor(INK)
        self.c.line(self.left, area_bottom, self.right, area_bottom)

        box_top = self.bottom + refran_h
        self.c.setLineWidth(1)
        self.c.roundRect(self.left, self.bottom, self.right - self.left, refran_h, 8)
        self.c.setFont(BODY_BOLD, 13)
        self.c.setFillColor(SOFT)
        self.c.drawString(self.left + 0.15 * INCH, box_top - 0.28 * INCH, "Refrán de la semana")
        self.c.setFillColor(INK)
        self.c.setFont(BODY, 19)
        self.c.drawString(self.left + 0.15 * INCH, box_top - 0.66 * INCH, f"«{refran}»")
        self.next_page()

    def agenda_closing_page(self) -> None:
        y = PAGE_H * 0.62
        self.centered("¡Feliz año nuevo!", y, BODY_BOLD, 40)
        y -= 0.8 * INCH
        text = ("Gracias por dejarnos acompañarle durante todo el año, semana a semana. "
                "Esperamos que estas páginas le hayan sido útiles y entretenidas.")
        y = self.paragraph(text, y, BODY, 20, 28, width=self.right - self.left - 0.8 * INCH,
                           centered=True)
        y -= 0.4 * INCH
        text = ("Si le ha gustado esta agenda, una opinión sincera en Amazon nos ayuda mucho "
                "a preparar la del año que viene.")
        self.paragraph(text, y, BODY, 16, 23, width=self.right - self.left - 1.2 * INCH,
                       centered=True, color=SOFT)
        self.next_page(number=False)


def load_refranes(path: Path) -> list[str]:
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    return [t["refran"].strip() for t in data["themes"]]


def build_agenda(book: Book, themes_path: Path, out_path: Path) -> tuple[int, list[BookPuzzle]]:
    refranes = load_refranes(themes_path)
    week_list = weeks(len(book.themes))
    assert week_list[-1].days[-1] >= date(YEAR, 12, 31), "agenda must cover the whole year"
    puzzles = build_puzzles(book)
    for bp in puzzles:
        bp.page = FRONT_PAGES + 2 * bp.number  # right-hand page of each spread
    out_path.parent.mkdir(parents=True, exist_ok=True)
    doc = AgendaInterior(out_path, book, refranes)
    doc.agenda_title_page()
    doc.agenda_copyright_page()
    doc.how_to_use_page()
    doc.personal_page()
    doc.phones_page()
    doc.birthdays_page()
    doc.year_pages()
    doc.holidays_page()
    for week, bp, refran in zip(week_list, puzzles, refranes):
        doc.week_page(week, refran)
        doc.puzzle_page(bp)
    doc.solutions(puzzles)
    doc.agenda_closing_page()
    return doc.save(), puzzles
