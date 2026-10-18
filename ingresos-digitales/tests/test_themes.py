from plan_c_kdp.themes import MAX_WORDS, MIN_WORDS, THEMES_DIR, load_book
from plan_c_kdp.wordsearch import generate, verify

BOOK = load_book(THEMES_DIR / "vol1_recuerdos_de_espana.yaml")


def test_vol1_has_about_100_themes_with_intro_and_12_to_18_words():
    assert len(BOOK.themes) == 100
    for t in BOOK.themes:
        assert t.intro and t.title
        assert MIN_WORDS <= len(t.words) <= MAX_WORDS


def test_every_theme_builds_a_verified_puzzle():
    for t in BOOK.themes:
        puzzle = generate(list(t.words), size=15, seed=f"{BOOK.id}:{t.id}")
        assert verify(puzzle) == [], t.id
