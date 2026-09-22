"""Minimax with alpha-beta pruning: quiescence search at the leaves
(avoids misjudging a position mid-capture-sequence), iterative
deepening with a hint move and persistent ordering heuristics, and
SearchStats for reporting. Uses board.copy() rather than make/undo,
since Board has no incremental undo."""

import time

from .evaluation import evaluate, CHECKMATE_SCORE
from .move_ordering import order_moves, MoveOrderingHeuristics, _captured_piece

# How many time-limited searches check the clock: every Nth node rather
# than every node, since time.time() itself has real overhead at the
# node-per-microsecond rates a deep search reaches.
_CLOCK_CHECK_INTERVAL = 1024


class SearchTimeout(Exception):
    """Raised when a time-limited search's deadline passes mid-search.
    Only iterative_deepening_search catches it, so a partially-searched
    (untrustworthy) deeper iteration is always discarded, never returned."""


class SearchStats:
    """Everything worth reporting about one search call."""

    def __init__(self):
        self.nodes = 0            # alpha_beta_search calls
        self.qnodes = 0           # quiescence_search calls
        self.depth_reached = 0    # deepest fully completed iteration
        self.score = 0            # best score found, in centipawns
        self.time_seconds = 0.0
        self.timed_out = False

    @property
    def total_nodes(self):
        return self.nodes + self.qnodes

    @property
    def nodes_per_second(self):
        if self.time_seconds <= 0:
            return 0
        return int(self.total_nodes / self.time_seconds)

    def __repr__(self):
        flag = ", timed_out" if self.timed_out else ""
        return (
            f"SearchStats(depth={self.depth_reached}, nodes={self.nodes}, "
            f"qnodes={self.qnodes}, score={self.score}, "
            f"time={self.time_seconds:.3f}s{flag})"
        )


def _check_deadline(stats, deadline):
    if deadline is None:
        return
    if stats.total_nodes % _CLOCK_CHECK_INTERVAL == 0 and time.time() >= deadline:
        raise SearchTimeout()


def quiescence_search(board, alpha, beta, maximizing, perspective,
                       heuristics=None, stats=None, deadline=None, depth_limit=6):
    """Extend search through captures/promotions only, until the
    position is quiet or `depth_limit` runs out -- avoids misjudging
    material mid-exchange (e.g. right after a queen takes a pawn)."""
    if stats is None:
        stats = SearchStats()
    _check_deadline(stats, deadline)
    stats.qnodes += 1

    stand_pat = evaluate(board, perspective=perspective)

    color = "white" if maximizing else "black"
    if board.turn == color and board.is_game_over():
        return stand_pat

    if depth_limit <= 0:
        return stand_pat

    # Stand-pat cutoff: the side to move isn't forced to capture, so if
    # just standing still already fails high/low, no capture sequence
    # from here needs to be explored either.
    if maximizing:
        if stand_pat >= beta:
            return beta
        alpha = max(alpha, stand_pat)
    else:
        if stand_pat <= alpha:
            return alpha
        beta = min(beta, stand_pat)

    tactical_moves = [
        move for move in board.get_legal_moves(color)
        if move.promotion or _captured_piece(board, move) is not None
    ]
    if not tactical_moves:
        return stand_pat

    ordered = order_moves(board, tactical_moves, heuristics=heuristics)

    for move in ordered:
        child = board.copy()
        child.make_move(move)
        score = quiescence_search(child, alpha, beta, not maximizing, perspective,
                                   heuristics, stats, deadline, depth_limit - 1)

        if maximizing:
            alpha = max(alpha, score)
        else:
            beta = min(beta, score)

        if beta <= alpha:
            break

    return alpha if maximizing else beta


