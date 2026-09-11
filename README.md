# Chess Engine

An open-source Python chess engine focused on learning, experimentation, and building chess AI from the ground up.

## Status

🚀 **v0.1.9** - Game Records & Engine Validation

Early development with core chess rules fully implemented and validated through comprehensive perft testing.

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

## Testing

### Run All Tests
```bash
pytest tests/ -v
```

### Run Perft Tests Only
```bash
pytest tests/test_perft.py -v
```

### Run Interactive Perft Validation
```bash
python run_perft_tests.py
```

## Project Structure

```
chess-engine/
├── chess_engine/
│   ├── __init__.py           # Package exports (v0.1.9)
│   ├── board.py              # Board representation & FEN
│   ├── moves.py              # Move class & notation
│   ├── pieces.py             # Piece definitions
│   ├── rules.py              # Movement validation
│   ├── check.py              # Check/checkmate/legal moves
│   ├── game.py               # Game history & PGN support (NEW v0.1.9)
│   └── perft.py              # Perft testing framework (NEW v0.1.9)
├── tests/
│   ├── test_moves.py         # Move parsing tests
│   ├── test_board.py         # Board & FEN tests
│   ├── test_rules.py         # Piece movement tests
│   ├── test_check.py         # Check & legal move tests
│   ├── test_game.py          # Game & PGN tests (NEW v0.1.9)
│   └── test_perft.py         # Perft validation tests (NEW v0.1.9)
├── run_perft_tests.py        # Interactive perft runner (NEW v0.1.9)
├── PERFT_VALIDATION.md       # Perft test documentation (NEW v0.1.9)
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

## Changelog

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

- [ ] **Position Evaluation:** Basic material + position scoring
- [ ] **Search Algorithm:** Minimax with alpha-beta pruning
- [ ] **Standard Notation:** Full SAN (Standard Algebraic Notation) support
- [ ] **Opening Book:** Standard chess openings
- [ ] **Endgame Tables:** 7-piece tablebases
- [ ] **UCI Protocol:** Standard chess GUI integration
- [ ] **Performance:** Bitboard representation and optimizations

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

**Status:** 🚀 Ready for learning and experimentation with core chess rules fully validated.

For detailed perft test results and move generation validation, see [PERFT_VALIDATION.md](PERFT_VALIDATION.md).
