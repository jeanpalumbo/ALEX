from datetime import date

import pytest
from pypdf import PdfReader

from plan_c_kdp import kdp_specs as kdp
from plan_c_kdp.agenda import AGENDA_YAML
from plan_c_kdp.agenda.builder import (FRONT_PAGES, build_agenda, common_holidays, day_labels,
                                       easter, load_refranes, weeks)
from plan_c_kdp.cover.builder import build_cover
from plan_c_kdp.listing.builder import title_and_subtitle, write_listing
from plan_c_kdp.themes import load_book
from plan_c_kdp.wordsearch import verify

BOOK = load_book(AGENDA_YAML)


def test_easter_dates():
    assert easter(2026) == date(2026, 4, 5)
    assert easter(2027) == date(2027, 3, 28)


def test_2027_common_holidays_match_the_boe():
    # BOE 13 Oct 2026: nine holidays common to all of Spain in 2027 (15 Aug is a Sunday).
    h = common_holidays(2027)
    assert set(h) == {date(2027, 1, 1), date(2027, 1, 6), date(2027, 3, 26), date(2027, 5, 1),
                      date(2027, 10, 12), date(2027, 11, 1), date(2027, 12, 6),
                      date(2027, 12, 8), date(2027, 12, 25)}
    labels = day_labels()
    assert labels[date(2027, 8, 15)][1] is False and "domingo" in labels[date(2027, 8, 15)][0]
    assert "comunidades" in labels[date(2027, 8, 16)][0]


def test_weeks_start_on_monday_and_cover_the_whole_year():
    ws = weeks(len(BOOK.themes))
    assert all(w.monday.weekday() == 0 for w in ws)
    assert ws[0].days[0] <= date(2027, 1, 1) <= ws[0].days[-1]
    assert ws[-1].days[-1] >= date(2027, 12, 31)
    assert len(BOOK.themes) == len(load_refranes(AGENDA_YAML)) == 53


def test_same_day_events_are_merged():
    text, is_holiday = day_labels()[date(2027, 3, 28)]
    assert "Pascua" in text and "reloj" in text and not is_holiday


@pytest.fixture(scope="module")
def built(tmp_path_factory):
    out = tmp_path_factory.mktemp("agenda")
    pages, puzzles = build_agenda(BOOK, AGENDA_YAML, out / "interior.pdf")
    build_cover(BOOK, pages, out / "cover.pdf")
    write_listing(BOOK, pages, out / "listing.md")
    return out, pages, puzzles


def test_agenda_pdf_layout(built):
    out, pages, puzzles = built
    reader = PdfReader(out / "interior.pdf")
    assert len(reader.pages) == pages and pages % 2 == 0
    assert kdp.min_inside_margin_in(pages) <= 0.75
    for bp in puzzles:
        assert verify(bp.puzzle) == []
        assert bp.page % 2 == 1  # puzzle on the right-hand page
        week_text = reader.pages[bp.page - 2].extract_text()  # facing left-hand page
        assert f"Semana {bp.number}" in week_text
        assert bp.theme.title in reader.pages[bp.page - 1].extract_text()
    assert puzzles[0].page == FRONT_PAGES + 2
    assert "Viernes Santo" in reader.pages[puzzles[12].page - 2].extract_text()


def test_agenda_listing_and_cover(built):
    out, pages, _ = built
    title, subtitle = title_and_subtitle(BOOK)
    assert title.startswith("Agenda 2027") and len(title) + len(subtitle) <= 200
    text = (out / "listing.md").read_text(encoding="utf-8")
    assert "Agenda 2027" in text and "Sopa de letras para mayores —" not in text
    cover = PdfReader(out / "cover.pdf").pages[0]
    assert float(cover.mediabox.width) == pytest.approx(kdp.cover_size_in(pages)[0] * 72, abs=0.01)
