"""Build everything for a KDP volume.

    python -m plan_c_kdp.build                 # Vol. 1, outputs in build/vol1/
    python -m plan_c_kdp.build --paper cream
"""

from __future__ import annotations

import argparse
from pathlib import Path

from plan_c_kdp.cover.builder import build_cover
from plan_c_kdp.interior.builder import build_interior
from plan_c_kdp.listing.builder import write_listing
from plan_c_kdp.themes import THEMES_DIR, load_book

PROJECT_ROOT = Path(__file__).resolve().parent.parent


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--themes", type=Path,
                        default=THEMES_DIR / "vol1_recuerdos_de_espana.yaml")
    parser.add_argument("--paper", choices=["white", "cream"], default="white")
    parser.add_argument("--cover-image", type=Path, default=None,
                        help="optional front-cover illustration (e.g. assets/cover.png)")
    parser.add_argument("--out", type=Path, default=None)
    args = parser.parse_args(argv)

    book = load_book(args.themes)
    out = args.out or PROJECT_ROOT / "build" / book.id
    interior = out / f"{book.id}_interior.pdf"
    pages, _ = build_interior(book, interior)
    cover = out / f"{book.id}_cover.pdf"
    build_cover(book, pages, cover, paper=args.paper, image=args.cover_image)
    listing = out / "listing.md"
    write_listing(book, pages, listing, paper=args.paper)
    print(f"interior: {interior} ({pages} pages)")
    print(f"cover:    {cover}")
    print(f"listing:  {listing}")


if __name__ == "__main__":
    main()
