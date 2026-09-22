# PLEASE DO NOT ATTEMPT TO PLAY
# GAME IS BROKEN RIGHT NOW, FIXES UNDERWAY

# Chess Engine

A Python chess engine built from scratch, mostly as a way to learn how chess engines actually work.

## Status

v0.3.1. Core rules and move generation are done and perft-validated. There's a from-scratch AI (v0.2.0-v0.2.5) with adjustable difficulty, and a terminal app (v0.2.6-v0.3.0) built around it - main menu, a Guide Book, an interactive tutorial, configurable display. v0.3.1 just reorganized the codebase into `core/`, `ai/`, and `cli/` since it had outgrown one flat folder.

## Features

### Core rules
Full board representation with FEN, all piece movement including castling/en passant/promotion, check/checkmate/stalemate detection, legal move generation, square-pair and FEN notation.

### Game management (v0.1.9)
Move history, PGN parsing and generation, undo/redo, JSON save/load, game metadata (players, event, date, result).

### Testing
140 tests across `tests/core/`, `tests/ai/`, `tests/cli/`. Move generation is validated against known perft values through depth 4 on several standard test positions - see `docs/PERFT_VALIDATION.md`.

### The AI (v0.2.0-v0.2.5)
Evaluation covers material, piece-square tables, pawn structure, king safety, center control, and development (`ai/evaluation.py`). Search is alpha-beta with quiescence search and iterative deepening under a time budget, ordered by MVV-LVA captures, killer moves, and a history heuristic. Difficulty is adaptive - it tracks how well you're playing and adjusts to match - with named presets (Beginner through Maximum) for menus. `AIPlayer.choose_move(board)` is the whole interface the game loop needs.

### The terminal app (v0.2.6-v0.3.0)
Main menu with Player vs Player, Player vs AI, and AI vs AI. Unicode board rendering with an ASCII fallback, coordinate labels, turn/check/checkmate status. AI vs AI runs on its own with live search stats, pause/stop, and automatic PGN recording. A built-in Guide Book and an interactive tutorial that uses the real board and move validation. Full command set: `p <from> <to> [promotion]`, `moves`, `history`, `undo`, `redo`, `fen`, `save`, `load`, `help`, `guide`, `quit`. Settings toggle Unicode/ASCII, redraw behavior, captured-piece display, and AI search stats.

## Quick Start

```bash
git clone https://github.com/thatonecoder-web/chess-engine.git
cd chess-engine
pip install -e ".[dev]"
```

Play in the terminal:
```bash
python -m chess_engine.main
```

## Library usage

```python
from chess_engine import Game, Move

game = Game()
game.set_metadata("White", "Player 1")
game.set_metadata("Black", "Player 2")

game.make_move(Move("e2", "e4"))
game.make_move(Move("c7", "c5"))
game.make_move(Move("g1", "f3"))

game.board.display()

game.undo()
game.redo()
```

Loading a FEN position:
```python
from chess_engine import Board

board = Board()
board.from_fen("r3k2r/p1ppqpb1/bn2pnp1/3PN3/1p2P3/2N2Q1p/PPPBBPPP/R3K2R w KQkq - 0 1")
board.display()
```

PGN:
```python
from chess_engine import Game

game = Game()
game.set_metadata("White", "Alice")
game.set_metadata("Black", "Bob")
# ... make moves ...
pgn = game.to_pgn()

pgn_text = """[White "Alice"]
[Black "Bob"]

1. e2e4 c7c5
2. g1f3 d7d6
"""
game2 = Game()
game2.from_pgn(pgn_text)
```

Save/load:
```python
game.save_to_file("my_game.json")

game2 = Game()
game2.load_from_file("my_game.json")
```

Perft:
```python
from chess_engine import Board, perft, perft_divide

board = Board()
count = perft(board, 4)  # 119,060 for the starting position
divide = perft_divide(board, 2)
for move, count in divide.items():
    print(f"{move}: {count}")
```

Playing against the AI:
```python
from chess_engine import Game, Move
from chess_engine.ai.difficulty_levels import make_ai_player

game = Game()
ai = make_ai_player("black", "Hard")  # Beginner, Easy, Medium, Hard, Expert, Maximum

game.make_move(Move("e2", "e4"))
ai_move = ai.choose_move(game.board)
game.make_move(ai_move)
ai.observe_player_move(game.board, Move("e2", "e4"))  # so it can adapt to you
```

## Testing

```bash
pytest tests/ -v            # everything
pytest tests/core/ -v       # rules only
pytest tests/ai/ -v         # AI only
pytest tests/cli/ -v        # terminal app only

python run_perft_tests.py       # interactive perft validation
python run_ai_benchmarks.py     # AI search benchmarks
```

## Project Structure

