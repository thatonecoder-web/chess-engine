"""Tests for game history, PGN parsing, and game persistence."""

import pytest
import tempfile
import json
from chess_engine.game import GameHistory, Game
from chess_engine.board import Board
from chess_engine.moves import Move


class TestGameHistory:
    """Test move history tracking and undo/redo."""

    def test_game_history_initialization(self):
        """GameHistory should initialize empty."""
        history = GameHistory()
        assert len(history.moves) == 0
        assert len(history.board_states) == 0
        assert history.current_index == -1
        assert not history.can_undo()
        assert not history.can_redo()

    def test_add_move_to_history(self):
        """Adding a move should update history state."""
        board = Board()
        history = GameHistory()
        move = Move("e2", "e4")

        board.make_move(move)
        history.add_move(move, board)

        assert len(history.moves) == 1
        assert history.current_index == 0
        assert history.can_undo()
        assert not history.can_redo()

    def test_undo_move(self):
        """Undo should restore previous board state."""
        board = Board()
        history = GameHistory()
        move = Move("e2", "e4")

        board.make_move(move)
        history.add_move(move, board)
        initial_state = board.to_fen()

        history.undo(board)
        assert history.current_index == -1
        assert board.to_fen() == "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"

    def test_redo_move(self):
        """Redo should restore undone move."""
        board = Board()
        history = GameHistory()
        move = Move("e2", "e4")

        board.make_move(move)
        history.add_move(move, board)
        fen_after_move = board.to_fen()

        history.undo(board)
        assert history.can_redo()

        history.redo(board)
        assert history.current_index == 0
        assert board.to_fen() == fen_after_move

    def test_get_all_moves(self):
        """get_all_moves should return complete move list."""
        board = Board()
        history = GameHistory()

        move1 = Move("e2", "e4")
        board.make_move(move1)
        history.add_move(move1, board)

        move2 = Move("e7", "e5")
        board.make_move(move2)
        history.add_move(move2, board)

        moves = history.get_all_moves()
        assert len(moves) == 2


class TestGame:
    """Test Game class with metadata and PGN support."""

    def test_game_initialization(self):
        """Game should initialize with empty board and metadata."""
        game = Game()
        assert game.board is not None
        assert game.history is not None
        assert game.metadata["Result"] == "*"

    def test_game_make_move(self):
        """Game should track moves."""
        game = Game()
        move = Move("e2", "e4")

        assert game.make_move(move)
        assert len(game.history.get_all_moves()) == 1

    def test_game_undo_redo(self):
        """Game should support undo/redo."""
        game = Game()
        move1 = Move("e2", "e4")
        move2 = Move("e7", "e5")

        game.make_move(move1)
        game.make_move(move2)
        assert len(game.history.get_all_moves()) == 2

        assert game.undo()
        assert len(game.history.get_moves_up_to_current()) == 1

        assert game.redo()
        assert len(game.history.get_moves_up_to_current()) == 2

    def test_set_and_get_metadata(self):
        """Game metadata should be settable and gettable."""
        game = Game()
        game.set_metadata("White", "Alice")
        game.set_metadata("Black", "Bob")

        assert game.get_metadata("White") == "Alice"
        assert game.get_metadata("Black") == "Bob"

    def test_to_pgn_basic(self):
        """to_pgn should generate valid PGN format."""
        game = Game()
        game.set_metadata("White", "Player1")
        game.set_metadata("Black", "Player2")

        move1 = Move("e2", "e4")
        move2 = Move("e7", "e5")
        game.make_move(move1)
        game.make_move(move2)

        pgn = game.to_pgn()
        assert "[White" in pgn
        assert "[Black" in pgn
        assert "e2e4" in pgn
        assert "e7e5" in pgn

    def test_from_pgn_basic(self):
        """from_pgn should parse a basic PGN string."""
        pgn_text = """[Event "Test"]
[Site "?"]
[Date "2026.09.11"]
[White "Alice"]
[Black "Bob"]
[Result "*"]

1. e2e4 e7e5
"""
        game = Game()
        game.from_pgn(pgn_text)

        assert game.get_metadata("White") == "Alice"
        assert game.get_metadata("Black") == "Bob"
        assert len(game.history.get_all_moves()) == 2

    def test_pgn_round_trip(self):
        """PGN should round-trip: to_pgn -> from_pgn should preserve moves."""
        game1 = Game()
        game1.set_metadata("White", "Alice")
        game1.set_metadata("Black", "Bob")

        moves = [
            Move("e2", "e4"),
            Move("c7", "c5"),
            Move("g1", "f3"),
            Move("d7", "d6"),
        ]

        for move in moves:
            game1.make_move(move)

        pgn = game1.to_pgn()

        game2 = Game()
        game2.from_pgn(pgn)

        assert len(game2.history.get_all_moves()) == len(moves)
        for i, move in enumerate(moves):
            assert game2.history.get_all_moves()[i].to_algebraic() == move.to_algebraic()

    def test_save_to_file(self):
        """Game should save to JSON file."""
        game = Game()
        game.make_move(Move("e2", "e4"))
        game.make_move(Move("e7", "e5"))

        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
            filename = f.name

        try:
            game.save_to_file(filename)

            with open(filename, 'r') as f:
                data = json.load(f)

            assert len(data["moves"]) == 2
            assert data["moves"][0] == "e2e4"
            assert data["moves"][1] == "e7e5"
        finally:
            import os
            os.unlink(filename)

    def test_load_from_file(self):
        """Game should load from JSON file."""
        game1 = Game()
        game1.make_move(Move("e2", "e4"))
        game1.make_move(Move("e7", "e5"))

        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
            filename = f.name

        try:
            game1.save_to_file(filename)

            game2 = Game()
            game2.load_from_file(filename)

            moves = game2.history.get_all_moves()
            assert len(moves) == 2
            assert moves[0].to_algebraic() == "e2e4"
            assert moves[1].to_algebraic() == "e7e5"
        finally:
            import os
            os.unlink(filename)
