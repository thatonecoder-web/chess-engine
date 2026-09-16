"""Tests for AI/evaluation.py."""

from chess_engine.board import Board
from chess_engine.moves import Move
from chess_engine.AI.evaluation import (
    evaluate,
    CHECKMATE_SCORE,
    PIECE_VALUES,
    _pawn_structure,
    _king_safety,
)


class TestMaterialAndSymmetry:
    def test_starting_position_is_balanced(self):
        board = Board()
        assert evaluate(board) == 0

    def test_perspective_flip_is_antisymmetric(self):
        board = Board()
        board.make_move(Move("e2", "e4"))
        white_score = evaluate(board, perspective="white")
        black_score = evaluate(board, perspective="black")
        assert white_score == -black_score

    def test_extra_queen_favors_that_side(self):
        board = Board()
        board.from_fen("4k3/8/8/8/8/8/8/3QK3 w - - 0 1")
        assert evaluate(board, perspective="white") > PIECE_VALUES["Q"]

    def test_extra_queen_for_black_favors_black(self):
        board = Board()
        board.from_fen("3qk3/8/8/8/8/8/8/4K3 w - - 0 1")
        assert evaluate(board, perspective="white") < -PIECE_VALUES["Q"]


class TestCheckmateAndStalemate:
    def test_white_checkmated_scores_minimum(self):
        board = Board()
        # Fool's mate: White has just been checkmated.
        board.from_fen("rnb1kbnr/pppp1ppp/8/4p3/6Pq/5P2/PPPPP2P/RNBQKBNR w KQkq - 1 3")
        assert evaluate(board, perspective="white") == -CHECKMATE_SCORE
        assert evaluate(board, perspective="black") == CHECKMATE_SCORE

    def test_stalemate_scores_zero(self):
        board = Board()
        # Classic stalemate: Black to move, not in check, no legal moves.
        board.from_fen("7k/5Q2/6K1/8/8/8/8/8 b - - 0 1")
        assert evaluate(board, perspective="white") == 0
        assert evaluate(board, perspective="black") == 0


class TestPieceSquareTables:
    def test_centralized_knight_beats_cornered_knight(self):
        centralized = Board()
        centralized.from_fen("4k3/8/8/3N4/8/8/8/4K3 w - - 0 1")

        cornered = Board()
        cornered.from_fen("4k3/8/8/8/8/8/8/N3K3 w - - 0 1")

        assert evaluate(centralized) > evaluate(cornered)


class TestPawnStructure:
    def test_doubled_pawns_penalized(self):
        doubled = Board()
        doubled.from_fen("4k3/8/8/8/4P3/8/4P3/4K3 w - - 0 1")

        spread = Board()
        spread.from_fen("4k3/8/8/8/4P3/8/3P4/4K3 w - - 0 1")

        assert _pawn_structure(doubled) < _pawn_structure(spread)

    def test_isolated_pawn_penalized(self):
        isolated = Board()
        isolated.from_fen("4k3/8/8/8/8/8/4P3/4K3 w - - 0 1")

        supported = Board()
        supported.from_fen("4k3/8/8/8/8/8/3PP3/4K3 w - - 0 1")

        assert _pawn_structure(isolated) < _pawn_structure(supported)

    def test_advanced_passed_pawn_beats_less_advanced_passed_pawn(self):
        far_advanced = Board()
        far_advanced.from_fen("4k3/8/4P3/8/8/8/8/4K3 w - - 0 1")

        less_advanced = Board()
        less_advanced.from_fen("4k3/8/8/8/8/8/4P3/4K3 w - - 0 1")

        assert _pawn_structure(far_advanced) > _pawn_structure(less_advanced)

    def test_blocked_pawn_is_not_passed(self):
        passed = Board()
        passed.from_fen("4k3/8/8/4P3/8/8/8/4K3 w - - 0 1")

        blocked = Board()
        blocked.from_fen("4k3/4p3/8/4P3/8/8/8/4K3 w - - 0 1")

        assert _pawn_structure(passed) > _pawn_structure(blocked)


class TestKingSafety:
    def test_shielded_king_beats_exposed_king(self):
        shielded = Board()
        shielded.from_fen("4k3/8/8/8/8/5PPP/8/4RK2 w - - 0 1")

        exposed = Board()
        exposed.from_fen("4k3/8/8/8/8/8/8/4RK2 w - - 0 1")

        assert _king_safety(shielded) > _king_safety(exposed)

    def test_king_on_open_file_penalized(self):
        open_file = Board()
        open_file.from_fen("4k3/8/8/8/8/8/8/4K3 w - - 0 1")

        closed_file = Board()
        closed_file.from_fen("4k3/8/8/8/8/8/4P3/4K3 w - - 0 1")

        assert _king_safety(open_file) < _king_safety(closed_file)
