"""Orders legal moves so search explores the most promising ones
first, which drastically increases alpha-beta pruning without
changing the final result. Priority: hint move, MVV-LVA captures,
promotions, checks, killer moves, history heuristic, then the rest in
generation order (deterministic, so search stays reproducible)."""

from ..core.pieces import Knight, Bishop, Rook, Queen
from .evaluation import PIECE_VALUES

CAPTURE_BASE_SCORE = 1_000_000
PROMOTION_BASE_SCORE = 900_000
CHECK_BONUS = 500_000
KILLER_BASE_SCORE = 400_000
HINT_SCORE = 2_000_000

PROMOTION_VALUES = {"q": 4, "r": 3, "b": 2, "n": 1}

# How many killer moves to remember per ply.
KILLERS_PER_PLY = 2


class MoveOrderingHeuristics:
    """Cross-node search state, shared across one top-level search call
    (see search.py), that lets ordering improve as the search goes:
    killer_moves[ply] (recent cutoff moves at that ply) and
    history[key] (a running, depth-weighted cutoff score per move)."""

    def __init__(self):
        self.killer_moves = {}   # ply -> [move, move]
        self.history = {}        # (color, start, end) -> score

    def record_cutoff(self, move, board, ply, depth):
        """Call when `move` (a non-capture) causes a beta cutoff."""
        if getattr(move, "_is_capture_cache", None):
            return  # captures are already ordered well by MVV-LVA

        killers = self.killer_moves.setdefault(ply, [])
        if move not in killers:
            killers.insert(0, move)
            del killers[KILLERS_PER_PLY:]

        key = (board.turn, move.start, move.end)
        self.history[key] = self.history.get(key, 0) + depth * depth

    def killer_score(self, move, ply):
        killers = self.killer_moves.get(ply)
        if not killers:
            return 0
        try:
            rank = killers.index(move)
        except ValueError:
            return 0
        return KILLER_BASE_SCORE - rank  # first killer scores slightly above the second

    def history_score(self, move, color):
        return self.history.get((color, move.start, move.end), 0)


def _captured_piece(board, move):
    """The piece `move` would capture, or None. Handles en passant,
    where the captured pawn is not on the destination square."""
    end_row, end_col = move.get_coordinates(move.end)
    target = board.board[end_row][end_col]
    if target is not None:
        return target

    start_row, start_col = move.get_coordinates(move.start)
    mover = board.board[start_row][start_col]
    is_pawn = mover is not None and mover.symbol.upper() == "P"
    is_diagonal = start_col != end_col and start_row != end_row
    if is_pawn and is_diagonal and board.en_passant_target == (end_row, end_col):
        return board.board[start_row][end_col]

    return None


def _mvv_lva_score(board, move, captured):
    """Higher score = better capture to try first."""
    start_row, start_col = move.get_coordinates(move.start)
    attacker = board.board[start_row][start_col]

    victim_value = PIECE_VALUES.get(captured.symbol.upper(), 0)
    attacker_value = PIECE_VALUES.get(attacker.symbol.upper(), 0) if attacker else 0

    # Scale victim value up so it dominates the sort; subtract attacker
    # value so among equal victims, the cheaper attacker sorts first.
    return victim_value * 10 - attacker_value


def _gives_direct_check(board, move):
    """
    Cheap (non-simulating) heuristic: would the moved piece, from its
    *destination* square, attack the enemy king given the board as it
    stands right now?

    This intentionally does not detect discovered checks (which would
    require actually making the move) — it's a move-ordering signal,
    not a legality check, so a false negative here only costs a little
    ordering quality, never correctness.
    """
    from ..core.check import find_king, _piece_attacks_square

    start_row, start_col = move.get_coordinates(move.start)
    end_row, end_col = move.get_coordinates(move.end)
    piece = board.board[start_row][start_col]
    if piece is None:
        return False

    opponent = "black" if piece.color == "white" else "white"
    king_pos = find_king(board, opponent)
    if king_pos is None:
        return False

    king_row, king_col = king_pos

    if move.promotion:
        promo_symbol = move.promotion.upper() if piece.color == "white" else move.promotion.lower()
        piece_cls_map = {"N": Knight, "B": Bishop, "R": Rook, "Q": Queen}
        piece = piece_cls_map.get(move.promotion.upper(), type(piece))(promo_symbol, piece.color)

    return _piece_attacks_square(board, piece, end_row, end_col, king_row, king_col)


def order_moves(board, moves, heuristics=None, ply=0, hint_move=None):
    """Return `moves` sorted best-first. `heuristics`/`ply` are optional
    (falls back to captures/promotions/checks-only ordering without
    them); `hint_move`, if given, is always tried first."""

    def sort_key(move):
        if hint_move is not None and move == hint_move:
            return HINT_SCORE

        score = 0

        captured = _captured_piece(board, move)
        move._is_capture_cache = captured is not None
        if captured is not None:
            score += CAPTURE_BASE_SCORE + _mvv_lva_score(board, move, captured)

        if move.promotion:
            score += PROMOTION_BASE_SCORE + PROMOTION_VALUES.get(move.promotion.lower(), 0)

        if _gives_direct_check(board, move):
            score += CHECK_BONUS

        if heuristics is not None:
            score += heuristics.killer_score(move, ply)
            score += heuristics.history_score(move, board.turn)

        return score

    return sorted(moves, key=sort_key, reverse=True)
