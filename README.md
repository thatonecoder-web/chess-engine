# Chess Engine

An open-source Python chess engine focused on learning, experimentation, and building chess AI from the ground up.

## Status

🚀 **v0.2.5** - Chess AI (from scratch)

Core chess rules are fully implemented and validated through comprehensive perft testing. v0.2.0 adds the engine's first AI opponent, built from scratch with selectable difficulty levels from 0 to max.

## Features

### Core Chess Engine
- ✅ Complete board representation with FEN support
- ✅ All piece movement rules (pawns, knights, bishops, rooks, queens, kings)
- ✅ Advanced rules: castling, en passant, pawn promotion
- ✅ Check, checkmate, and stalemate detection
- ✅ Legal move generation with full validation
- ✅ Algebraic and FEN notation support

### Game Management (v0.1.9)
- ✅ **Move History:** Track moves with move numbers and game state
- ✅ **PGN Support:** Parse and generate Portable Game Notation
- ✅ **Undo/Redo:** Full game replay and position restoration
- ✅ **Game Persistence:** Save/load games in JSON format
- ✅ **Metadata:** Store player names, event details, dates, results

### Validation & Testing
- ✅ **Perft Testing:** Recursive move generation validation against known positions
- ✅ **Multiple Test Positions:** Starting position, Kiwipete, en passant, castling, promotion
- ✅ **Comprehensive Test Suite:** 50+ unit tests covering all rule variations
- ✅ **Move Generation:** Fully validated through perft up to depth 4

### Chess AI (v0.2.0 — In Progress)
- 🚧 **Evaluation Function:** Material count + piece-square tables
- 🚧 **Search:** Minimax with alpha-beta pruning
- 🚧 **Move Ordering:** Captures/checks searched first for search efficiency
- 🚧 **Difficulty Levels:** Selectable strength from 0 to max (depth scaling, move randomness, blunder injection)
- 🚧 **AIPlayer Interface:** Clean integration with the existing game loop

## Quick Start

### Installation
```bash
git clone https://github.com/thatonecoder-web/chess-engine.git
cd chess-engine
pip install -e ".[dev]"
```

### Basic Usage

#### Playing a Game
```python
from chess_engine import Game, Move

game = Game()
game.set_metadata("White", "Player 1")
game.set_metadata("Black", "Player 2")

# Make moves
game.make_move(Move("e2", "e4"))
game.make_move(Move("c7", "c5"))
game.make_move(Move("g1", "f3"))

# Display board
game.board.display()

# Undo/redo
game.undo()
game.redo()
```

#### Loading a Position
```python
from chess_engine import Board

board = Board()
# Start from a FEN position
board.from_fen("r3k2r/p1ppqpb1/bn2pnp1/3PN3/1p2P3/2N2Q1p/PPPBBPPP/R3K2R w KQkq - 0 1")
board.display()
```

#### PGN Support
```python
from chess_engine import Game

# Generate PGN
game = Game()
game.set_metadata("White", "Alice")
game.set_metadata("Black", "Bob")
# ... make moves ...
pgn = game.to_pgn()
print(pgn)

# Parse PGN
pgn_text = """[White "Alice"]
[Black "Bob"]

1. e2e4 c7c5
2. g1f3 d7d6
"""
game2 = Game()
game2.from_pgn(pgn_text)
```

#### Game Persistence
```python
# Save game
game.save_to_file("my_game.json")

# Load game
game2 = Game()
game2.load_from_file("my_game.json")
```

#### Move Generation Validation
```python
from chess_engine import Board, perft, perft_divide

board = Board()

# Count positions at depth 4
count = perft(board, 4)  # Returns 119,060 for starting position
print(f"Perft(4): {count:,}")

# Breakdown by first move
divide = perft_divide(board, 2)
for move, count in divide.items():
    print(f"{move}: {count}")
```

#### Playing Against the AI (v0.2.0)
```python
from chess_engine import Game, Move
from chess_engine.ai import AIPlayer

game = Game()
ai = AIPlayer(level=5)  # 0 = weakest, "max" = strongest

game.make_move(Move("e2", "e4"))
ai_move = ai.get_move(game.board)
game.make_move(ai_move)
```

## Testing

### Run All Tests
```bash
pytest tests/ -v
```

### Run Perft Tests Only
```bash
pytest tests/test_perft.py -v
```

### Run AI Tests Only
```bash
pytest tests/ai/ -v
```

### Run Interactive Perft Validation
```bash
python run_perft_tests.py
```

## Project Structure

```
chess-engine/
├── chess_engine/
│   ├── __init__.py           # Package exports
│   ├── board.py              # Board representation & FEN
│   ├── moves.py              # Move class & notation
│   ├── pieces.py             # Piece definitions
│   ├── rules.py              # Movement validation
│   ├── check.py              # Check/checkmate/legal moves
│   ├── game.py               # Game history & PGN support (v0.1.9)
│   ├── perft.py              # Perft testing framework (v0.1.9)
│   └── ai/                   # Chess AI, from scratch (NEW v0.2.0)
│       ├── __init__.py
│       ├── evaluation.py     # Material count + piece-square tables
│       ├── search.py         # Minimax with alpha-beta pruning
│       ├── move_ordering.py  # Captures/checks-first ordering
│       ├── difficulty.py     # Level 0-max config
│       └── ai_player.py      # AIPlayer interface
├── tests/
│   ├── test_moves.py         # Move parsing tests
│   ├── test_board.py         # Board & FEN tests
│   ├── test_rules.py         # Piece movement tests
│   ├── test_check.py         # Check & legal move tests
│   ├── test_game.py          # Game & PGN tests (v0.1.9)
│   ├── test_perft.py         # Perft validation tests (v0.1.9)
│   └── ai/                   # AI tests (NEW v0.2.0)
│       ├── test_evaluation.py
│       ├── test_search.py
│       ├── test_move_ordering.py
│       ├── test_difficulty.py
│       └── test_ai_player.py
├── run_perft_tests.py        # Interactive perft runner
├── PERFT_VALIDATION.md       # Perft test documentation
├── README.md                 # This file
├── changelog                 # Version history
├── pyproject.toml            # Project configuration
└── LICENSE                   # MIT License
```

