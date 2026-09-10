from .rules import is_valid_move
from .moves import Move
from .pieces import Pawn, Knight, Bishop, Rook, Queen, King


def _coord_to_square(row, col):
    """Convert an internal board coordinate pair into an algebraic square."""

    return f"{chr(ord('a') + col)}{8 - row}"


def _path_is_clear(board, start, end):
    """Check whether all squares between start and end are empty."""

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
    """Return True when a piece attacks the requested destination square."""

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
    """Check whether a square is attacked by a given color.

    This attack check is geometry-based rather than only delegating to
    is_valid_move(), because pawn attacks are diagonal and can legitimately
    test an empty target square in the attack map.
    """

    for start_row in range(8):
        for start_col in range(8):
            piece = board.board[start_row][start_col]

            if piece is None or piece.color != by_color:
                continue

            if _piece_attacks_square(board, piece, start_row, start_col, row, col):
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


def generate_legal_moves(board, color):
    """Return a list of Move objects that can be legally made by the given side.

    The generator mirrors the board-level legality gate used by the engine:
    basic piece movement must be valid and the null move must not expose the
    side's own king to check.
    """

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

                    # Let the board encode the side-specific castling/en-passant
                    # constraints that the generic movement rules file cannot see.
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
    """Check whether a player has at least one legal move."""

    return len(generate_legal_moves(board, color)) > 0


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