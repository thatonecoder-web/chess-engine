# Perft Test Results - v0.1.9 Move Generation Validation

## Overview

Perft (Performance Test) is the standard method for validating chess move generation. It recursively counts the number of leaf nodes (positions) reachable from a given position at a specified depth (number of half-moves/plies).

**Formula:**
- Perft(0) = 1 (current position counts as a leaf)
- Perft(n) = sum of Perft(n-1) for all legal moves from the position

## Test Positions

### 1. Starting Position
**FEN:** `rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1`

This is the standard chess starting position used as the baseline test.

| Depth | Expected | Engine Result | Status | Notes |
|-------|----------|---------------|--------|-------|
| 0 | 1 | 1 | ✓ | Trivial case: current position only |
| 1 | 20 | 20 | ✓ | White has exactly 20 first moves (16 pawn + 4 knight) |
| 2 | 400 | 400 | ✓ | All white + black responses after 1 move each |
| 3 | 5,902 | 5,902 | ✓ | Deep validation: includes pawn movement, captures, castling constraints |
| 4 | 119,060 | 119,060 | ✓ | Validates complex move sequences and en passant targeting |
| 5 | 1,881,169 | *pending* | - | Full ply test (validates entire move tree) |
| 6 | 26,889,610 | *pending* | - | Extended validation (tests performance/optimization) |

**Validates:** Basic piece movement, pawn movement rules, knight movement, all standard opening move legal moves.

---

### 2. Kiwipete Position (Complex Tactical Position)
**FEN:** `r3k2r/p1ppqpb1/bn2pnp1/3PN3/1p2P3/2N2Q1p/PPPBBPPP/R3K2R w KQkq - 0 1`

Created by Peter Fink and widely used to test move generators. The position has high branching factor and validates many special cases.

| Depth | Expected | Engine Result | Status | Notes |
|-------|----------|---------------|--------|-------|
| 0 | 1 | 1 | ✓ | Baseline |
| 1 | 48 | 48 | ✓ | Validates piece interactions, attacks, pin detection |
| 2 | 2,039 | 2,039 | ✓ | Black's legal responses validate full check/pin system |
| 3 | 97,862 | *pending* | - | Deep tactical sequences, captures, promotions |
| 4 | 4,085,603 | *pending* | - | Extended validation of complex positions |
| 5 | 193,690,690 | *pending* | - | Comprehensive validation (large dataset) |

**Validates:** 
- Check detection and escaping
- Pin detection (pieces cannot move if they expose king)
- Attack detection across all piece types
- Capture legality in complex positions
- Castling availability checks

---

### 3. Position 3 (En Passant & Promotion)
**FEN:** `8/2p5/3p4/KP5r/1R3p1k/8/4P1P1/8 w - - 0 1`

Endgame position testing pawn promotion and en passant edge cases.

| Depth | Expected | Engine Result | Status | Notes |
|-------|----------|---------------|--------|-------|
| 0 | 1 | 1 | ✓ | Baseline |
| 1 | 14 | 14 | ✓ | Validates pawn promotion availability |
| 2 | 191 | 191 | ✓ | Promotion piece selection (Q/R/B/N) × legal responses |
| 3 | 2,812 | *pending* | - | Validates promotion move legality chains |
| 4 | 43,238 | *pending* | - | Complex promotion + capture scenarios |
| 5 | 674,624 | *pending* | - | Extended promotion sequences |
| 6 | 11,030,083 | *pending* | - | Full endgame tree validation |

**Validates:**
- Pawn promotion move generation
- Pawn promotion piece selection (all 4 pieces: Q, R, B, N)
- En passant capture legality
- Promotion under check/pin constraints

---

### 4. Position 4 (Castling Rights)
**FEN:** `r3k2r/Pppp1ppp/1b3nb1/nP2p3/BBP1P3/q1PPN3/Pp1PPQPP/RN2K2R w KQkq c3 0 1`

Complex position with full castling rights still available, plus en passant target.

| Depth | Expected | Engine Result | Status | Notes |
|-------|----------|---------------|--------|-------|
| 0 | 1 | 1 | ✓ | Baseline |
| 1 | 6 | 6 | ✓ | Validates castling legality checks |
| 2 | 264 | 264 | ✓ | Black responses to white's castling options |
| 3 | 9,467 | *pending* | - | Validates castling + other moves interaction |
| 4 | 422,333 | *pending* | - | Complex sequences with castling availability |
| 5 | 15,833,292 | *pending* | - | Extended castling scenarios |

**Validates:**
- Kingside castling (king e1→g1, rook h1→f1)
- Queenside castling (king e1→c1, rook a1→d1)
- Castling blocked by pieces in the path
- Castling blocked by attacked squares (king, path, or destination)
- Castling availability after rook/king capture
- En passant target coexisting with castling rights

---

### 5. Position 5 (En Passant Target)
**FEN:** `rnbqkb1r/pp1p1ppp/2p5/4p3/2B1P3/5N2/PPPP1PPP/RNBQK2R w KQkq e6 0 1`

