"""Static position evaluation, in centipawns, from White's perspective
before the final `perspective` flip. Terms: material, piece-square
tables, pawn structure (doubled/isolated/passed), king safety, center
control, and development (tapered out past the opening)."""

from ..core.check import is_square_attacked, find_king, is_in_check, has_legal_moves

# Standard material values, in centipawns.
PIECE_VALUES = {
    "P": 100,
    "N": 320,
    "B": 330,
    "R": 500,
    "Q": 900,
    "K": 0,  # king's value isn't material-relevant; checkmate is handled separately
}

# Piece-square tables: bonus/penalty per square, from White's perspective
# (row 0 = rank 8, row 7 = rank 1). For Black, the table is read mirrored
# vertically (see _pst_value below).
PIECE_SQUARE_TABLES = {
    "P": [
        [0,  0,  0,  0,  0,  0,  0,  0],
        [50, 50, 50, 50, 50, 50, 50, 50],
        [10, 10, 20, 30, 30, 20, 10, 10],
        [5,  5, 10, 25, 25, 10,  5,  5],
        [0,  0,  0, 20, 20,  0,  0,  0],
        [5, -5,-10,  0,  0,-10, -5,  5],
        [5, 10, 10,-20,-20, 10, 10,  5],
        [0,  0,  0,  0,  0,  0,  0,  0],
    ],
    "N": [
        [-50,-40,-30,-30,-30,-30,-40,-50],
        [-40,-20,  0,  0,  0,  0,-20,-40],
        [-30,  0, 10, 15, 15, 10,  0,-30],
        [-30,  5, 15, 20, 20, 15,  5,-30],
        [-30,  0, 15, 20, 20, 15,  0,-30],
        [-30,  5, 10, 15, 15, 10,  5,-30],
        [-40,-20,  0,  5,  5,  0,-20,-40],
        [-50,-40,-30,-30,-30,-30,-40,-50],
    ],
    "B": [
        [-20,-10,-10,-10,-10,-10,-10,-20],
        [-10,  0,  0,  0,  0,  0,  0,-10],
        [-10,  0,  5, 10, 10,  5,  0,-10],
        [-10,  5,  5, 10, 10,  5,  5,-10],
        [-10,  0, 10, 10, 10, 10,  0,-10],
        [-10, 10, 10, 10, 10, 10, 10,-10],
        [-10,  5,  0,  0,  0,  0,  5,-10],
        [-20,-10,-10,-10,-10,-10,-10,-20],
    ],
    "R": [
        [0,  0,  0,  0,  0,  0,  0,  0],
        [5, 10, 10, 10, 10, 10, 10,  5],
        [-5,  0,  0,  0,  0,  0,  0, -5],
        [-5,  0,  0,  0,  0,  0,  0, -5],
        [-5,  0,  0,  0,  0,  0,  0, -5],
        [-5,  0,  0,  0,  0,  0,  0, -5],
        [-5,  0,  0,  0,  0,  0,  0, -5],
        [0,  0,  0,  5,  5,  0,  0,  0],
    ],
    "Q": [
        [-20,-10,-10, -5, -5,-10,-10,-20],
        [-10,  0,  0,  0,  0,  0,  0,-10],
        [-10,  0,  5,  5,  5,  5,  0,-10],
        [-5,  0,  5,  5,  5,  5,  0, -5],
        [0,  0,  5,  5,  5,  5,  0, -5],
        [-10,  5,  5,  5,  5,  5,  0,-10],
        [-10,  0,  5,  0,  0,  0,  0,-10],
        [-20,-10,-10, -5, -5,-10,-10,-20],
    ],
    "K": [
        [-30,-40,-40,-50,-50,-40,-40,-30],
        [-30,-40,-40,-50,-50,-40,-40,-30],
        [-30,-40,-40,-50,-50,-40,-40,-30],
        [-30,-40,-40,-50,-50,-40,-40,-30],
        [-20,-30,-30,-40,-40,-30,-30,-20],
        [-10,-20,-20,-20,-20,-20,-20,-10],
        [20, 20,  0,  0,  0,  0, 20, 20],
        [20, 30, 10,  0,  0, 10, 30, 20],
    ],
}

CHECKMATE_SCORE = 100_000

# The four central squares (d4, e4, d5, e5), as (row, col).
CENTER_SQUARES = [(3, 3), (3, 4), (4, 3), (4, 4)]

CENTER_OCCUPATION_BONUS = 15
CENTER_ATTACK_BONUS = 5

# Knights/bishops sitting on their starting square when it's no longer
# early game get a small penalty to encourage getting pieces out.
DEVELOPMENT_PENALTY = 12
HOME_SQUARES = {
    "white": {"N": [(7, 1), (7, 6)], "B": [(7, 2), (7, 5)]},
    "black": {"N": [(0, 1), (0, 6)], "B": [(0, 2), (0, 5)]},
}
# Development only matters before ~10 minor/major pieces have been
# traded off; past that the game is no longer "early".
DEVELOPMENT_PHASE_MATERIAL_THRESHOLD = 6_000

DOUBLED_PAWN_PENALTY = 15
ISOLATED_PAWN_PENALTY = 12
PASSED_PAWN_BONUS = [0, 15, 25, 40, 60, 90, 130, 0]  # indexed by ranks advanced

KING_SHIELD_BONUS = 10        # per friendly pawn on the 3 squares in front of the king
KING_OPEN_FILE_PENALTY = 20   # king on a file with no friendly pawn on it at all


def _pst_value(symbol, color, row, col):
    """Look up a piece-square bonus, mirroring the table for Black."""
    table = PIECE_SQUARE_TABLES[symbol]
    if color == "white":
        return table[row][col]
    return table[7 - row][col]


