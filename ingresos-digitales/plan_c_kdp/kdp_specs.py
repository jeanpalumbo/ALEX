"""KDP paperback specs, checked against KDP help pages on 2026-10-18.

Sources:
- Interior margins/bleed: kdp.amazon.com/en_US/help/topic/GVBQ3CMEQW3W2VL6
- Cover size/spine:       kdp.amazon.com/en_US/help/topic/G201953020
- Printing cost:          kdp.amazon.com/en_US/help/topic/G201834340
- Royalty bands (EUR):    50% at <= 9.98 EUR, 60% at >= 9.99 EUR (re-check before pricing)
Re-check these pages before each new volume; KDP changes them from time to time.
"""

from __future__ import annotations

INCH = 72.0  # PDF points per inch

TRIM_W_IN, TRIM_H_IN = 8.5, 11.0
BLEED_IN = 0.125
MIN_OUTSIDE_MARGIN_NO_BLEED_IN = 0.25
COVER_SAFE_IN = 0.125          # keep cover text this far inside the trim
SPINE_TEXT_MIN_PAGES = 79      # KDP: more than 79 pages for spine text
SPINE_TEXT_CLEARANCE_IN = 0.0625
# KDP prints its barcode on the back cover, bottom right, if none is supplied.
BARCODE_W_IN, BARCODE_H_IN = 2.0, 1.2
BARCODE_EDGE_IN = 0.25

SPINE_PER_PAGE_IN = {"white": 0.002252, "cream": 0.0025}

_INSIDE_MARGIN_TABLE = [  # (max pages, inside margin in inches)
    (150, 0.375), (300, 0.5), (500, 0.625), (700, 0.75), (828, 0.875),
]


def min_inside_margin_in(pages: int) -> float:
    if pages < 24:
        raise ValueError("KDP paperbacks need at least 24 pages")
    for max_pages, margin in _INSIDE_MARGIN_TABLE:
        if pages <= max_pages:
            return margin
    raise ValueError("KDP paperbacks allow at most 828 pages")


def spine_width_in(pages: int, paper: str = "white") -> float:
    return pages * SPINE_PER_PAGE_IN[paper]


def cover_size_in(pages: int, paper: str = "white") -> tuple[float, float]:
    width = BLEED_IN + TRIM_W_IN + spine_width_in(pages, paper) + TRIM_W_IN + BLEED_IN
    height = BLEED_IN + TRIM_H_IN + BLEED_IN
    return width, height


def printing_cost(pages: int, marketplace: str = "EUR") -> float:
    """Black ink, large trim (8.5x11 counts as large), 110-828 pages."""
    fixed, per_page = {"EUR": (0.75, 0.016), "USD": (1.00, 0.017)}[marketplace]
    return round(fixed + pages * per_page, 2)


def royalty(list_price: float, pages: int, marketplace: str = "EUR") -> float:
    rate = 0.6 if list_price >= 9.99 else 0.5
    return round(rate * list_price - printing_cost(pages, marketplace), 2)
