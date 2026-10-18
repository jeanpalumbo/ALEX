"""Build everything for one or more KDP volumes.

    python -m plan_c_kdp.build                       # every volume in plan_c_kdp/themes/
    python -m plan_c_kdp.build --themes plan_c_kdp/themes/vol2_anos_60.yaml
    python -m plan_c_kdp.build --paper cream --cover-image assets/portada.png
"""

from __future__ import annotations

import argparse
from pathlib import Path

from plan_c_kdp.cover.builder import build_cover
from plan_c_kdp.interior.builder import build_interior
from plan_c_kdp.listing.builder import write_listing
from plan_c_kdp.themes import THEMES_DIR, load_book

PROJECT_ROOT = Path(__file__).resolve().parent.parent


def build_volume(themes: Path, out_root: Path, paper: str, cover_image: Path | None) -> None:
    book = load_book(themes)
    out = out_root / book.id
    interior = out / f"{book.id}_interior.pdf"
    pages, _ = build_interior(book, interior)
    cover = out / f"{book.id}_cover.pdf"
    build_cover(book, pages, cover, paper=paper, image=cover_image)
    listing = out / "listing.md"
    write_listing(book, pages, listing, paper=paper)
    print(f"[{book.id}] {book.subtitle}: {pages} pages")
    print(f"  interior: {interior}")
    print(f"  cover:    {cover}")
    print(f"  listing:  {listing}")


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--themes", type=Path, action="append",
                        help="theme YAML file (repeatable); default: all in plan_c_kdp/themes/")
    parser.add_argument("--paper", choices=["white", "cream"], default="white")
    parser.add_argument("--cover-image", type=Path, default=None,
                        help="optional front-cover illustration (only with a single --themes)")
    parser.add_argument("--out", type=Path, default=PROJECT_ROOT / "build")
    args = parser.parse_args(argv)

    files = args.themes or sorted(THEMES_DIR.glob("*.yaml"))
    if args.cover_image and len(files) != 1:
        parser.error("--cover-image needs exactly one --themes file")
    for themes in files:
        build_volume(themes, args.out, args.paper, args.cover_image)


if __name__ == "__main__":
    main()
