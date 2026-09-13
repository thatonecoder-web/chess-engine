# v0.2.0 Release Summary

## Overview

Chess Engine v0.2.0 introduces the engine's first AI: a from-scratch chess AI with selectable difficulty levels from 0 to max, built entirely on top of the existing move generation and rules engine.

**Release Date:** TBD  
**Status:** 🚧 Planned / In Progress

---

## What's New in v0.2.0

### 1. Evaluation Function
- **Material Counting:** Standard piece values as the baseline score
- **Piece-Square Tables:** Positional bonuses/penalties per piece type and square
- Foundation designed to be extended later (mobility, king safety, pawn structure)

### 2. Search Algorithm
- **Minimax:** Core game-tree search from scratch
- **Alpha-Beta Pruning:** Cuts down the search tree for faster, deeper search
- **Move Ordering:** Captures and checks searched first to improve alpha-beta efficiency

### 3. Difficulty Levels (0 to Max)
- **Depth Scaling:** Higher levels search deeper
- **Move Randomness:** Lower levels pick randomly among the top-N evaluated moves rather than always the best, to avoid robotic/exploitable play
- **Blunder Injection:** Lower levels occasionally play a deliberately weaker move
- Level configuration centralized in one place for easy tuning

### 4. AIPlayer Interface
- **Clean Boundary:** `game.py` calls `AIPlayer(level).get_move(board)` without needing to know how the search works internally
- Sets up v0.3.0's board-representation changes (e.g. bitboards) to happen without touching how the game loop talks to the AI

---

## Files Added/Modified

### New Files (v0.2.0)
```
chess_engine/
└── ai/                       # New subpackage
    ├── __init__.py
    ├── evaluation.py         # Material count + piece-square tables
    ├── search.py             # Minimax with alpha-beta pruning
    ├── move_ordering.py      # Captures/checks-first ordering
    ├── difficulty.py         # Level 0-max config table
    └── ai_player.py          # AIPlayer interface

tests/
└── ai/                       # New test subpackage
    ├── __init__.py
    ├── test_evaluation.py
    ├── test_search.py
    ├── test_move_ordering.py
    ├── test_difficulty.py
    └── test_ai_player.py
```

### Modified Files (v0.2.0)
```
├── __init__.py          # Updated version to 0.2.0, new AI exports
├── pyproject.toml       # Updated version to 0.2.0
├── changelog            # Added v0.2.0 entry
├── game.py              # Wired up to call AIPlayer for AI-controlled sides
└── README.md            # Updated with AI usage examples
```

---

## Code Quality (Planned)

### Modules to Add
```python
# evaluation.py
def evaluate(board) -> int
    # Material count + piece-square table lookup

# search.py
def minimax(board, depth, alpha, beta, maximizing) -> int
def find_best_move(board, depth) -> Move

# move_ordering.py
def order_moves(board, moves) -> list[Move]
    # Captures/checks first

# difficulty.py
DIFFICULTY_LEVELS = {
    0: {...},   # depth, randomness, blunder rate
    # ...
    "max": {...},
}

# ai_player.py
class AIPlayer:
    def __init__(self, level: int)
    def get_move(self, board) -> Move
```

### Documentation
- [ ] Docstrings on all public methods
- [ ] Type hints for clarity
- [ ] README section on AI usage and difficulty levels
- [ ] Updated changelog

---

## Release Checklist

- [ ] Evaluation function implemented and tested
- [ ] Minimax + alpha-beta search implemented and tested
- [ ] Move ordering implemented and tested
- [ ] Difficulty levels (0-max) implemented and tuned
- [ ] AIPlayer interface implemented
- [ ] game.py integration complete
- [ ] Test suite passing (evaluation, search, move ordering, difficulty, AIPlayer)
- [ ] Documentation complete (README AI section)
- [ ] Version bumped to 0.2.0
- [ ] Changelog updated
- [ ] Package exports updated
- [ ] pyproject.toml updated
- [ ] Backward compatibility confirmed (no breaking changes to existing modules)

---

## Performance Notes

- Board representation stays as-is for v0.2.0 (no bitboards yet) — v0.3.0 is where representation optimization for search speed is planned
- Search depth at max difficulty will be constrained by the current (unoptimized) move generator's speed until v0.3.0's representation upgrade lands

---

## Breaking Changes

None expected. This adds a new `ai/` subpackage and an optional AI-controlled player path through `game.py`; existing Board, Move, Game, and check/rules APIs are unaffected.

---

## Known Limitations (Expected at Release)

1. **No Bitboards Yet:** Search speed is limited by the current board representation; bitboard optimization is planned for v0.3.0.
2. **No Transposition Table:** Repeated positions are re-searched from scratch; planned for v0.3.0.
3. **No Quiescence Search:** Search may be subject to the horizon effect on tactical sequences at the search boundary; planned for v0.3.0.
4. **No Opening Book:** The AI calculates every move from scratch, even in the opening.

---

## Migration Guide

### For Existing Users
No changes needed for existing move generation, rules, or game-management code.

### New Features to Try (once implemented)
```python
from chess_engine.ai import AIPlayer

ai = AIPlayer(level=5)
move = ai.get_move(board)
```

---

## Future Roadmap

### v0.3.0 - Search & Representation Upgrades
- Board representation optimization (e.g. bitboards) for search speed
- Transposition tables
- Quiescence search
- Iterative deepening
- UCI protocol support
- Standard Algebraic Notation (SAN)

### v0.4.0 - Advanced Features
- Opening book (ECO codes)
- Endgame tables (3-4 pieces)

### v0.5.0 - GUI & Integration
- Chess GUI compatibility
- Stockfish comparison tests
- Blitz/rapid time controls
- Tournament mode

---

## Getting Help

### Documentation
- [README.md](README.md) - Quick start and feature overview
- [changelog](changelog) - Complete version history

### Running Tests (once implemented)
```bash
# All tests
pytest tests/ -v

# AI tests only
pytest tests/ai/ -v
```

---

## License

MIT License - See LICENSE file for details.

---

**v0.2.0 brings the engine its first opponent — an AI built entirely from scratch, tunable from beginner to strong play.**
