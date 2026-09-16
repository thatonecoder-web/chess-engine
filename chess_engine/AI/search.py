"""
search.py
=========

Minimax with alpha-beta pruning, plus the pieces needed to make that
practical at real playing strength:

    - quiescence_search        extends search through captures/promotions
                                at leaf nodes so the engine doesn't stop
                                mid-exchange and misjudge the position
                                (the "horizon effect")
    - iterative_deepening_search
                                searches depth 1, then 2, then 3, ...,
                                reusing each pass's best move to order
                                the next (and giving the engine a legal
                                move to fall back on if it runs out of
                                time partway through a deeper pass)
    - SearchStats               nodes/qnodes/depth/score/time, so the
                                game loop or a benchmark can report on
                                what the search actually did

Board copies (board.copy()) are used instead of a make/undo pair,
since Board has no incremental undo — see Board.copy()'s docstring for
why a shallow grid copy wouldn't be safe here.
"""

import time

from .evaluation import evaluate, CHECKMATE_SCORE
from .move_ordering import order_moves, MoveOrderingHeuristics, _captured_piece

# How many time-limited searches check the clock: every Nth node rather
# than every node, since time.time() itself has real overhead at the
# node-per-microsecond rates a deep search reaches.
_CLOCK_CHECK_INTERVAL = 1024


class SearchTimeout(Exception):
    """Raised when a time-limited search's deadline passes mid-search.

    Only iterative_deepening_search catches this; alpha_beta_search and
    quiescence_search let it propagate all the way up so a partially
    searched (and therefore untrustworthy) deeper iteration is always
    discarded rather than accidentally returned.
    """


class SearchStats:
    """Everything worth reporting about one search call."""

    def __init__(self):
        self.nodes = 0            # alpha_beta_search calls
        self.qnodes = 0           # quiescence_search calls
        self.depth_reached = 0    # deepest FULLY completed iteration
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
    """
    Extend search past the nominal depth limit through captures and
    promotions only, until the position is "quiet" (no more tactical
    shots available) or `depth_limit` is exhausted.

    Without this, alpha_beta_search would statically evaluate a
    position mid-capture-sequence (e.g. right after a queen takes a
    pawn but before the recapture), badly misjudging material.
    """
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
    """
    Recursively search to `depth` plies, pruning branches that can't
    affect the final decision, then handing off to quiescence_search at
    the leaves so tactical sequences aren't cut off mid-exchange.

    Returns (best_score, best_move). best_move is None at a terminal
    node, since there's nothing left to choose from there.
    """
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
        # No legal moves but not caught by is_game_over() above (e.g.
        # it's not actually this color's turn on `board`) -> treat as
        # a terminal node rather than crashing.
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
    """
    Search depth 1, then 2, then 3, ..., up to `max_depth`.

    Two things make this more than "the same search, run redundantly
    at each depth first":
      - Killer moves and the history table (via a single shared
        MoveOrderingHeuristics) persist across iterations, so ordering
        keeps improving instead of starting cold each depth.
      - Each iteration's best move is passed to the next as a `hint`,
        so the move that was best a moment ago gets tried (and usually
        confirmed, cheaply) first at the next depth.

    If `time_limit` (seconds) is given and is exceeded mid-iteration,
    the partially-searched deeper iteration is discarded — its score
    isn't trustworthy, since alpha-beta was cut off before considering
    every move at the root — and the last *fully completed* iteration's
    move is returned instead. This is the search's time-management: it
    always returns a legal move (as long as at least depth 1 completed)
    no matter how tight the time budget is.

    IMPORTANT: `perspective` should stay "white" for normal play (the
    default) regardless of which color is actually on the move or which
    color the AI is playing. `maximizing`/`minimizing` (derived below
    from board.turn) is what makes the search correct for whichever
    side is actually to move — every score is still measured on one
    fixed white-relative scale. Passing a different perspective changes
    what a returned *score* means for display purposes, but doing so
    together with `maximizing` would double-flip whose good is whose,
    which is a real bug, not a feature — leave it as "white" unless you
    specifically need a black-relative score AND know maximizing/
    minimizing must NOT also be flipped to compensate.
    """
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

        # A proven forced mate can't be improved on by searching deeper.
        if abs(best_score) >= CHECKMATE_SCORE - 1000:
            break

    stats.time_seconds = time.time() - start_time
    return best_score, best_move, stats


def get_top_n_moves(board, depth, n=3, maximizing=True, perspective="white", heuristics=None):
    """
    Evaluate every legal move one ply, each followed by a full
    (depth - 1)-ply search, and return the top `n` as
    [(score, move), ...] sorted best-first.

    This is what the adaptive AI player samples from instead of always
    playing the single best move — see difficulty.py and ai_player.py.
    """
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
