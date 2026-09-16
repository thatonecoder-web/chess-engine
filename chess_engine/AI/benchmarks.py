"""
benchmarks.py
=============

AI performance benchmarks: how many nodes/second the search reaches,
and how deep iterative deepening gets within a fixed time budget, on a
handful of representative positions (opening, a tactical middlegame
position, and a sparse endgame).

Kept separate from the pytest suite (which cares about correctness,
not speed) — this is what run_ai_benchmarks.py at the repo root calls
to print a human-readable report, and it's also handy from a shell for
checking whether a change to evaluation/search/move_ordering made
things meaningfully faster or slower.
"""

from ..board import Board
from .search import iterative_deepening_search

BENCHMARK_POSITIONS = {
    "starting_position": (
        "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"
    ),
    "open_middlegame": (
        # Italian Game middlegame: lots of piece activity, few forced lines.
        "r1bqk2r/pppp1ppp/2n2n2/2b1p3/2B1P3/3P1N2/PPP2PPP/RNBQ1RK1 w kq - 4 6"
    ),
    "tactical_middlegame": (
        # Kiwipete: the standard "everything is loose" perft/tactics stress test.
        "r3k2r/p1ppqpb1/bn2pnp1/3PN3/1p2P3/2N2Q1p/PPPBBPPP/R3K2R w KQkq - 0 1"
    ),
    "sparse_endgame": (
        "8/5k2/8/8/8/8/3K1P2/8 w - - 0 1"
    ),
}


def benchmark_position(fen, max_depth=5, time_limit=5.0):
    """Run one timed iterative-deepening search and return its SearchStats."""
    board = Board()
    board.from_fen(fen)
    _, _, stats = iterative_deepening_search(board, max_depth=max_depth, time_limit=time_limit)
    return stats


def run_ai_benchmarks(max_depth=5, time_limit=5.0):
    """Run every position in BENCHMARK_POSITIONS and return
    {name: SearchStats}, in the same order they're defined."""
    return {
        name: benchmark_position(fen, max_depth=max_depth, time_limit=time_limit)
        for name, fen in BENCHMARK_POSITIONS.items()
    }