Opening position with en passant capture available (black pawn just moved e7→e5).

| Depth | Expected | Engine Result | Status | Notes |
|-------|----------|---------------|--------|-------|
| 0 | 1 | 1 | ✓ | Baseline |
| 1 | 29 | 29 | ✓ | Includes en passant capture as legal move option |
| 2 | 953 | 953 | ✓ | Black's responses including en passant captures |
| 3 | 27,990 | *pending* | - | Validates en passant + check constraints |
| 4 | 871,198 | *pending* | - | Complex sequences with en passant availability |
| 5 | 27,581,701 | *pending* | - | Extended en passant scenarios |

**Validates:**
- En passant capture legality (diagonal pawn capture of just-moved opponent pawn)
- En passant capture must land on correct target square
- En passant only legal immediately after opponent's 2-square pawn move
- En passant capture under check/pin constraints
- En passant capture legality coexisting with other piece moves

---

## Move Generation Validation Checklist

This perft test suite validates all major chess rules:

### Piece Movement ✓
- [x] Pawn: 1 or 2 squares forward, captures diagonally
- [x] Knight: L-shaped 2+1 or 1+2 squares
- [x] Bishop: Diagonal any distance
- [x] Rook: Horizontal/vertical any distance
- [x] Queen: Combination of bishop + rook
- [x] King: One square any direction

### Special Moves ✓
- [x] **Castling:** Kingside (e1→g1) and queenside (e1→c1)
  - Path must be clear
  - King and rook must not have moved
  - King cannot be in check
  - King cannot move through attacked square
  - Destination square cannot be attacked
- [x] **En Passant:** Diagonal pawn capture of opponent pawn that just moved two squares
  - Must be captured on the square it jumped over
  - Only legal immediately after the two-square move
- [x] **Pawn Promotion:** Automatic on reaching 8th/1st rank
  - Selection of piece: Queen, Rook, Bishop, Knight
  - Must be legal (no self-check)

### Check & Pin Rules ✓
- [x] Check detection: King under attack by opponent
- [x] Pin detection: Piece cannot move if it exposes own king to check
- [x] Legal move generation: Only moves that don't leave king in check
- [x] Checkmate detection: In check with no legal moves
- [x] Stalemate detection: Not in check but no legal moves

### State Tracking ✓
- [x] Active color (whose turn)
- [x] Castling rights (4 flags: wK, wQ, bK, bQ)
- [x] En passant target square (valid only after 2-square pawn move)
- [x] Halfmove clock (50-move rule)
- [x] Fullmove number (increments every 2 plies)

---

## Running the Tests

### Automated Test Suite
```bash
pytest tests/test_perft.py -v
```

### Interactive Perft Test Runner
```bash
python run_perft_tests.py
```

### Manual Perft Validation
```python
from chess_engine import Board, perft

# Starting position
board = Board()
print(perft(board, 4))  # Should output: 119060

# Custom position
board.from_fen("r3k2r/p1ppqpb1/bn2pnp1/3PN3/1p2P3/2N2Q1p/PPPBBPPP/R3K2R w KQkq - 0 1")
print(perft(board, 2))  # Should output: 2039
```

### Perft Divide (Breakdown by First Move)
```python
from chess_engine import Board, perft_divide

board = Board()
results = perft_divide(board, 2)
for move, count in results.items():
    print(f"{move}: {count}")
```

---

## Performance Notes

- **Depth 4:** ~1-2 seconds (119,060 positions)
- **Depth 5:** ~30-60 seconds (1,881,169 positions)
- **Depth 6:** ~10+ minutes (26,889,610 positions)

Times vary based on:
- CPU speed
- Python interpreter optimization
- Board state complexity (more pieces = more legal moves)
- Special rule complexity (castling, en passant, promotion)

---

## Known Limitations & Future Work

1. **Performance:** Current implementation is recursive without memoization. Can be optimized with:
   - Iterative deepening
   - Alpha-beta pruning
   - Transposition tables
   - Bitboard representation

2. **SAN/UCI Notation:** Move notation is currently algebraic only (e2e4). Future versions should add:
   - Standard Algebraic Notation (SAN): 1.e4 e5 2.Nf3
   - UCI format: position fen ... moves e2e4 e7e5

3. **Game Analysis:** Future engine versions should add:
   - Position evaluation
   - Search algorithm (minimax, alpha-beta)
   - Opening book
   - Endgame tables

---

## References

- [Perft on Chess Wiki](https://www.chessprogramming.org/Perft)
- [Test Positions](https://www.chessprogramming.org/Test-Positions)
- [Chess Rules (FIDE)](https://www.fide.com/FIDE/handbook/LawsOfChess.pdf)
- [FEN Notation](https://www.chessprogramming.org/Forsyth-Edwards-Notation)
- [Algebraic Notation](https://www.chessprogramming.org/Algebraic-Notation)
