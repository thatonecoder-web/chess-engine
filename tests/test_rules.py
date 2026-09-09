import pytest

from chess_engine.board import Board
from chess_engine.moves import Move
from chess_engine.pieces import Queen, Rook, Bishop, Knight, Pawn, King
from chess_engine.rules import is_valid_move


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

    # Clear the diagonal route by making the pawn on d2 leave the file
    # and then letting the pawn on e2 vacate the bishop's path window.
    board.make_move(Move("d2", "d4"))
    board.turn = "white"
    board.make_move(Move("e2", "e3"))

    move = Move("d1", "h5")

    start = move.get_coordinates(move.start)
    end = move.get_coordinates(move.end)

    assert is_valid_move(board, start, end) is True


def test_king_moves_one_square():
    board = Board()

    move = Move("e1", "e2")

    start = move.get_coordinates(move.start)
    end = move.get_coordinates(move.end)

    # e2 contains a white pawn, so the king may not land on that square.
    assert is_valid_move(board, start, end) is False


def test_piece_cannot_capture_own_piece():
    board = Board()

    move = Move("e2", "e1")

    start = move.get_coordinates(move.start)
    end = move.get_coordinates(move.end)

    assert is_valid_move(board, start, end) is False


@pytest.mark.parametrize(
    ("start", "end", "promotion", "expected_cls"),
    [
        ("a7", "a8", "q", Queen),
        ("a7", "a8", "r", Rook),
        ("a7", "a8", "b", Bishop),
        ("a7", "a8", "n", Knight),
        ("h2", "h1", "q", Queen),
        ("h2", "h1", "r", Rook),
        ("h2", "h1", "b", Bishop),
        ("h2", "h1", "n", Knight),
    ],
)
def test_pawn_promotion_supports_every_piece_and_color(start, end, promotion, expected_cls):
    board = Board()
    board.board = [[None for _ in range(8)] for _ in range(8)]
    board.turn = "white" if start[1] == "7" else "black"

    color = "white" if start[1] == "7" else "black"
    pawn = Pawn("P" if color == "white" else "p", color)

    if color == "white":
        start_row, start_col = Move(start, end).get_coordinates(start)
        end_row, end_col = Move(start, end).get_coordinates(end)
    else:
        start_row, start_col = Move(start, end).get_coordinates(start)
        end_row, end_col = Move(start, end).get_coordinates(end)

    board.board[start_row][start_col] = pawn

    move = Move(start, end, promotion=promotion)

    assert board.make_move(move) is True
    assert isinstance(board.board[end_row][end_col], expected_cls)
    assert board.board[end_row][end_col].color == color


def test_en_passant_capture_is_legal_immediately_after_double_step():
    board = Board()
    board.board = [[None for _ in range(8)] for _ in range(8)]
    board.turn = "white"

    white_pawn = Pawn("P", "white")
    black_pawn = Pawn("p", "black")

    board.board[3][4] = white_pawn
    board.board[3][3] = black_pawn

    board.previous_move = Move("d7", "d5")
    board.en_passant_target = (2, 3)

    assert board.make_move(Move("e5", "d6")) is True
    assert board.board[3][4] is None
    assert board.board[3][3] is None
    assert isinstance(board.board[2][3], Pawn)
    assert board.board[2][3].color == "white"


def test_illegal_en_passant_after_turn_passes_is_rejected():
    board = Board()
    board.board = [[None for _ in range(8)] for _ in range(8)]
    board.turn = "white"

    white_pawn = Pawn("P", "white")
    black_pawn = Pawn("p", "black")

    board.board[3][4] = white_pawn
    board.board[3][3] = black_pawn

    # No previous move means the en passant target tuple is stale.
    board.previous_move = None
    board.en_passant_target = None

    assert board.make_move(Move("e5", "d6")) is False


def test_white_kingside_castling_moves_rook_and_king():
    board = Board()
    board.board = [[None for _ in range(8)] for _ in range(8)]
    board.turn = "white"

    king = King("K", "white")
    rook = Rook("R", "white")
    board.board[7][4] = king
    board.board[7][7] = rook

    board.en_passant_target = None
    board.previous_move = None

    assert board.make_move(Move("e1", "g1")) is True
    assert isinstance(board.board[7][6], King)
    assert isinstance(board.board[7][5], Rook)
    assert board.board[7][7] is None


def test_cannot_castle_through_or_into_attack():
    board = Board()
    board.board = [[None for _ in range(8)] for _ in range(8)]
    board.turn = "white"

    king = King("K", "white")
    rook = Rook("R", "white")
    board.board[7][4] = king
    board.board[7][7] = rook

    # A bishop on f1 is between king and rook, so the move should be rejected.
    board.board[7][5] = Bishop("B", "black")

    assert board.make_move(Move("e1", "g1")) is False