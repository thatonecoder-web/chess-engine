"""
evaluation.py
=============

Static position evaluation: material count + piece-square tables.

ASSUMPTIONS ABOUT YOUR BOARD (adjust to match your actual classes):
- board.squares is an 8x8 structure (row 0 = rank 8 / Black's back rank,
  row 7 = rank 1 / White's back rank) where each square is either None
  (empty) or a piece object with:
    piece.color  -> "white" or "black"
    piece.symbol -> one of "P", "N", "B", "R", "Q", "K" (uppercase, color-agnostic)
- board.is_checkmate(color) -> bool
- board.is_stalemate() -> bool

If your Board/Piece classes are shaped differently, only this file needs
to change — everything else (search, move ordering, AI player) just
calls evaluate(board) and treats it as a black box.
"""

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


def _pst_value(symbol, color, row, col):
    """Look up a piece-square bonus, mirroring the table for Black."""
    table = PIECE_SQUARE_TABLES[symbol]
    if color == "white":
        return table[row][col]
    return table[7 - row][col]


def evaluate(board, perspective="white"):
    """
    Static evaluation of the current position, in centipawns.

    Positive scores favor `perspective`; negative scores favor the
    opponent. This is what alpha_beta_search calls at leaf nodes, and
    what the AI player uses to compare candidate moves.
    """
    if board.is_checkmate("white"):
        score = -CHECKMATE_SCORE
    elif board.is_checkmate("black"):
        score = CHECKMATE_SCORE
    elif board.is_stalemate():
        score = 0
    else:
        score = 0
        for row in range(8):
            for col in range(8):
                piece = board.squares[row][col]
                if piece is None:
                    continue

                material = PIECE_VALUES[piece.symbol]
                positional = _pst_value(piece.symbol, piece.color, row, col)
                value = material + positional

                if piece.color == "white":
                    score += value
                else:
                    score -= value

    return score if perspective == "white" else -score
