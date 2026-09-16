"""Tests for AI/move_ordering.py."""

from chess_engine.board import Board
from chess_engine.moves import Move
from chess_engine.AI.move_ordering import (
    order_moves,
    MoveOrderingHeuristics,
    _captured_piece,
)


def _find(moves, start, end):
    for move in moves:
        if move.start == start and move.end == end:
            return move
    raise AssertionError(f"{start}{end} not found among {[str(m) for m in moves]}")


class TestCaptureOrdering:
    def test_captures_come_before_quiet_moves(self):
        board = Board()
        # White pawn e4 can capture Black's pawn on d5, or play a quiet move.
        board.from_fen("rnbqkbnr/ppp1pppp/8/3p4/4P3/8/PPPP1PPP/RNBQKBNR w KQkq d6 0 2")
        moves = board.get_legal_moves("white")
        ordered = order_moves(board, moves)

        capture = _find(ordered, "e4", "d5")
        assert ordered.index(capture) == 0

    def test_mvv_lva_prefers_capturing_higher_value_victim(self):
        board = Board()
        # White rook can capture either the queen (same rank) or the
        # knight (same file); MVV-LVA should rank the queen capture first.
        board.from_fen("4k3/8/2n5/8/8/2R4q/8/4K3 w - - 0 1")
        moves = board.get_legal_moves("white")
        ordered = order_moves(board, moves)

        rook_takes_queen = _find(ordered, "c3", "h3")
        rook_takes_knight = _find(ordered, "c3", "c6")
        assert ordered.index(rook_takes_queen) < ordered.index(rook_takes_knight)

    def test_en_passant_capture_is_detected(self):
        board = Board()
        board.from_fen("4k3/8/8/3pP3/8/8/8/4K3 w - d6 0 1")
        move = Move("e5", "d6")
        captured = _captured_piece(board, move)
        assert captured is not None
        assert captured.symbol == "p"


class TestPromotionOrdering:
    def test_promotion_ranked_above_quiet_moves(self):
        board = Board()
        board.from_fen("8/4P1k1/8/8/8/8/6K1/8 w - - 0 1")
        moves = board.get_legal_moves("white")
        ordered = order_moves(board, moves)

        promotion = _find(ordered, "e7", "e8")
        king_move = _find(ordered, "g2", "g1")
        assert ordered.index(promotion) < ordered.index(king_move)


class TestHintMove:
    def test_hint_move_is_tried_first(self):
        board = Board()
        moves = board.get_legal_moves("white")
        # Pick an arbitrary legal move as the "previous iteration's best".
        hint = _find(moves, "g1", "f3")
        ordered = order_moves(board, moves, hint_move=hint)
        assert ordered[0] == hint


class TestKillerAndHistoryHeuristics:
    def test_killer_move_boosted_at_its_ply(self):
        board = Board()
        moves = board.get_legal_moves("white")
        killer = _find(moves, "b1", "c3")

        heuristics = MoveOrderingHeuristics()
        heuristics.killer_moves[2] = [killer]

        ordered = order_moves(board, moves, heuristics=heuristics, ply=2)
        # The killer should now rank above other quiet, non-capture moves.
        assert ordered.index(killer) < len(moves) - 1
        assert ordered.index(killer) == 0

    def test_history_score_accumulates_and_orders(self):
        board = Board()
        moves = board.get_legal_moves("white")
        favored = _find(moves, "b1", "c3")

        heuristics = MoveOrderingHeuristics()
        heuristics.record_cutoff(favored, board, ply=5, depth=4)

        ordered = order_moves(board, moves, heuristics=heuristics)
        # No captures/promotions/checks are available from the start
        # position, so the history-boosted move should sort first among
        # otherwise-equal quiet moves.
        assert ordered[0] == favored


class TestDeterminism:
    def test_ordering_is_stable_across_repeated_calls(self):
        board = Board()
        moves = board.get_legal_moves("white")

        first = [str(m) for m in order_moves(board, list(moves))]
        second = [str(m) for m in order_moves(board, list(moves))]
        assert first == second
