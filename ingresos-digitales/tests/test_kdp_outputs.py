import re

import pytest
from pypdf import PdfReader

from plan_c_kdp import kdp_specs as kdp
from plan_c_kdp.cover.builder import build_cover
from plan_c_kdp.interior.builder import (BOTTOM_IN, INSIDE_IN, OUTSIDE_IN, TOP_IN,
                                          build_interior)
from plan_c_kdp.listing.builder import KEYWORDS, title_and_subtitle, write_listing
from plan_c_kdp.themes import THEMES_DIR, load_book

@pytest.fixture(scope="module", params=sorted(THEMES_DIR.glob("*.yaml")), ids=lambda p: p.stem)
def built(request, tmp_path_factory):
    book = load_book(request.param)
    out = tmp_path_factory.mktemp(book.id)
    pages, puzzles = build_interior(book, out / "interior.pdf")
    build_cover(book, pages, out / "cover.pdf")
    write_listing(book, pages, out / "listing.md")
    return out, pages, puzzles, book


def _fonts_embedded(reader: PdfReader) -> set[str]:
    names = set()
    for page in reader.pages:
        fonts = page["/Resources"].get("/Font", {})
        for ref in fonts.values():
            font = ref.get_object()
            descendants = font.get("/DescendantFonts")
            target = descendants[0].get_object() if descendants else font
            descriptor = target["/FontDescriptor"].get_object()
            assert any(k in descriptor for k in ("/FontFile", "/FontFile2", "/FontFile3")), \
                f"font not embedded: {font['/BaseFont']}"
            names.add(str(font["/BaseFont"]))
    return names


def test_interior_page_size_count_and_fonts(built):
    out, pages, puzzles, _ = built
    reader = PdfReader(out / "interior.pdf")
    assert len(reader.pages) == pages
    assert pages % 2 == 0 and 24 <= pages <= 590  # B&W 8.5x11 white paper range
    for page in reader.pages:
        assert (float(page.mediabox.width), float(page.mediabox.height)) == (612, 792)
    assert INSIDE_IN >= kdp.min_inside_margin_in(pages)
    assert min(OUTSIDE_IN, TOP_IN, BOTTOM_IN) >= kdp.MIN_OUTSIDE_MARGIN_NO_BLEED_IN
    assert _fonts_embedded(reader)


def test_each_puzzle_page_shows_its_title_and_words(built):
    out, _, puzzles, _ = built
    reader = PdfReader(out / "interior.pdf")
    for bp in puzzles[:5] + puzzles[-5:]:
        text = reader.pages[bp.page - 1].extract_text()
        assert bp.theme.title in text
        for word in bp.puzzle.words:
            assert word in text


def test_cover_size_matches_kdp_formula_and_is_cmyk_only(built):
    out, pages, _, _ = built
    reader = PdfReader(out / "cover.pdf")
    assert len(reader.pages) == 1
    w_in, h_in = kdp.cover_size_in(pages)
    page = reader.pages[0]
    assert float(page.mediabox.width) == pytest.approx(w_in * 72, abs=0.01)
    assert float(page.mediabox.height) == pytest.approx(h_in * 72, abs=0.01)
    content = page.get_contents().get_data().decode("latin-1")
    assert not re.search(r"\b(rg|RG)\b", content), "RGB colour found in cover"
    assert _fonts_embedded(reader)


def test_listing_fits_kdp_limits(built):
    out, _, _, book = built
    title, subtitle = title_and_subtitle(book)
    assert len(title) + len(subtitle) <= 200
    kw = book.keywords or KEYWORDS
    assert len(kw) == 7 and all(len(k) <= 50 for k in kw)
    text = (out / "listing.md").read_text(encoding="utf-8")
    assert "Declaración de IA" in text and title in text


def test_kdp_spec_helpers():
    assert kdp.min_inside_margin_in(134) == 0.375
    assert kdp.min_inside_margin_in(151) == 0.5
    assert kdp.spine_width_in(100) == pytest.approx(0.2252)
    assert kdp.printing_cost(200, "USD") == 4.40  # KDP's own worked example
    assert kdp.royalty(9.99, 134) > kdp.royalty(9.98, 134)
