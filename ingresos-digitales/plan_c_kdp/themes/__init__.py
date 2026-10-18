"""Load and validate the theme YAML files that feed a book."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

import yaml

from plan_c_kdp.wordsearch import PuzzleError, normalize

THEMES_DIR = Path(__file__).resolve().parent
MIN_WORDS, MAX_WORDS = 12, 18


@dataclass(frozen=True)
class Theme:
    id: str
    title: str
    intro: str
    words: tuple[str, ...]


@dataclass(frozen=True)
class Book:
    id: str
    title: str
    subtitle: str
    volume: int
    author: str
    year: int
    themes: tuple[Theme, ...]
    # Optional per-volume settings so each book in the series looks and reads differently.
    cover_word: str = "RECUERDOS"
    palette: str = "terracotta"
    blurb: str = ""
    keywords: tuple[str, ...] = ()
    # Optional text overrides for products that are not plain puzzle books (e.g. the agenda).
    cover: dict = field(default_factory=dict)
    listing: dict = field(default_factory=dict)


def load_book(path: Path | str) -> Book:
    data = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    meta = data["book"]
    themes = tuple(
        Theme(id=t["id"], title=t["title"].strip(), intro=t["intro"].strip(),
              words=tuple(str(w) for w in t["words"]))
        for t in data["themes"]
    )
    book = Book(id=meta["id"], title=meta["title"], subtitle=meta["subtitle"],
                volume=int(meta["volume"]), author=meta["author"], year=int(meta["year"]),
                themes=themes, cover_word=meta.get("cover_word", "RECUERDOS"),
                palette=meta.get("palette", "terracotta"), blurb=meta.get("blurb", "").strip(),
                keywords=tuple(meta.get("keywords", ())), cover=meta.get("cover", {}),
                listing=meta.get("listing", {}))
    problems = validate(book)
    if problems:
        raise ValueError("invalid theme file:\n  " + "\n  ".join(problems))
    return book


def validate(book: Book) -> list[str]:
    problems = []
    seen = set()
    for t in book.themes:
        if t.id in seen:
            problems.append(f"duplicate theme id {t.id}")
        seen.add(t.id)
        if not t.title or not t.intro:
            problems.append(f"{t.id}: missing title or intro")
        if not MIN_WORDS <= len(t.words) <= MAX_WORDS:
            problems.append(f"{t.id}: {len(t.words)} words (expected {MIN_WORDS}-{MAX_WORDS})")
        for w in t.words:
            try:
                normalize(w)
            except PuzzleError as e:
                problems.append(f"{t.id}: {e}")
    return problems