```
chess-engine/
├── chess_engine/
│   ├── __init__.py             # public API
│   ├── main.py                 # python -m chess_engine.main
│   ├── core/                   # pure chess: rules, state, no AI or UI
│   │   ├── board.py
│   │   ├── moves.py
│   │   ├── pieces.py
│   │   ├── rules.py
│   │   ├── check.py
│   │   ├── game.py             # history & PGN (v0.1.9)
│   │   └── perft.py            # (v0.1.9)
│   ├── ai/                     # the engine (v0.2.0-v0.2.5)
│   │   ├── evaluation.py
│   │   ├── search.py           # alpha-beta, quiescence, iterative deepening
│   │   ├── move_ordering.py
│   │   ├── difficulty.py       # adaptive skill tracking
│   │   ├── difficulty_levels.py
│   │   ├── ai_player.py
│   │   └── benchmarks.py
│   └── cli/                    # the terminal app (v0.2.6-v0.3.0)
│       ├── menu.py
│       ├── play.py             # game loop for all three modes
│       ├── commands.py
│       ├── guide.py
│       ├── tutorial.py
│       ├── settings.py
│       └── ui.py
├── tests/
│   ├── core/
│   ├── ai/
│   └── cli/
├── run_perft_tests.py
├── run_ai_benchmarks.py
├── docs/
│   ├── PERFT_VALIDATION.md
│   ├── CHANGELOG.md
│   ├── REPOSITORY_ORGANIZATION.md
│   └── releases/
│       ├── RELEASE_v0.2.5.md
│       └── RELEASE_v0.3.1.md
├── README.md
├── pyproject.toml
└── LICENSE
```

## Architecture

**Move generation:** the board tracks position, castling rights, and en passant target. `generate_legal_moves()` produces every legal move for a color, filtering out anything that leaves that side's own king in check. Castling, en passant, and promotion are handled as special cases on top of the base movement rules.

**Perft:** counts leaf positions at a given depth and checks the count against known-correct values for a handful of standard positions (starting position, Kiwipete, a few tactical/special-rules positions). Full writeup in `docs/PERFT_VALIDATION.md`.

| Position | Depth 1 | Depth 2 | Depth 3 | Depth 4 |
|----------|---------|---------|---------|---------|
| Starting | 20 | 400 | 5,902 | 119,060 |
| Kiwipete | 48 | 2,039 | 97,862 | 4,085,603 |
| Position 3 | 14 | 191 | 2,812 | 43,238 |
| Position 4 | 6 | 264 | 9,467 | 422,333 |
| Position 5 | 29 | 953 | 27,990 | 871,198 |

**The AI:** evaluation scores material, piece-square tables, pawn structure, king safety, center control, and development. Search is alpha-beta with quiescence search at the leaves and iterative deepening under a time budget, using move ordering (MVV-LVA, killer moves, history) to prune more aggressively. `difficulty.py`'s `PlayerModel` tracks a continuous skill estimate rather than a fixed level; `difficulty_levels.py` maps named presets onto that scale, either adapting further (Player vs AI) or pinned for the game (AI vs AI). The whole thing is reachable through `AIPlayer.choose_move(board)`, so internals can change without touching how it's called.

**The terminal app:** a thin layer over the same `Board`/`Game`/`AIPlayer` classes above. `cli.menu` drives the main menu, `cli.play` runs the game loop for all three modes (sharing captured-piece tracking, undo/redo, save/load, and commands regardless of who's moving), `cli.ui` renders the board, `cli.guide`/`cli.tutorial` hold their content, and `cli.settings.Settings` is one mutable object threaded through all of it.

## Documentation

- [docs/PERFT_VALIDATION.md](docs/PERFT_VALIDATION.md) - perft methodology and validated positions
- [docs/CHANGELOG.md](docs/CHANGELOG.md) - full version history
- [docs/REPOSITORY_ORGANIZATION.md](docs/REPOSITORY_ORGANIZATION.md) - current structure and status
- [docs/releases/RELEASE_v0.2.5.md](docs/releases/RELEASE_v0.2.5.md) - the from-scratch AI
- [docs/releases/RELEASE_v0.3.1.md](docs/releases/RELEASE_v0.3.1.md) - the terminal app and the reorg

## Goals

Learn how chess engines work, build the AI from scratch, experiment, keep it easy to contribute to.

## What's left

- Bitboards (search still deep-copies a plain 8x8 grid at every node)
- Transposition table
- Full SAN, alongside the current square-pair notation
- UCI protocol
- Opening book
- Endgame tablebases

## Contributing

Open to it - this is a learning project. Bitboards/transposition tables, evaluation tuning, search variants, UCI support, more test positions, and general documentation cleanup are all fair game.

## License

See [LICENSE](LICENSE).
