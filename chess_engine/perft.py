"""Perft (performance test) for validating move generation."""

from .check import generate_legal_moves
from .board import Board


def perft(board, depth):
    """Recursively count leaf nodes (positions) at the given depth.

    This is the standard perft test used to validate move generation in chess engines.
    Perft(0) returns 1 (the current position counts as a leaf).
    Perft(n) recursively counts all positions reachable in n plies (half-moves).
    """
    if depth == 0:
        return 1

    count = 0
    moves = generate_legal_moves(board, board.turn)

    for move in moves:
        # Make the move on a copy to avoid modifying the board
        board_copy = Board()
        board_copy.from_fen(board.to_fen())
        board_copy.make_move(move)

        count += perft(board_copy, depth - 1)

    return count


def perft_divide(board, depth):
    """Perft with breakdown by first move.

    Returns a dict mapping move notation to the count of positions
    reachable after each move.
    """
    if depth == 0:
        return {None: 1}

    results = {}
    moves = generate_legal_moves(board, board.turn)

    for move in moves:
        board_copy = Board()
        board_copy.from_fen(board.to_fen())
        board_copy.make_move(move)

        count = perft(board_copy, depth - 1)
        results[move.to_algebraic()] = count

    return results


# Known correct Perft values for standard starting position
PERFT_STARTING_POSITION = {
    0: 1,
    1: 20,
    2: 400,
    3: 5_902,
    4: 119_060,
    5: 1_881_169,
    6: 26_889_610,
}

# Test positions for special rules (castling, en passant, promotion)
PERFT_TEST_POSITIONS = {
    "kiwipete": {
        "fen": "r3k2r/p1ppqpb1/bn2pnp1/3PN3/1p2P3/2N2Q1p/PPPBBPPP/R3K2R w KQkq - 0 1",
        "perft": {
            0: 1,
            1: 48,
            2: 2_039,
            3: 97_862,
            4: 4_085_603,
            5: 193_690_690,
        },
    },
    "position_3": {
        "fen": "8/2p5/3p4/KP5r/1R3p1k/8/4P1P1/8 w - - 0 1",
        "perft": {
            0: 1,
            1: 14,
            2: 191,
            3: 2_812,
            4: 43_238,
            5: 674_624,
            6: 11_030_083,
        },
    },
    "position_4": {
        "fen": "r3k2r/Pppp1ppp/1b3nb1/nP2p3/BBP1P3/q1PPN3/Pp1PPQPP/RN2K2R w KQkq c3 0 1",
        "perft": {
            0: 1,
            1: 6,
            2: 264,
            3: 9_467,
            4: 422_333,
            5: 15_833_292,
        },
    },
    "position_5": {
        "fen": "rnbqkb1r/pp1p1ppp/2p5/4p3/2B1P3/5N2/PPPP1PPP/RNBQK2R w KQkq e6 0 1",
        "perft": {
            0: 1,
            1: 29,
            2: 953,
            3: 27_990,
            4: 871_198,
            5: 27_581_701,
        },
    },
    "position_6": {
        "fen": "r3k2r/p1ppqpb1/bn2pnp1/3PN3/1p2P3/2N2Q1p/PPPBBPPP/R3K2R w KQkq - 0 1",
        "perft": {
            0: 1,
            1: 48,
            2: 2_039,
            3: 97_862,
            4: 4_085_603,
            5: 193_690_690,
        },
    },
}


def run_perft_test(position_name="starting", depth=4):
    """Run a perft test and return results with validation."""
    if position_name == "starting":
        board = Board()
        expected = PERFT_STARTING_POSITION
    else:
        test_position = PERFT_TEST_POSITIONS.get(position_name)
        if not test_position:
            raise ValueError(f"Unknown test position: {position_name}")
        board = Board()
        board.from_fen(test_position["fen"])
        expected = test_position.get("perft", {})

    results = {}
    for d in range(depth + 1):
        count = perft(board, d)
        expected_count = expected.get(d, None)
        status = "✓" if expected_count is None or count == expected_count else "✗"
        results[d] = {
            "count": count,
            "expected": expected_count,
            "status": status,
        }

    return results
