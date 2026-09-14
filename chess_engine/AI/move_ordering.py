"""
move_ordering.py
=================

Orders a list of legal moves so the search explores the most promising
ones first. Good ordering doesn't change the final result of alpha-beta,
but it drastically increases how much of the tree gets pruned, since a
strong move found early tightens alpha/beta sooner.

Priority (highest first):
    1. Captures, ranked by MVV-LVA (Most Valuable Victim, Least Valuable
       Attacker) — e.g. capturing a queen with a pawn ranks above
       capturing a pawn with a queen.
    2. Moves that give check.
    3. Everything else, in whatever order they were generated.

ASSUMPTIONS ABOUT YOUR MOVE OBJECT (adjust to match your Move class):
    move.captured_piece -> piece object or None
    move.gives_check    -> bool (optional; safe to omit, see below)
    move.piece          -> the piece being moved
"""

from .evaluation import PIECE_VALUES


def _mvv_lva_score(move):
    """Higher score = better capture to try first."""
    victim = getattr(move, "captured_piece", None)
    attacker = getattr(move, "piece", None)

    if victim is None:
        return 0

    victim_value = PIECE_VALUES.get(victim.symbol, 0)
    attacker_value = PIECE_VALUES.get(attacker.symbol, 0) if attacker else 0

    # Scale victim value up so it dominates the sort; subtract attacker
    # value so among equal victims, the cheaper attacker sorts first.
    return victim_value * 10 - attacker_value


def order_moves(board, moves):
    """
    Return `moves` sorted best-first for alpha-beta search.

    `board` is accepted (and unused directly here) so this function's
    signature can grow later — e.g. incorporating a transposition-table
    "best move from last search" hint — without changing every call site.
    """

    def sort_key(move):
        score = 0

        if getattr(move, "captured_piece", None) is not None:
            score += 100_000 + _mvv_lva_score(move)

        if getattr(move, "gives_check", False):
            score += 10_000

        return score

    return sorted(moves, key=sort_key, reverse=True)
