from .rules import is_valid_move
from .moves import Move
from .pieces import Pawn, Knight, Bishop, Rook, Queen, King


def _coord_to_square(row, col):
    return f"{chr(ord('a') + col)}{8 - row}"


def _path_is_clear(board, start, end):
    start_row, start_col = start
    end_row, end_col = end

    row_step = 0
    col_step = 0

    if end_row > start_row:
        row_step = 1
    elif end_row < start_row:
        row_step = -1

    if end_col > start_col:
        col_step = 1
    elif end_col < start_col:
        col_step = -1

    if row_step == 0 and col_step == 0:
        return True

    current_row = start_row + row_step
    current_col = start_col + col_step

    while (current_row, current_col) != (end_row, end_col):
        if board.board[current_row][current_col] is not None:
            return False

        current_row += row_step
        current_col += col_step

    return True


def _piece_attacks_square(board, piece, start_row, start_col, target_row, target_col):
    row_change = target_row - start_row
    col_change = target_col - start_col

    if isinstance(piece, Pawn):
        direction = -1 if piece.color == "white" else 1
        return row_change == direction and abs(col_change) == 1

    if isinstance(piece, Knight):
        return (abs(row_change), abs(col_change)) in [(1, 2), (2, 1)]

    if isinstance(piece, Bishop):
        if abs(row_change) != abs(col_change):
            return False
        return _path_is_clear(board, (start_row, start_col), (target_row, target_col))

    if isinstance(piece, Rook):
        if not (row_change == 0 or col_change == 0):
            return False
        return _path_is_clear(board, (start_row, start_col), (target_row, target_col))

    if isinstance(piece, Queen):
        straight = (row_change == 0 or col_change == 0)
        diagonal = abs(row_change) == abs(col_change)
        if not (straight or diagonal):
            return False
        return _path_is_clear(board, (start_row, start_col), (target_row, target_col))

    if isinstance(piece, King):
        return max(abs(row_change), abs(col_change)) == 1

    return False


def find_king(board, color):
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
    """Geometry-based rather than delegating to is_valid_move(), since
    pawn attacks are diagonal and can target an empty square."""
    for start_row in range(8):
        for start_col in range(8):
            piece = board.board[start_row][start_col]

            if piece is None or piece.color != by_color:
                continue

            if _piece_attacks_square(board, piece, start_row, start_col, row, col):
                return True

    return False


def is_in_check(board, color):
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
    """Make a move directly on the grid (no legality checks) and return
    whatever was on the destination square, for check-detection use."""
    start_row, start_col = start
    end_row, end_col = end

    captured_piece = board.board[end_row][end_col]

    board.board[end_row][end_col] = board.board[start_row][start_col]
    board.board[start_row][start_col] = None

    return captured_piece


def undo_temporary_move(board, start, end, captured_piece):
    start_row, start_col = start
    end_row, end_col = end

    board.board[start_row][start_col] = board.board[end_row][end_col]
    board.board[end_row][end_col] = captured_piece


def move_leaves_king_in_check(board, start, end):
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


def generate_legal_moves(board, color):
    """All legal Move objects for `color`: basic movement must be valid
    and the move must not leave that side's own king in check."""
    moves = []

    for start_row in range(8):
        for start_col in range(8):
            piece = board.board[start_row][start_col]

            if piece is None or piece.color != color:
                continue

            for end_row in range(8):
                for end_col in range(8):
                    start = (start_row, start_col)
                    end = (end_row, end_col)

                    if not is_valid_move(board, start, end):
                        continue

                    # castling/en passant legality is board-specific and
                    # not visible to the generic movement rules above
                    move = Move(_coord_to_square(start_row, start_col), _coord_to_square(end_row, end_col))

                    if isinstance(piece, King) and abs(end_col - start_col) == 2:
                        if not board._can_castle(move):
                            continue

                    if (
                        isinstance(piece, Pawn)
                        and end_row != start_row
                        and abs(end_col - start_col) == 1
                        and board.board[end_row][end_col] is None
                    ):
                        if board.en_passant_target != (end_row, end_col):
                            continue

                    if move_leaves_king_in_check(board, start, end):
                        continue

                    moves.append(move)

    return moves


def has_legal_moves(board, color):
    return len(generate_legal_moves(board, color)) > 0


def is_checkmate(board, color):
    return (
        is_in_check(board, color)
        and not has_legal_moves(board, color)
    )


def is_stalemate(board, color):
    return (
        not is_in_check(board, color)
        and not has_legal_moves(board, color)
    )