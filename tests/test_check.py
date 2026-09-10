from chess_engine.board import Board
from chess_engine.moves import Move
from chess_engine.pieces import Pawn
from chess_engine.check import (
    find_king,
    is_square_attacked,
    is_in_check,
    move_leaves_king_in_check,
    has_legal_moves,
    generate_legal_moves,
    is_checkmate,
    is_stalemate,
)


def test_find_white_king():
    board = Board()

    assert find_king(board, "white") == (7, 4)


def test_find_black_king():
    board = Board()

    assert find_king(board, "black") == (0, 4)


def test_king_not_in_check_at_start():
    board = Board()

    assert is_in_check(board, "white") is False
    assert is_in_check(board, "black") is False


def test_rook_can_attack_king():
    board = Board()

    # Clear the board.
    board.board = [[None for _ in range(8)] for _ in range(8)]

    # White king on e1.
    board.board[7][4] = board._create_board()[7][4]

    # Black rook on e8.
    board.board[0][4] = board._create_board()[0][0]

    board.board[0][4].color = "black"

    assert is_in_check(board, "white") is True


def test_bishop_can_attack_king():
    board = Board()

    board.board = [[None for _ in range(8)] for _ in range(8)]

    original = board._create_board()

    # White king on e1.
    board.board[7][4] = original[7][4]

    # Black bishop on b4.
    board.board[4][1] = original[0][2]

    assert is_in_check(board, "white") is True


def test_knight_can_attack_king():
    board = Board()

    board.board = [[None for _ in range(8)] for _ in range(8)]

    original = board._create_board()

    # White king on e4.
    board.board[4][4] = original[7][4]

    # Black knight on f6.
    board.board[2][5] = original[0][1]

    assert is_in_check(board, "white") is True


def test_king_cannot_move_into_check():
    board = Board()

    board.board = [[None for _ in range(8)] for _ in range(8)]

    original = board._create_board()

    # White king on e1.
    board.board[7][4] = original[7][4]

    # Black rook on e8.
    board.board[0][4] = original[0][0]

    start = (7, 4)
    end = (6, 4)

    assert move_leaves_king_in_check(board, start, end) is True


def test_king_can_move_when_not_into_check():
    board = Board()

    board.board = [[None for _ in range(8)] for _ in range(8)]

    original = board._create_board()

    # White king on e1.
    board.board[7][4] = original[7][4]

    start = (7, 4)
    end = (6, 4)

    assert move_leaves_king_in_check(board, start, end) is False


def test_player_has_legal_moves_at_start():
    board = Board()

    assert has_legal_moves(board, "white") is True
    assert has_legal_moves(board, "black") is True


def test_position_is_not_checkmate_at_start():
    board = Board()

    assert is_checkmate(board, "white") is False
    assert is_checkmate(board, "black") is False


def test_position_is_not_stalemate_at_start():
    board = Board()

    assert is_stalemate(board, "white") is False
    assert is_stalemate(board, "black") is False


def test_generate_legal_moves_returns_a_list_for_white_at_start():
    board = Board()

    moves = generate_legal_moves(board, "white")

    assert isinstance(moves, list)
    assert len(moves) >= 20
    assert all(isinstance(move, Move) for move in moves)


def test_pawn_attacks_are_detected_on_the_diagonal_even_when_target_square_is_empty():
    board = Board()
    board.board = [[None for _ in range(8)] for _ in range(8)]

    black_pawn = Pawn("p", "black")
    board.board[4][4] = black_pawn

    assert is_square_attacked(board, 5, 5, "black") is True