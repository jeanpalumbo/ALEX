"""Build the Agenda 2027: interior, cover and listing in build/agenda2027/.

    python -m plan_c_kdp.agenda
"""

from __future__ import annotations

from pathlib import Path

from plan_c_kdp.agenda import AGENDA_YAML
from plan_c_kdp.agenda.builder import build_agenda
from plan_c_kdp.cover.builder import build_cover
from plan_c_kdp.listing.builder import write_listing
from plan_c_kdp.themes import load_book

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent


def main() -> None:
    book = load_book(AGENDA_YAML)
    out = PROJECT_ROOT / "build" / book.id
    interior = out / f"{book.id}_interior.pdf"
    pages, _ = build_agenda(book, AGENDA_YAML, interior)
    build_cover(book, pages, out / f"{book.id}_cover.pdf")
    write_listing(book, pages, out / "listing.md")
    print(f"[{book.id}] {pages} pages -> {out}")


if __name__ == "__main__":
    main()
