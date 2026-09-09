from .rules import is_valid_move


def find_king(board, color):
    """Return the king's board coordinates for the given color."""

    for row in range(8):
        for col in range(8):
            piece = board.board[row][col]

            if (
                piece is not None
                and piece.color == color
                and piece.symbol.lower() == "k"
            ):
                return row, col

    return None


def is_square_attacked(board, row, col, by_color):
    """Check whether a square is attacked by a given color."""

    for start_row in range(8):
        for start_col in range(8):
            piece = board.board[start_row][start_col]

            if piece is None or piece.color != by_color:
                continue

            if is_valid_move(
                board,
                (start_row, start_col),
                (row, col),
            ):
                return True

    return False


def is_in_check(board, color):
    """Check whether the given color's king is currently in check."""

    king_position = find_king(board, color)

    if king_position is None:
        return False

    king_row, king_col = king_position

    opponent = "black" if color == "white" else "white"

    return is_square_attacked(
        board,
        king_row,
        king_col,
        opponent,
    )


def make_temporary_move(board, start, end):
    """Make a temporary move and return the captured piece."""

    start_row, start_col = start
    end_row, end_col = end

    captured_piece = board.board[end_row][end_col]

    board.board[end_row][end_col] = board.board[start_row][start_col]
    board.board[start_row][start_col] = None

    return captured_piece


def undo_temporary_move(board, start, end, captured_piece):
    """Undo a temporary move."""

    start_row, start_col = start
    end_row, end_col = end

    board.board[start_row][start_col] = board.board[end_row][end_col]
    board.board[end_row][end_col] = captured_piece


def move_leaves_king_in_check(board, start, end):
    """Check whether making a move would leave the moving side's king in check."""

    start_row, start_col = start
    piece = board.board[start_row][start_col]

    if piece is None:
        return True

    captured_piece = make_temporary_move(board, start, end)

    result = is_in_check(board, piece.color)

    undo_temporary_move(
        board,
        start,
        end,
        captured_piece,
    )

    return result


def has_legal_moves(board, color):
    """Check whether a player has at least one legal move."""

    for start_row in range(8):
        for start_col in range(8):
            piece = board.board[start_row][start_col]

            if piece is None or piece.color != color:
                continue

            for end_row in range(8):
                for end_col in range(8):
                    if not is_valid_move(
                        board,
                        (start_row, start_col),
                        (end_row, end_col),
                    ):
                        continue

                    if not move_leaves_king_in_check(
                        board,
                        (start_row, start_col),
                        (end_row, end_col),
                    ):
                        return True

    return False


def is_checkmate(board, color):
    """Check whether a player is checkmated."""

    return (
        is_in_check(board, color)
        and not has_legal_moves(board, color)
    )


def is_stalemate(board, color):
    """Check whether a player is stalemated."""

    return (
        not is_in_check(board, color)
        and not has_legal_moves(board, color)
    )