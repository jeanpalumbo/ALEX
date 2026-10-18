"""Word search generator for large-print books aimed at older readers.

Spelling rules (decided for Vol. 1, see README):
- Uppercase only. Accents and diaeresis are removed (Á -> A, Ü -> U) so the word
  in the list is spelled exactly as in the grid.
- Ñ is kept as its own letter: it is a distinct letter in Spanish and readers
  expect ESPAÑA, not ESPANA.
- Words read only forwards: left to right, top to bottom, and the two diagonals
  that read left to right (down-right and up-right). Nothing is written backwards.
- Each word appears exactly once in the grid (checked in all 8 directions), and
  the filler never spells a word from a small offensive-word blocklist.
"""

from __future__ import annotations

import random
import unicodedata
from dataclasses import dataclass, field

# (row step, col step), all reading left-to-right or top-to-bottom.
DIRECTIONS = {
    "E": (0, 1),
    "S": (1, 0),
    "SE": (1, 1),
    "NE": (-1, 1),
}
# Horizontal and vertical are the easiest to spot, so they dominate.
DIRECTION_WEIGHTS = {"E": 0.4, "S": 0.3, "SE": 0.18, "NE": 0.12}
ALL_STEPS = [(dr, dc) for dr in (-1, 0, 1) for dc in (-1, 0, 1) if (dr, dc) != (0, 0)]

ALPHABET = "ABCDEFGHIJKLMNÑOPQRSTUVWXYZ"
# Approximate Spanish letter frequencies (%). Ñ, K, W are left out of the filler
# on purpose: rare letters in the filler only add noise for the reader.
FILLER_WEIGHTS = {
    "A": 12.5, "B": 1.4, "C": 4.7, "D": 5.9, "E": 13.7, "F": 0.7, "G": 1.0, "H": 0.7,
    "I": 6.2, "J": 0.4, "L": 5.0, "M": 3.2, "N": 6.7, "O": 8.7, "P": 2.5, "Q": 0.9,
    "R": 6.9, "S": 8.0, "T": 4.6, "U": 3.9, "V": 0.9, "X": 0.2, "Y": 0.9, "Z": 0.5,
}
BLOCKLIST = {
    "PUTA", "PUTO", "MIERDA", "COÑO", "POLLA", "CULO", "PEDO", "CACA", "PIS", "TETA",
    "PENE", "COJON", "JODER", "JODE", "MEAR", "CAGAR", "CAGO", "NAZI", "MARICON",
    "ZORRA", "GUARRA", "PICHA", "CHOCHO", "FOLLAR", "FOLLA", "MAMON", "CABRON",
    "SEXO", "MUERTE", "MATAR",
}


class PuzzleError(Exception):
    pass


def normalize(word: str) -> str:
    """Uppercase, strip accents, keep Ñ. Raises if anything but letters remains."""
    upper = word.strip().upper().replace("Ñ", "\0")
    stripped = "".join(c for c in unicodedata.normalize("NFD", upper)
                       if unicodedata.category(c) != "Mn")
    result = stripped.replace("\0", "Ñ")
    if not result or any(c not in ALPHABET for c in result):
        raise PuzzleError(f"word must be a single word of letters only: {word!r}")
    return result


@dataclass(frozen=True)
class Placement:
    word: str
    row: int
    col: int
    direction: str

    def cells(self) -> list[tuple[int, int]]:
        dr, dc = DIRECTIONS[self.direction]
        return [(self.row + i * dr, self.col + i * dc) for i in range(len(self.word))]


@dataclass
class Puzzle:
    size: int
    grid: list[list[str]]
    placements: list[Placement] = field(default_factory=list)

    @property
    def words(self) -> list[str]:
        return [p.word for p in self.placements]

    def rows(self) -> list[str]:
        return ["".join(r) for r in self.grid]


def find_all(grid: list[list[str]], word: str) -> list[tuple[int, int, tuple[int, int]]]:
    """Every occurrence of `word` in any of the 8 directions: (row, col, step)."""
    size = len(grid)
    hits = []
    n = len(word)
    for r in range(size):
        for c in range(size):
            if grid[r][c] != word[0]:
                continue
            for dr, dc in ALL_STEPS:
                end_r, end_c = r + (n - 1) * dr, c + (n - 1) * dc
                if not (0 <= end_r < size and 0 <= end_c < size):
                    continue
                if all(grid[r + i * dr][c + i * dc] == word[i] for i in range(n)):
                    hits.append((r, c, (dr, dc)))
    return hits


