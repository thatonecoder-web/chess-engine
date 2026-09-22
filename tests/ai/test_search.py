"""Tests for AI/search.py."""

import time

from chess_engine.core.board import Board
from chess_engine.ai.search import (
    alpha_beta_search,
    quiescence_search,
    iterative_deepening_search,
    get_top_n_moves,
    SearchStats,
)
from chess_engine.ai.evaluation import CHECKMATE_SCORE


class TestAlphaBetaBasics:
    def test_returns_a_legal_move_from_the_start_position(self):
        board = Board()
        score, move = alpha_beta_search(board, depth=2, maximizing=True)
        legal = {(m.start, m.end) for m in board.get_legal_moves("white")}
        assert (move.start, move.end) in legal

    def test_finds_mate_in_one_for_white(self):
        board = Board()
        # Scholar's-mate setup: White to move, Qxf7# is available.
        board.from_fen("r1bqkb1r/pppp1ppp/2n2n2/4p2Q/2B1P3/8/PPPP1PPP/RNB1K1NR w KQkq - 4 4")
        score, move = alpha_beta_search(board, depth=1, maximizing=True)
        assert move.start == "h5" and move.end == "f7"
        assert score == CHECKMATE_SCORE

    def test_finds_mate_in_one_for_black(self):
        board = Board()
        # Fool's mate setup: Black to move, Qh4# is available.
        board.from_fen("rnbqkbnr/pppp1ppp/8/4p3/6P1/5P2/PPPPP2P/RNBQKBNR b KQkq - 0 2")
        score, move = alpha_beta_search(board, depth=1, maximizing=False)
        assert move.start == "d8" and move.end == "h4"
        assert score == -CHECKMATE_SCORE

    def test_deterministic_across_repeated_runs(self):
        board = Board()
        result_a = alpha_beta_search(board, depth=2, maximizing=True)
        result_b = alpha_beta_search(board, depth=2, maximizing=True)
        assert result_a[0] == result_b[0]
        assert (result_a[1].start, result_a[1].end) == (result_b[1].start, result_b[1].end)


class TestQuiescenceSearch:
    def test_does_not_stop_mid_capture_sequence(self):
        # White to move; Nxe5 wins a pawn but is recaptured by the
        # d-pawn. A search that ignores the recapture (no quiescence)
        # would misjudge this as White simply winning a pawn for free.
        board = Board()
        board.from_fen("4k3/3p4/8/4n3/8/8/8/4KN2 w - - 0 1")
        score = quiescence_search(board, float("-inf"), float("inf"), maximizing=True,
                                   perspective="white")
        # After Nxe5 dxe5, material is even -> the quiescent score
        # should settle near 0, not "White is up a knight for a pawn".
        assert abs(score) < 150

    def test_quiet_position_returns_static_eval(self):
        board = Board()
        score = quiescence_search(board, float("-inf"), float("inf"), maximizing=True,
                                   perspective="white")
        assert score == 0


class TestIterativeDeepening:
    def test_returns_a_legal_move(self):
        board = Board()
        score, move, stats = iterative_deepening_search(board, max_depth=3, time_limit=5)
        legal = {(m.start, m.end) for m in board.get_legal_moves("white")}
        assert (move.start, move.end) in legal
        assert isinstance(stats, SearchStats)
        assert stats.depth_reached >= 1

    def test_respects_time_limit(self):
        board = Board()
        start = time.time()
        score, move, stats = iterative_deepening_search(board, max_depth=20, time_limit=0.3)
        elapsed = time.time() - start
        assert move is not None
        # Generous margin: the clock is only polled periodically inside
        # search, and one already-started iteration must finish.
        assert elapsed < 3.0

    def test_stops_early_on_forced_mate(self):
        board = Board()
        board.from_fen("r1bqkb1r/pppp1ppp/2n2n2/4p2Q/2B1P3/8/PPPP1PPP/RNB1K1NR w KQkq - 4 4")
        score, move, stats = iterative_deepening_search(board, max_depth=10, time_limit=5)
        assert score == CHECKMATE_SCORE
        assert move.start == "h5" and move.end == "f7"

    def test_deterministic_across_repeated_runs(self):
        board = Board()
        _, move_a, _ = iterative_deepening_search(board, max_depth=3, time_limit=5)
        _, move_b, _ = iterative_deepening_search(board, max_depth=3, time_limit=5)
        assert (move_a.start, move_a.end) == (move_b.start, move_b.end)


class TestGetTopNMoves:
    def test_returns_moves_sorted_best_first_for_white(self):
        board = Board()
        top = get_top_n_moves(board, depth=2, n=3, maximizing=True)
        scores = [score for score, _ in top]
        assert scores == sorted(scores, reverse=True)

    def test_returns_moves_sorted_best_first_for_black(self):
        board = Board()
        board.make_move(board.get_legal_moves("white")[0])
        top = get_top_n_moves(board, depth=2, n=3, maximizing=False)
        scores = [score for score, _ in top]
        # For Black, "best" means most negative on the fixed
        # white-relative scale, so ascending order is best-first.
        assert scores == sorted(scores)