## Architecture

### Move Generation Pipeline
1. **Board State:** Maintain current position, castling rights, en passant target
2. **Legal Moves:** Generate all legal moves for a color using `generate_legal_moves()`
3. **Validation:** Verify moves don't leave own king in check
4. **Special Handling:** Castling, en passant, and promotion through board methods

### Perft Testing
Perft (Performance Test) validates move generation by:
- Recursively counting leaf nodes at a given depth
- Comparing against known correct values
- Testing starting position, Kiwipete, and tactical positions
- Verifying all chess rules including special moves

**Validated Positions:**
| Position | Depth 1 | Depth 2 | Depth 3 | Depth 4 |
|----------|---------|---------|---------|---------|
| Starting | 20 ✓ | 400 ✓ | 5,902 ✓ | 119,060 ✓ |
| Kiwipete | 48 ✓ | 2,039 ✓ | 97,862 | 4,085,603 |
| Position 3 | 14 ✓ | 191 ✓ | 2,812 | 43,238 |
| Position 4 | 6 ✓ | 264 ✓ | 9,467 | 422,333 |
| Position 5 | 29 ✓ | 953 ✓ | 27,990 | 871,198 |

See [PERFT_VALIDATION.md](PERFT_VALIDATION.md) for detailed perft test documentation.

### Chess AI (v0.2.0)
The AI is built from scratch on top of the existing move generator:
- **Evaluation:** Scores a position using material count and piece-square tables
- **Search:** Minimax with alpha-beta pruning explores the game tree, aided by move ordering (captures/checks first) for efficiency
- **Difficulty:** A single `difficulty.py` config table drives depth, move-randomness-among-top-N, and blunder probability per level, so tuning strength doesn't require touching the search code
- **Integration:** `AIPlayer.get_move(board)` is the only interface `game.py` needs — internals (including a future bitboard rewrite in v0.3.0) can change without affecting how the game loop calls the AI

## Changelog

### v0.2.0 — Chess AI (from scratch)
- 🚧 Evaluation function: material count + piece-square tables
- 🚧 Minimax search with alpha-beta pruning
- 🚧 Move ordering (captures/checks first) for search efficiency
- 🚧 Selectable difficulty levels, 0 to max
- 🚧 `AIPlayer` interface for integration with the existing game loop

### v0.1.9 — Game Records & Engine Validation
- ✅ Move history tracking with move numbers and game state information
- ✅ PGN (Portable Game Notation) parsing and generation
- ✅ PGN game metadata support (players, event, site, date, result)
- ✅ Complete game replay from PGN move sequences
- ✅ Recursive Perft testing for validating legal move generation
- ✅ Standard starting-position Perft test cases
- ✅ Tactical and special-rule Perft positions (castling, en passant, promotion, checks, pins)
- ✅ Move-generation regression tests based on Perft results
- ✅ JSON-based save files for preserving resumable game state
- ✅ Undo and redo functionality using recorded game state
- ✅ Expanded test coverage for PGN parsing, game replay, Perft validation, move history, and persistence

### Previous Versions
See [changelog](changelog) for complete version history.

## Goals

- Learn how chess engines work
- Build chess AI from scratch
- Experiment with different approaches
- Keep the project open-source and easy to contribute to

## Next Steps (Future Versions)

- [ ] **Bitboard Representation:** Board representation optimization for search speed (v0.3.0)
- [ ] **Transposition Tables:** Avoid re-searching repeated positions (v0.3.0)
- [ ] **Quiescence Search:** Avoid the horizon effect on tactical sequences (v0.3.0)
- [ ] **Iterative Deepening:** Search under a time budget (v0.3.0)
- [ ] **Standard Notation:** Full SAN (Standard Algebraic Notation) support (v0.3.0)
- [ ] **UCI Protocol:** Standard chess GUI integration (v0.3.0)
- [ ] **Opening Book:** Standard chess openings (v0.4.0)
- [ ] **Endgame Tables:** Tablebases (v0.4.0)

## Contributing

This is an open-source educational project. Contributions welcome!

Areas for improvement:
- Performance optimizations (bitboards, transposition tables)
- Engine evaluation functions
- Search algorithms (minimax, alpha-beta, NegaMax)
- UCI/XBoard protocol support
- Comprehensive documentation
- Additional test positions

## License

See [LICENSE](LICENSE) for details.

---

**Status:** 🚀 Core chess rules fully validated; the from-scratch AI is in progress for v0.2.0.

For detailed perft test results and move generation validation, see [PERFT_VALIDATION.md](PERFT_VALIDATION.md).
