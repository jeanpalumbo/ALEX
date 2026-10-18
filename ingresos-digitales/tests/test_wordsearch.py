import pytest

from plan_c_kdp.wordsearch import DIRECTIONS, PuzzleError, find_all, generate, normalize, verify

WORDS = ["Peonza", "Chapas", "Canicas", "Comba", "Rayuela", "Escondite", "Tula", "Tabas",
         "Cometa", "Patines", "Aro", "Balón", "Goma", "Cromos", "Churro", "Muñeca"]


def test_normalize_strips_accents_but_keeps_enye():
    assert normalize("Balón") == "BALON"
    assert normalize("cigüeña") == "CIGUEÑA"
    assert normalize("  árbitro ") == "ARBITRO"


@pytest.mark.parametrize("bad", ["dos palabras", "abc1", "", "pre-fijo"])
def test_normalize_rejects_non_letters(bad):
    with pytest.raises(PuzzleError):
        normalize(bad)


def test_every_word_is_in_its_grid_exactly_once_and_matches_the_solution():
    for seed in range(30):
        puzzle = generate(WORDS, size=15, seed=seed)
        assert verify(puzzle) == []
        assert sorted(puzzle.words) == sorted(normalize(w) for w in WORDS)
        for p in puzzle.placements:
            spelled = "".join(puzzle.grid[r][c] for r, c in p.cells())
            assert spelled == p.word
            assert len(find_all(puzzle.grid, p.word)) == 1


def test_words_are_never_written_backwards():
    puzzle = generate(WORDS, seed=7)
    for p in puzzle.placements:
        dr, dc = DIRECTIONS[p.direction]
        assert dc >= 0 and not (dc == 0 and dr < 0)


def test_generation_is_deterministic():
    assert generate(WORDS, seed="x").grid == generate(WORDS, seed="x").grid


def test_verify_detects_a_broken_solution():
    puzzle = generate(WORDS, seed=1)
    r, c = puzzle.placements[0].cells()[0]
    puzzle.grid[r][c] = "Ñ" if puzzle.grid[r][c] != "Ñ" else "X"
    assert verify(puzzle)


@pytest.mark.parametrize("words, msg", [
    (["pan", "panadero", "leche"], "contained"),
    (["ana", "leche", "queso"], "palindrome"),
    (["supercalifragilistico", "uno"], "longer"),
    (["ab", "leche"], "short"),
])
def test_rejects_word_lists_that_cannot_give_a_unique_solution(words, msg):
    with pytest.raises(PuzzleError, match=msg):
        generate(words)
