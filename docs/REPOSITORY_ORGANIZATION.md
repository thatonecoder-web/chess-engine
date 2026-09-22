# Repository Organization

## Root Directory
```
chess-engine/
├── README.md
├── docs/
│   ├── PERFT_VALIDATION.md
│   ├── CHANGELOG.md
│   ├── REPOSITORY_ORGANIZATION.md   # this file
│   └── releases/
│       ├── RELEASE_v0.2.5.md        # the from-scratch AI (v0.2.0-v0.2.5)
│       └── RELEASE_v0.3.1.md        # terminal experience & reorg (v0.2.6-v0.3.1)
├── pyproject.toml
├── LICENSE
├── .gitignore
├── run_perft_tests.py
├── run_ai_benchmarks.py
└── .github/
```

## Package Structure
```
chess_engine/
├── __init__.py                  # public API, unchanged since v0.1.9
├── main.py                      # entry point: python -m chess_engine.main
├── core/                        # pure chess rules and state
│   ├── board.py                 # board representation & FEN
│   ├── moves.py                 # Move class & notation
│   ├── pieces.py
│   ├── rules.py                 # movement validation
│   ├── check.py                 # check/checkmate/legal moves
│   ├── game.py                  # history & PGN (v0.1.9)
│   └── perft.py                 # perft framework (v0.1.9)
├── ai/                          # the chess engine (v0.2.0-v0.2.5; was AI/ before v0.3.1)
│   ├── evaluation.py
│   ├── search.py                # alpha-beta, quiescence, iterative deepening
│   ├── move_ordering.py
│   ├── difficulty.py            # adaptive skill tracking
│   ├── difficulty_levels.py     # named presets for menus (v0.2.7)
│   ├── ai_player.py
│   └── benchmarks.py
└── cli/                         # the terminal app (v0.2.6-v0.3.0)
    ├── menu.py
    ├── play.py                  # game loop for all three modes
    ├── commands.py
    ├── guide.py                 # 17-topic Guide Book
    ├── tutorial.py
    ├── settings.py
    └── ui.py
```

## Tests
```
tests/
├── core/   # 60 tests - moves, board, rules, check, game
├── ai/     # 58 tests - evaluation, search, move ordering, difficulty, tactics
└── cli/    # 22 tests - ui, menu, play loop, guide, tutorial

140 tests total, all passing.
```

## Where things stand

| Milestone | Status | What it added |
|-----------|--------|---------|
| v0.1.0-v0.1.9 | done | core rules, move generation, PGN, persistence, perft |
| v0.2.0-v0.2.5 | done | the AI: evaluation, alpha-beta search, move ordering, adaptive difficulty |
| v0.2.6-v0.3.0 | done | the terminal app: menu, three game modes, Guide Book, tutorial, settings |
| v0.3.1 | done | reorganized into core/ai/cli, no functional changes |

## Perft results

| Position | Depth 1 | Depth 2 | Depth 3 | Depth 4 |
|----------|---------|---------|---------|---------|
| Starting | 20 | 400 | 5,902 | 119,060 |
| Kiwipete | 48 | 2,039 | 97,862 | 4,085,603 |
| Position 3 | 14 | 191 | 2,812 | 43,238 |
| Position 4 | 6 | 264 | 9,467 | 422,333 |
| Position 5 | 29 | 953 | 27,990 | 871,198 |

Full methodology in `docs/PERFT_VALIDATION.md`.

## What's left

- Bitboards (the board representation is a plain 8x8 grid, deep-copied on every search node - fine for now, but the ceiling on search speed)
- Transposition table
- Full SAN, alongside the current square-pair notation
- UCI protocol
- Opening book
- Endgame tablebases

Quiescence search and iterative deepening were originally slated for
this list too, but both landed back in v0.2.5.

---
Last updated September 17, 2026.
