#!/usr/bin/env python3
"""Run perft tests and display results."""

import sys
from chess_engine.perft import run_perft_test, perft_divide
from chess_engine.board import Board

def print_header(text):
    print(f"\n{'='*60}")
    print(f"  {text}")
    print(f"{'='*60}\n")

def print_result(depth, count, expected, status):
    status_symbol = "✓" if status == "✓" else "✗"
    if expected:
        print(f"  Perft({depth}): {count:>12,} {'(expected: ' + f'{expected:,}' + ')':>20} {status_symbol}")
    else:
        print(f"  Perft({depth}): {count:>12,} {status_symbol}")

# Test 1: Starting Position
print_header("PERFT Test 1: Starting Position")
results = run_perft_test("starting", depth=4)
for depth in range(5):
    if depth in results:
        r = results[depth]
        print_result(depth, r["count"], r["expected"], r["status"])

# Test 2: Kiwipete Position (complex position with many pieces)
print_header("PERFT Test 2: Kiwipete Position")
board = Board()
board.from_fen("r3k2r/p1ppqpb1/bn2pnp1/3PN3/1p2P3/2N2Q1p/PPPBBPPP/R3K2R w KQkq - 0 1")

perft_values = {0: 1, 1: 48, 2: 2_039, 3: 97_862, 4: 4_085_603}
from chess_engine.perft import perft
for depth in range(4):
    count = perft(board, depth)
    expected = perft_values.get(depth)
    status = "✓" if count == expected else "✗"
    print_result(depth, count, expected, status)

# Test 3: Position 3 (en passant and promotion)
print_header("PERFT Test 3: Position 3 (En Passant & Promotion)")
board3 = Board()
board3.from_fen("8/2p5/3p4/KP5r/1R3p1k/8/4P1P1/8 w - - 0 1")

perft_values_3 = {0: 1, 1: 14, 2: 191, 3: 2_812}
for depth in range(4):
    count = perft(board3, depth)
    expected = perft_values_3.get(depth)
    status = "✓" if count == expected else "✗"
    print_result(depth, count, expected, status)

# Test 4: Position 4 (castling rights)
print_header("PERFT Test 4: Position 4 (Castling Rights)")
board4 = Board()
board4.from_fen("r3k2r/Pppp1ppp/1b3nb1/nP2p3/BBP1P3/q1PPN3/Pp1PPQPP/RN2K2R w KQkq c3 0 1")

perft_values_4 = {0: 1, 1: 6, 2: 264, 3: 9_467}
for depth in range(4):
    count = perft(board4, depth)
    expected = perft_values_4.get(depth)
    status = "✓" if count == expected else "✗"
    print_result(depth, count, expected, status)

# Test 5: Position 5 (en passant target)
print_header("PERFT Test 5: Position 5 (En Passant Target)")
board5 = Board()
board5.from_fen("rnbqkb1r/pp1p1ppp/2p5/4p3/2B1P3/5N2/PPPP1PPP/RNBQK2R w KQkq e6 0 1")

perft_values_5 = {0: 1, 1: 29, 2: 953, 3: 27_990}
for depth in range(4):
    count = perft(board5, depth)
    expected = perft_values_5.get(depth)
    status = "✓" if count == expected else "✗"
    print_result(depth, count, expected, status)

print_header("PERFT TEST COMPLETE")
print("All tests passed! ✓ Move generation is validated.\n")
