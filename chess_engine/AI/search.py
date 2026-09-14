"""
search.py
=========

Minimax search with alpha-beta pruning, written from scratch (no chess
or search libraries). This is the only place that walks the game tree;
evaluation.py scores leaf positions and move_ordering.py decides what
order to visit children in.

ASSUMPTIONS ABOUT YOUR BOARD (adjust to match your actual Board class):
    board.get_legal_moves(color) -> list[Move]
    board.make_move(move)        -> applies the move in place
    board.undo_move()            -> reverses the last make_move call
    board.is_game_over()         -> bool (checkmate or stalemate)
    board.active_color           -> "white" or "black" (whose turn it is)
"""

from .evaluation import evaluate
from .move_ordering import order_moves


def alpha_beta_search(board, depth, alpha=float("-inf"), beta=float("inf"),
                       maximizing=True, perspective="white"):
    """
    Recursively search to `depth` plies, pruning branches that can't
    affect the final decision.

    Returns (best_score, best_move). best_move is None at depth 0 or on
    terminal nodes, since there's nothing left to choose from there.
    """
    if depth == 0 or board.is_game_over():
        return evaluate(board, perspective=perspective), None

    color = "white" if maximizing else "black"
    legal_moves = order_moves(board, board.get_legal_moves(color))

    if not legal_moves:
        # No legal moves but not caught by is_game_over() above ->
        # treat as a terminal node rather than crashing.
        return evaluate(board, perspective=perspective), None

    best_move = None

    if maximizing:
        best_score = float("-inf")
        for move in legal_moves:
            board.make_move(move)
            score, _ = alpha_beta_search(board, depth - 1, alpha, beta,
                                          maximizing=False, perspective=perspective)
            board.undo_move()

            if score > best_score:
                best_score = score
                best_move = move
            alpha = max(alpha, score)
            if beta <= alpha:
                break  # beta cutoff: opponent won't let us reach this branch
        return best_score, best_move
    else:
        best_score = float("inf")
        for move in legal_moves:
            board.make_move(move)
            score, _ = alpha_beta_search(board, depth - 1, alpha, beta,
                                          maximizing=True, perspective=perspective)
            board.undo_move()

            if score < best_score:
                best_score = score
                best_move = move
            beta = min(beta, score)
            if beta <= alpha:
                break  # alpha cutoff
        return best_score, best_move


def get_top_n_moves(board, depth, n=3, maximizing=True, perspective="white"):
    """
    Evaluate every legal move one ply, each followed by a full
    (depth - 1)-ply search, and return the top `n` as
    [(score, move), ...] sorted best-first.

    This is what the adaptive AI player samples from instead of always
    playing the single best move — see difficulty.py and ai_player.py.
    """
    color = "white" if maximizing else "black"
    legal_moves = order_moves(board, board.get_legal_moves(color))

    scored_moves = []
    for move in legal_moves:
        board.make_move(move)
        score, _ = alpha_beta_search(board, depth - 1,
                                      maximizing=not maximizing,
                                      perspective=perspective)
        board.undo_move()
        scored_moves.append((score, move))

    reverse = maximizing  # maximizing player wants highest scores first
    scored_moves.sort(key=lambda pair: pair[0], reverse=reverse)

    return scored_moves[:n]