def verify(puzzle: Puzzle, blocklist: set[str] = BLOCKLIST) -> list[str]:
    """Return a list of problems; empty means the puzzle and its solution are correct."""
    problems = []
    size = puzzle.size
    if len(puzzle.grid) != size or any(len(row) != size for row in puzzle.grid):
        problems.append("grid is not square")
        return problems
    for row in puzzle.grid:
        for ch in row:
            if ch not in ALPHABET:
                problems.append(f"invalid character {ch!r} in grid")
    for p in puzzle.placements:
        cells = p.cells()
        if not all(0 <= r < size and 0 <= c < size for r, c in cells):
            problems.append(f"{p.word}: solution runs off the grid")
            continue
        spelled = "".join(puzzle.grid[r][c] for r, c in cells)
        if spelled != p.word:
            problems.append(f"{p.word}: solution cells spell {spelled}")
        hits = find_all(puzzle.grid, p.word)
        if len(hits) != 1:
            problems.append(f"{p.word}: found {len(hits)} times in grid (expected 1)")
    # A blocklisted string that is part of a real word (PIS in PISTO) is fine.
    words = puzzle.words
    for bad in blocklist:
        if any(bad in w or bad[::-1] in w for w in words):
            continue
        if find_all(puzzle.grid, bad):
            problems.append(f"blocklisted word {bad} appears in grid")
    return problems


def _can_place(grid, word, r, c, dr, dc) -> int | None:
    """Return number of overlapping letters if the word fits here, else None."""
    size = len(grid)
    end_r, end_c = r + (len(word) - 1) * dr, c + (len(word) - 1) * dc
    if not (0 <= end_r < size and 0 <= end_c < size):
        return None
    overlap = 0
    for i, ch in enumerate(word):
        cell = grid[r + i * dr][c + i * dc]
        if cell is None:
            continue
        if cell != ch:
            return None
        overlap += 1
    if overlap == len(word):
        return None
    return overlap


def _place_all(words: list[str], size: int, rng: random.Random,
               direction_weights: dict[str, float]
               ) -> tuple[list[list[str | None]], list[Placement]] | None:
    grid: list[list[str | None]] = [[None] * size for _ in range(size)]
    placements = []
    for word in sorted(words, key=len, reverse=True):
        # Pick the direction first (weighted), then fall back to the others.
        names = list(direction_weights)
        first = rng.choices(names, [direction_weights[n] for n in names])[0]
        order = [first] + rng.sample([n for n in names if n != first], len(names) - 1)
        chosen = None
        for name in order:
            dr, dc = DIRECTIONS[name]
            candidates = []
            for r in range(size):
                for c in range(size):
                    overlap = _can_place(grid, word, r, c, dr, dc)
                    if overlap is not None:
                        candidates.append((overlap, r, c))
            if candidates:
                # Sometimes prefer a crossing: keeps the grid compact.
                crossing = [x for x in candidates if x[0] > 0]
                pool = crossing if crossing and rng.random() < 0.4 else candidates
                _, r, c = rng.choice(pool)
                chosen = (name, r, c)
                break
        if chosen is None:
            return None
        name, r, c = chosen
        dr, dc = DIRECTIONS[name]
        for i, ch in enumerate(word):
            grid[r + i * dr][c + i * dc] = ch
        placements.append(Placement(word, r, c, name))
    return grid, placements


def _fill(grid: list[list[str | None]], rng: random.Random) -> list[list[str]]:
    letters = list(FILLER_WEIGHTS)
    weights = list(FILLER_WEIGHTS.values())
    return [[cell if cell is not None else rng.choices(letters, weights)[0] for cell in row]
            for row in grid]


def generate(words: list[str], size: int = 15, seed: int | str = 0,
             max_attempts: int = 400) -> Puzzle:
    """Build a verified puzzle. Deterministic for a given seed."""
    normalized = [normalize(w) for w in words]
    if len(set(normalized)) != len(normalized):
        raise PuzzleError("duplicate words after normalization")
    for w in normalized:
        if len(w) > size:
            raise PuzzleError(f"{w} is longer than the grid ({size})")
        if len(w) < 3:
            raise PuzzleError(f"{w} is too short (min 3 letters)")
        if w == w[::-1]:
            raise PuzzleError(f"{w} is a palindrome and would appear twice")
    for a in normalized:
        for b in normalized:
            if a != b and (a in b or a[::-1] in b):
                raise PuzzleError(f"{a} is contained in {b}; it would appear twice")

    rng = random.Random(f"wordsearch:{seed}")
    for _ in range(max_attempts):
        placed = _place_all(normalized, size, rng, DIRECTION_WEIGHTS)
        if placed is None:
            continue
        skeleton, placements = placed
        for _ in range(20):
            puzzle = Puzzle(size, _fill(skeleton, rng), placements)
            if not verify(puzzle):
                # Keep the word list in the original (input) order for display.
                order = {w: i for i, w in enumerate(normalized)}
                puzzle.placements.sort(key=lambda p: order[p.word])
                return puzzle
    raise PuzzleError(f"could not build a valid {size}x{size} grid for {len(words)} words")