def _iter_pieces(board):
    """Yield (row, col, piece) for every occupied square."""
    for row in range(8):
        for col in range(8):
            piece = board.board[row][col]
            if piece is not None:
                yield row, col, piece


def _material_and_pst(board):
    """Material + piece-square score, and total material on the board
    (used to gate the development term to the early game)."""
    score = 0
    total_material = 0

    for row, col, piece in _iter_pieces(board):
        kind = piece.symbol.upper()
        material = PIECE_VALUES[kind]
        positional = _pst_value(kind, piece.color, row, col)
        value = material + positional

        total_material += material
        score += value if piece.color == "white" else -value

    return score, total_material


def _center_control(board):
    """Bonus for occupying or attacking the four center squares."""
    score = 0
    for row, col in CENTER_SQUARES:
        piece = board.board[row][col]
        if piece is not None:
            score += CENTER_OCCUPATION_BONUS if piece.color == "white" else -CENTER_OCCUPATION_BONUS

        if is_square_attacked(board, row, col, "white"):
            score += CENTER_ATTACK_BONUS
        if is_square_attacked(board, row, col, "black"):
            score -= CENTER_ATTACK_BONUS

    return score


def _development(board, total_material):
    """Penalize minor pieces still sitting on their home square once
    the game is past its opening phase."""
    if total_material < DEVELOPMENT_PHASE_MATERIAL_THRESHOLD:
        return 0  # too much material has already been traded; not "early" anymore

    score = 0
    for color, squares_by_kind in HOME_SQUARES.items():
        sign = 1 if color == "white" else -1
        for kind, squares in squares_by_kind.items():
            expected_symbol = kind if color == "white" else kind.lower()
            for row, col in squares:
                piece = board.board[row][col]
                if piece is not None and piece.symbol == expected_symbol:
                    score -= sign * DEVELOPMENT_PENALTY

    return score


def _pawn_files(board, color):
    """Map file -> sorted list of ranks (rows) occupied by `color`'s pawns."""
    files = {}
    symbol = "P" if color == "white" else "p"
    for row, col, piece in _iter_pieces(board):
        if piece.symbol == symbol:
            files.setdefault(col, []).append(row)
    return files


def _is_passed(color, col, most_advanced_row, other_files):
    """No enemy pawn on this file or an adjacent file that's still
    ahead of our most-advanced pawn on this file."""
    for check_col in (col - 1, col, col + 1):
        for enemy_row in other_files.get(check_col, []):
            blocking = (
                enemy_row < most_advanced_row
                if color == "white"
                else enemy_row > most_advanced_row
            )
            if blocking:
                return False
    return True


def _pawn_structure(board):
    """Doubled, isolated, and passed pawn terms."""
    score = 0
    white_files = _pawn_files(board, "white")
    black_files = _pawn_files(board, "black")

    for color, files, other_files, sign in (
        ("white", white_files, black_files, 1),
        ("black", black_files, white_files, -1),
    ):
        for col, rows in files.items():
            # Doubled: more than one pawn of the same color on a file.
            if len(rows) > 1:
                score -= sign * DOUBLED_PAWN_PENALTY * (len(rows) - 1)

            # Isolated: no friendly pawn on an adjacent file.
            if (col - 1) not in files and (col + 1) not in files:
                score -= sign * ISOLATED_PAWN_PENALTY

            # Passed pawn bonus, scaled by how far it's advanced.
            most_advanced_row = min(rows) if color == "white" else max(rows)
            if _is_passed(color, col, most_advanced_row, other_files):
                ranks_advanced = (
                    6 - most_advanced_row if color == "white" else most_advanced_row - 1
                )
                ranks_advanced = max(0, min(7, ranks_advanced))
                score += sign * PASSED_PAWN_BONUS[ranks_advanced]

    return score


def _king_safety(board):
    """Reward a pawn shield in front of the king; penalize a king stuck
    on a file with no friendly pawn on it at all."""
    score = 0
    for color, sign, shield_row_offset in (("white", 1, -1), ("black", -1, 1)):
        king_pos = find_king(board, color)
        if king_pos is None:
            continue

        king_row, king_col = king_pos
        pawn_symbol = "P" if color == "white" else "p"

        shield_row = king_row + shield_row_offset
        if 0 <= shield_row < 8:
            for col in (king_col - 1, king_col, king_col + 1):
                if 0 <= col < 8:
                    square = board.board[shield_row][col]
                    if square is not None and square.symbol == pawn_symbol:
                        score += sign * KING_SHIELD_BONUS

        has_file_pawn = any(
            board.board[r][king_col] is not None
            and board.board[r][king_col].symbol == pawn_symbol
            for r in range(8)
        )
        if not has_file_pawn:
            score -= sign * KING_OPEN_FILE_PENALTY

    return score


def evaluate(board, perspective="white"):
    """Static evaluation in centipawns; positive favors `perspective`.
    Called by alpha_beta_search at leaf nodes."""
    # Checking legal moves once here (rather than via is_checkmate() and
    # is_stalemate() separately, which would each regenerate them) keeps
    # this cheap enough to call at every leaf node.
    side_to_move = board.turn
    in_check = is_in_check(board, side_to_move)
    if in_check and not has_legal_moves(board, side_to_move):
        score = -CHECKMATE_SCORE if side_to_move == "white" else CHECKMATE_SCORE
    elif not in_check and not has_legal_moves(board, side_to_move):
        score = 0
    else:
        material_pst, total_material = _material_and_pst(board)
        score = (
            material_pst
            + _pawn_structure(board)
            + _king_safety(board)
            + _center_control(board)
            + _development(board, total_material)
        )

    return score if perspective == "white" else -score
