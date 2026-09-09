from .pieces import Pawn, Knight, Bishop, Rook, Queen, King


def is_valid_move(board, start, end):
    """
    Check whether a piece can legally move from start to end
    based on basic piece movement rules.

    This does NOT check:
    - Check
    - Checkmate
    - Castling
    - En passant
    - Promotion
    """

    start_row, start_col = start
    end_row, end_col = end

    if not (0 <= start_row < 8 and 0 <= start_col < 8):
        return False

    if not (0 <= end_row < 8 and 0 <= end_col < 8):
        return False

    piece = board.board[start_row][start_col]
    target = board.board[end_row][end_col]

    if piece is None:
        return False

    # Cannot capture your own piece
    if target is not None and target.color == piece.color:
        return False

    row_change = end_row - start_row
    col_change = end_col - start_col

    if isinstance(piece, Pawn):
        return _valid_pawn_move(
            board,
            start_row,
            start_col,
            end_row,
            end_col,
            row_change,
            col_change,
            target,
        )

    if isinstance(piece, Knight):
        return (abs(row_change), abs(col_change)) in [(1, 2), (2, 1)]

    if isinstance(piece, Bishop):
        return (
            abs(row_change) == abs(col_change)
            and _path_is_clear(board, start, end)
        )

    if isinstance(piece, Rook):
        return (
            (row_change == 0 or col_change == 0)
            and _path_is_clear(board, start, end)
        )

    if isinstance(piece, Queen):
        is_straight = row_change == 0 or col_change == 0
        is_diagonal = abs(row_change) == abs(col_change)

        return (
            (is_straight or is_diagonal)
            and _path_is_clear(board, start, end)
        )

    if isinstance(piece, King):
        # Castling is handled explicitly by Board.make_move, but the
        # base rule still needs to allow the normal one-square king step.
        if abs(row_change) <= 1 and abs(col_change) <= 1 and not (row_change == 0 and col_change == 0):
            return True
        return False

    return False


def _valid_pawn_move(
    board,
    start_row,
    start_col,
    end_row,
    end_col,
    row_change,
    col_change,
    target,
):
    """Check basic pawn movement and captures, including en passant legality."""

    piece = board.board[start_row][start_col]
    direction = -1 if piece.color == "white" else 1

    # One square forward, vertical only.
    if col_change == 0 and row_change == direction and target is None:
        return True

    # Two squares forward from starting row only when the path is clear.
    starting_row = 6 if piece.color == "white" else 1
    if (
        col_change == 0
        and row_change == 2 * direction
        and start_row == starting_row
        and target is None
    ):
        middle_row = start_row + direction
        return board.board[middle_row][start_col] is None

    # Diagonal capture onto an occupied enemy square.
    if abs(col_change) == 1 and row_change == direction and target is not None:
        return target.color != piece.color

    # En passant is a diagonal capture into an empty square, only when the
    # target square matches the board's remembered en-passant square.
    if abs(col_change) == 1 and row_change == direction and target is None:
        if board.en_passant_target == (end_row, end_col):
            captured = board.board[start_row][end_col]
            return (
                captured is not None
                and isinstance(captured, Pawn)
                and captured.color != piece.color
            )

    return False


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