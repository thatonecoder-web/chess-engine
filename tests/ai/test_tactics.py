"""
Tactical regression positions.

Each entry is a known tactical motif (fork, pin/skewer, back-rank mate,
mate-in-2) with a FEN and the move (or one of a small set of equally
winning moves) the engine is expected to find. These aren't puzzles
about "does the engine play well" in a fuzzy sense — every position
here has one clearly, objectively best move, so a search deep/wide
enough to be worth shipping should find it every time.

Kept separate from test_search.py's unit-level checks so this file can
double as a quick "did a change to evaluation/search/move_ordering
regress tactical strength" smoke test.
"""

import pytest

from chess_engine.core.board import Board
from chess_engine.ai.search import iterative_deepening_search

TACTICAL_POSITIONS = [
    pytest.param(
        # White to move: Qxf7# (scholar's mate finish).
        "r1bqkb1r/pppp1ppp/2n2n2/4p2Q/2B1P3/8/PPPP1PPP/RNB1K1NR w KQkq - 4 4",
        {("h5", "f7")},
        4,
        id="scholars_mate_finish",
    ),
    pytest.param(
        # Black to move: Qh4# (fool's mate finish).
        "rnbqkbnr/pppp1ppp/8/4p3/6P1/5P2/PPPPP2P/RNBQKBNR b KQkq - 0 2",
        {("d8", "h4")},
        4,
        id="fools_mate_finish",
    ),
    pytest.param(
        # White to move: back-rank mate with Re8#. Black's king is
        # boxed in by its own pawns, and the e-file is completely open.
        "6k1/5ppp/8/8/8/8/8/4R1K1 w - - 0 1",
        {("e1", "e8")},
        3,
        id="back_rank_mate",
    ),
    pytest.param(
        # White knight fork: Nc7+ forks Black's king (e8) and rook (a8) —
        # the king must move, and Nxa8 wins the rook next.
        "r3k2r/8/8/3N4/8/8/8/4K3 w kq - 0 1",
        {("d5", "c7")},
        4,
        id="knight_fork_wins_rook",
    ),
    pytest.param(
        # White to move: the rook on a1 is undefended and blocked from
        # giving check by White's own queen — Qxa1 just wins it outright.
        "6k1/8/8/8/8/8/6PP/r3Q1K1 w - - 0 1",
        {("e1", "a1")},
        3,
        id="queen_wins_undefended_rook",
    ),
]


@pytest.mark.parametrize("fen, acceptable_moves, depth", TACTICAL_POSITIONS)
def test_finds_the_tactic(fen, acceptable_moves, depth):
    board = Board()
    board.from_fen(fen)

    _, move, _ = iterative_deepening_search(board, max_depth=depth, time_limit=10)

    assert move is not None
    assert (move.start, move.end) in acceptable_moves, (
        f"expected one of {acceptable_moves}, engine played {move.start}{move.end}"
    )
