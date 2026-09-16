"""
chess_engine.ai
================

From-scratch chess AI with adaptive difficulty.

Unlike a fixed ELO/depth selector, this module tracks how the human
player is actually performing move-to-move (via `PlayerModel`) and
continuously retunes the engine's own search depth and move-selection
noise (via `DifficultyController`) to match, rather than picking a
static strength up front.

Core search (`alpha_beta_search`, `evaluate`, `order_moves`) is plain
minimax with alpha-beta pruning, written from scratch with no external
chess/AI libraries, extended with quiescence search (avoids the
horizon effect on captures) and iterative deepening with time
management (`iterative_deepening_search`) so the engine always returns
a legal move within a time budget rather than a fixed, possibly very
slow, depth. The adaptive layer sits on top of it in `difficulty.py`,
and `AIPlayer` ties everything together into the interface the game
loop talks to.
"""

from .evaluation import (
    evaluate,
    PIECE_VALUES,
    PIECE_SQUARE_TABLES,
    CHECKMATE_SCORE,
)

from .search import (
    alpha_beta_search,
    quiescence_search,
    iterative_deepening_search,
    get_top_n_moves,
    SearchStats,
    SearchTimeout,
)

from .move_ordering import (
    order_moves,
    MoveOrderingHeuristics,
)

from .difficulty import (
    PlayerModel,
    DifficultyController,
)

from .ai_player import (
    AIPlayer,
)

__all__ = [
    # evaluation
    "evaluate",
    "PIECE_VALUES",
    "PIECE_SQUARE_TABLES",
    "CHECKMATE_SCORE",
    # search
    "alpha_beta_search",
    "quiescence_search",
    "iterative_deepening_search",
    "get_top_n_moves",
    "SearchStats",
    "SearchTimeout",
    # move ordering
    "order_moves",
    "MoveOrderingHeuristics",
    # adaptive difficulty
    "PlayerModel",
    "DifficultyController",
    # public interface
    "AIPlayer",
]

__version__ = "0.2.5"
