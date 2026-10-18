import pytest

from plan_c_kdp.themes import MAX_WORDS, MIN_WORDS, THEMES_DIR, load_book
from plan_c_kdp.wordsearch import generate, verify

BOOKS = [load_book(p) for p in sorted(THEMES_DIR.glob("*.yaml"))]


def test_there_are_at_least_two_volumes_with_distinct_ids_and_themes():
    assert len(BOOKS) >= 2
    assert len({b.id for b in BOOKS}) == len(BOOKS)
    titles = [{t.title for t in b.themes} for b in BOOKS]
    for i in range(len(titles)):
        for j in range(i + 1, len(titles)):
            assert not titles[i] & titles[j], "volumes repeat theme titles"


@pytest.mark.parametrize("book", BOOKS, ids=lambda b: b.id)
def test_volume_has_100_themes_with_intro_and_12_to_18_words(book):
    assert len(book.themes) == 100
    for t in book.themes:
        assert t.intro and t.title
        assert MIN_WORDS <= len(t.words) <= MAX_WORDS


@pytest.mark.parametrize("book", BOOKS, ids=lambda b: b.id)
def test_every_theme_builds_a_verified_puzzle(book):
    for t in book.themes:
        puzzle = generate(list(t.words), size=15, seed=f"{book.id}:{t.id}")
        assert verify(puzzle) == [], t.id
