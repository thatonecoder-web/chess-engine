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
chess/AI libraries. The adaptive layer sits on top of it in
`difficulty.py`, and `AIPlayer` ties everything together into the
interface the game loop talks to.
"""

from .evaluation import (
    evaluate,
    PIECE_VALUES,
    PIECE_SQUARE_TABLES,
)

from .search import (
    alpha_beta_search,
    get_top_n_moves,
)

from .move_ordering import (
    order_moves,
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
    # search
    "alpha_beta_search",
    "get_top_n_moves",
    # move ordering
    "order_moves",
    # adaptive difficulty
    "PlayerModel",
    "DifficultyController",
    # public interface
    "AIPlayer",
]

__version__ = "0.2.0"
