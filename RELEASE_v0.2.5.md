# v0.2.5 Release Summary

## Overview

v0.2.0 shipped the AI module's scaffolding, written against an assumed
Board/Move/Piece interface. v0.2.5 is where that AI actually gets
wired up against the real engine, and brought up to a complete,
from-scratch chess AI: full evaluation, alpha-beta search with
quiescence and iterative deepening, advanced move ordering, and a
time-managed, adaptive-difficulty `AIPlayer` integrated into the game
loop.

**Release Date:** TBD

---

## What's New in v0.2.5

### 1. Evaluation (`AI/evaluation.py`)
- Material + piece-square tables (carried over from v0.2.0, fixed to
  use real, case-sensitive piece symbols instead of the assumed
  uppercase-only ones)
- **Pawn structure:** doubled, isolated, and passed pawns (passed-pawn
  bonus scales with how far advanced the pawn is)
- **King safety:** pawn-shield bonus in front of the king, penalty for
  a king stuck on a completely open file
- **Center control:** bonus for occupying or attacking d4/d5/e4/e5
- **Development:** penalty for minor pieces still on their home square,
  tapered out once enough material has been traded (i.e. no longer
  "the opening")

### 2. Search (`AI/search.py`)
- **Quiescence search:** extends search through captures/promotions at
  leaf nodes so the engine doesn't misjudge a position mid-exchange
- **Iterative deepening:** searches depth 1, 2, 3, ... — each pass
  reuses the last pass's best move as an ordering hint, and killer
  moves / history heuristics persist across passes
- **Time management:** a time-limited search always returns the best
  move from the last *fully completed* depth if it runs out of time
  mid-iteration, rather than returning a partially-searched (and
  therefore untrustworthy) result
- **SearchStats:** nodes, quiescence nodes, depth reached, score, wall
  time, and nodes/second for every search call
- **Deterministic:** the same position searched to the same depth
  always returns the same move (no reliance on dict/set ordering or
  unseeded randomness anywhere in the search path itself)

### 3. Move Ordering (`AI/move_ordering.py`)
- Captures ranked by MVV-LVA (including en passant, which needed its
  own lookup since the captured pawn isn't on the destination square)
- Promotions
- A cheap (non-simulating) "gives check" heuristic
- Killer moves (per-ply, persists across an iterative-deepening search)
- History heuristic (persists across an iterative-deepening search,
  weighted by the depth of the cutoff it caused)
- An optional "hint" move (from the previous iterative-deepening pass)
  tried first, ahead of everything else

### 4. AIPlayer & Difficulty (`AI/ai_player.py`, `AI/difficulty.py`)
- `DifficultyController.get_time_limit()`: skill-scaled per-move time
  budget, used by `AIPlayer` via `iterative_deepening_search`
- `AIPlayer` now runs full iterative deepening (with time management)
  at the top of a difficulty level, and falls back to the existing
  candidate-pool + noise sampling at lower skill levels
- Fixed `estimate_move_quality`'s `board.active_color` reference (the
  real attribute is `board.turn`)

### 5. Game Loop Integration (`main.py`)
- Terminal game loop now offers Human vs Human or Human vs AI, with a
  color choice for the human side
- AI moves print their search depth/node count; human moves feed
  `AIPlayer.observe_player_move()` so adaptive difficulty keeps working

### 6. Board API additions (`board.py`)
The AI package only ever talks to a Board through these — it never
touches the underlying grid or coordinate math directly:
- `Board.copy()` — an independent copy (pieces cloned, not shared) for
  search to explore hypothetical lines without mutating the real
  game's piece `has_moved` flags
- `Board.get_legal_moves(color=None)`
- `Board.is_in_check(color=None)` / `is_checkmate(color=None)` /
  `is_stalemate(color=None)`
- `Board.is_game_over()`

### 7. Bug fix: `Move` equality (`moves.py`)
`Move` had no `__eq__`/`__hash__`, so two `Move` objects describing the
same square-pair move (e.g. one parsed from user input, one returned
by move generation) never compared equal. This silently broke
move-quality tracking (`estimate_move_quality`) and would have broken
killer-move/history-table lookups too. Added value-based `__eq__` and
`__hash__` on `(start, end, promotion)`.

### 8. Tests
- `tests/ai-tests/test_evaluation.py` — material, symmetry, checkmate/
  stalemate scoring, PST, pawn structure, king safety
- `tests/ai-tests/test_move_ordering.py` — capture ordering, MVV-LVA,
  en passant detection, promotions, hint moves, killer/history
  heuristics, determinism
- `tests/ai-tests/test_search.py` — legal-move sanity, mate-in-1 (both
  colors), quiescence avoiding the horizon effect, iterative deepening
  (time limit, early stop on forced mate, determinism), `get_top_n_moves`
- `tests/ai-tests/test_difficulty.py` — `PlayerModel` and
  `DifficultyController` scaling
- `tests/ai-tests/test_ai_player.py` — legal moves for both colors, a
  regression test for the perspective bug below, move-quality
  estimation, `weighted_pick`
- `tests/ai-tests/test_tactics.py` — five known tactical motifs (mate
  finishes, back-rank mate, a knight fork, an undefended-piece win)
  the search is expected to find every time

### 9. Benchmarks
- `chess_engine/AI/benchmarks.py` + `run_ai_benchmarks.py` (mirrors
  `run_perft_tests.py`'s pattern) — timed iterative-deepening runs on
  an opening, middlegame, tactical, and sparse-endgame position

---

## Bug Fixed During Development: Search Perspective

An early version of this release threaded a `perspective` argument
tied to the AI's own color through `iterative_deepening_search` and
`get_top_n_moves`. That's inconsistent with how `maximizing`/
`minimizing` already work in this codebase: they alternate based on
whose turn it actually is, against one *fixed* white-relative score.
Also varying `perspective` by the AI's color double-flipped the sign
for a Black-playing AI — caught because it made the AI refuse an
available mate-in-1. Fixed by keeping `perspective="white"` fixed
everywhere in the search path; `maximizing`/`minimizing` alone is what
makes the search correct for whichever side is actually moving. A
regression test (`test_black_ai_takes_an_available_mate`) covers this.

---

## Known Limitations

1. **No bitboards yet** — `Board.copy()` deep-copies the piece grid at
   every search node rather than mutating in place with undo, since
   the existing `Board` has no incremental undo. This is correct but
   not fast; representation optimization is still planned for v0.3.0.
2. **No transposition table** — repeated positions (transpositions)
   are re-searched from scratch.
3. **"Gives check" move-ordering is a heuristic** — it checks whether
   the moved piece directly attacks the enemy king from its
   destination square, using the board as it stood before the move.
   It does not detect discovered checks. This only affects move
   ordering (search speed), never correctness — actual check/checkmate
   detection (`check.py`) is unaffected and exact.
4. **No opening book or endgame tablebase.**

---

## Breaking Changes

None for existing Board/Move/Game/check/rules callers. `AI/__init__.py`
exports have grown (new names added), and `AIPlayer.choose_move()`'s
top-difficulty behavior now takes measurably longer per move (it's
actually searching, bounded by `DifficultyController.get_time_limit()`,
rather than returning near-instantly).
