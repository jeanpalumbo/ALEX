"""Register the bundled OFL fonts with reportlab (TTF fonts are embedded as subsets)."""

from __future__ import annotations

from pathlib import Path

from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

FONTS_DIR = Path(__file__).resolve().parent / "assets" / "fonts"

BODY = "Atkinson"            # Atkinson Hyperlegible: designed for low-vision readers
BODY_BOLD = "Atkinson-Bold"
DISPLAY = "AbrilFatface"     # cover titles only

_FILES = {
    BODY: "AtkinsonHyperlegible-Regular.ttf",
    BODY_BOLD: "AtkinsonHyperlegible-Bold.ttf",
    DISPLAY: "AbrilFatface-Regular.ttf",
}


def register_fonts() -> None:
    for name, filename in _FILES.items():
        if name not in pdfmetrics.getRegisteredFontNames():
            pdfmetrics.registerFont(TTFont(name, str(FONTS_DIR / filename)))