def alpha_beta_search(board, depth, alpha=float("-inf"), beta=float("inf"), maximizing=True,
                       perspective="white", heuristics=None, ply=0, stats=None,
                       deadline=None, hint_move=None, quiescence_depth=6):
    """Search to `depth` plies, then hand off to quiescence_search at
    the leaves. Returns (best_score, best_move); best_move is None at
    a terminal node."""
    if stats is None:
        stats = SearchStats()
    _check_deadline(stats, deadline)
    stats.nodes += 1

    color = "white" if maximizing else "black"

    if board.turn == color and board.is_game_over():
        return evaluate(board, perspective=perspective), None

    if depth == 0:
        score = quiescence_search(board, alpha, beta, maximizing, perspective,
                                   heuristics, stats, deadline, quiescence_depth)
        return score, None

    legal_moves = board.get_legal_moves(color)
    if not legal_moves:
        return evaluate(board, perspective=perspective), None

    ordered = order_moves(board, legal_moves, heuristics=heuristics, ply=ply, hint_move=hint_move)

    best_move = None

    if maximizing:
        best_score = float("-inf")
        for move in ordered:
            child = board.copy()
            child.make_move(move)
            score, _ = alpha_beta_search(child, depth - 1, alpha, beta, False, perspective,
                                          heuristics, ply + 1, stats, deadline,
                                          quiescence_depth=quiescence_depth)

            if score > best_score:
                best_score = score
                best_move = move
            alpha = max(alpha, score)
            if beta <= alpha:
                if heuristics is not None:
                    heuristics.record_cutoff(move, board, ply, depth)
                break  # beta cutoff: opponent won't let us reach this branch
        return best_score, best_move
    else:
        best_score = float("inf")
        for move in ordered:
            child = board.copy()
            child.make_move(move)
            score, _ = alpha_beta_search(child, depth - 1, alpha, beta, True, perspective,
                                          heuristics, ply + 1, stats, deadline,
                                          quiescence_depth=quiescence_depth)

            if score < best_score:
                best_score = score
                best_move = move
            beta = min(beta, score)
            if beta <= alpha:
                if heuristics is not None:
                    heuristics.record_cutoff(move, board, ply, depth)
                break  # alpha cutoff
        return best_score, best_move


def iterative_deepening_search(board, max_depth, time_limit=None, perspective="white",
                                quiescence_depth=6):
    """Search depth 1, 2, 3, ... up to `max_depth`, sharing move-ordering
    heuristics and a hint move across iterations. If `time_limit`
    (seconds) is exceeded mid-iteration, that iteration's untrustworthy
    partial result is discarded and the last fully completed
    iteration's move is returned instead.

    `perspective` should stay "white" regardless of which side is
    actually moving or which color the AI plays -- maximizing/minimizing
    (derived from board.turn) is what makes the search correct for
    whoever's to move, against one fixed white-relative score. Changing
    perspective together with maximizing double-flips whose good is
    whose (a real bug, not a feature)."""
    maximizing = (board.turn == "white")

    heuristics = MoveOrderingHeuristics()
    stats = SearchStats()
    deadline = None if time_limit is None else time.time() + time_limit

    best_score = evaluate(board, perspective=perspective)
    best_move = None
    start_time = time.time()

    for depth in range(1, max_depth + 1):
        try:
            score, move = alpha_beta_search(
                board, depth, maximizing=maximizing, perspective=perspective,
                heuristics=heuristics, stats=stats, deadline=deadline,
                hint_move=best_move, quiescence_depth=quiescence_depth,
            )
        except SearchTimeout:
            stats.timed_out = True
            break

        if move is not None:
            best_score, best_move = score, move
        stats.depth_reached = depth
        stats.score = best_score

        if abs(best_score) >= CHECKMATE_SCORE - 1000:
            break  # proven forced mate; searching deeper can't improve it

    stats.time_seconds = time.time() - start_time
    return best_score, best_move, stats


def get_top_n_moves(board, depth, n=3, maximizing=True, perspective="white", heuristics=None):
    """Evaluate every legal move one ply plus a full (depth-1)-ply
    search, and return the top `n` as [(score, move), ...], best-first.
    Used by the adaptive AI player to sample instead of always playing
    the single best move."""
    color = "white" if maximizing else "black"
    heuristics = heuristics if heuristics is not None else MoveOrderingHeuristics()
    legal_moves = board.get_legal_moves(color)
    ordered = order_moves(board, legal_moves, heuristics=heuristics)

    scored_moves = []
    for move in ordered:
        child = board.copy()
        child.make_move(move)
        score, _ = alpha_beta_search(child, max(depth - 1, 0), maximizing=not maximizing,
                                      perspective=perspective, heuristics=heuristics)
        scored_moves.append((score, move))

    reverse = maximizing  # maximizing player wants highest scores first
    scored_moves.sort(key=lambda pair: pair[0], reverse=reverse)

    return scored_moves[:n]
