from src.board import Board
from src.moves import Move


def test_board_creation():
    board = Board()

    assert board.board[6][0].symbol == "P"
    assert board.board[7][4].symbol == "K"
    assert board.board[1][0].symbol == "p"
    assert board.turn == "white"


def test_move_piece():
    board = Board()

    move = Move("e2", "e4")

    assert board.make_move(move) is True
    assert board.board[6][4] is None
    assert board.board[4][4].symbol == "P"


def test_turn_switches():
    board = Board()

    board.make_move(Move("e2", "e4"))

    assert board.turn == "black"

    board.make_move(Move("e7", "e5"))

    assert board.turn == "white"


def test_cannot_move_empty_square():
    board = Board()

    move = Move("e4", "e5")

    assert board.make_move(move) is False


def test_cannot_move_opponents_piece():
    board = Board()

    move = Move("e7", "e5")

    assert board.make_move(move) is False


def test_cannot_capture_own_piece():
    board = Board()

    move = Move("e2", "e1")

    assert board.make_move(move) is False