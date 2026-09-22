"""From-scratch chess AI with adaptive difficulty: alpha-beta search
with quiescence and iterative deepening (search.py, evaluation.py,
move_ordering.py), a skill estimate that adjusts strength to match the
human player (difficulty.py), and AIPlayer as the interface the game
loop talks to (ai_player.py)."""

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
