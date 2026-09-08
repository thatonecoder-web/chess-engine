from src.board import Board
from src.moves import Move
from src.rules import is_valid_move


def test_pawn_can_move_one_square():
    board = Board()

    move = Move("e2", "e3")

    start = move.get_coordinates(move.start)
    end = move.get_coordinates(move.end)

    assert is_valid_move(board, start, end) is True


def test_pawn_can_move_two_squares():
    board = Board()

    move = Move("e2", "e4")

    start = move.get_coordinates(move.start)
    end = move.get_coordinates(move.end)

    assert is_valid_move(board, start, end) is True


def test_pawn_cannot_move_three_squares():
    board = Board()

    move = Move("e2", "e5")

    start = move.get_coordinates(move.start)
    end = move.get_coordinates(move.end)

    assert is_valid_move(board, start, end) is False


def test_knight_can_jump():
    board = Board()

    move = Move("g1", "f3")

    start = move.get_coordinates(move.start)
    end = move.get_coordinates(move.end)

    assert is_valid_move(board, start, end) is True


def test_bishop_moves_diagonally():
    board = Board()

    # Clear the pawn first.
    board.make_move(Move("e2", "e4"))

    move = Move("f1", "b5")

    start = move.get_coordinates(move.start)
    end = move.get_coordinates(move.end)

    assert is_valid_move(board, start, end) is True


def test_bishop_cannot_move_through_piece():
    board = Board()

    move = Move("f1", "b5")

    start = move.get_coordinates(move.start)
    end = move.get_coordinates(move.end)

    assert is_valid_move(board, start, end) is False


def test_rook_moves_straight():
    board = Board()

    # Clear the pawn in front of the rook.
    board.make_move(Move("a2", "a4"))

    move = Move("a1", "a3")

    start = move.get_coordinates(move.start)
    end = move.get_coordinates(move.end)

    assert is_valid_move(board, start, end) is True


def test_queen_moves_diagonally():
    board = Board()

    # Clear the diagonal path.
    board.make_move(Move("d2", "d4"))

    move = Move("d1", "h5")

    start = move.get_coordinates(move.start)
    end = move.get_coordinates(move.end)

    assert is_valid_move(board, start, end) is True


def test_king_moves_one_square():
    board = Board()

    # Clear the square in front of the king.
    board.make_move(Move("e2", "e3"))

    move = Move("e1", "e2")

    start = move.get_coordinates(move.start)
    end = move.get_coordinates(move.end)

    # e2 contains the pawn, so this should be rejected.
    assert is_valid_move(board, start, end) is False


def test_piece_cannot_capture_own_piece():
    board = Board()

    move = Move("e2", "e1")

    start = move.get_coordinates(move.start)
    end = move.get_coordinates(move.end)

    assert is_valid_move(board, start, end) is False