"""Bridges the engine's continuous, adaptive skill_estimate (see
difficulty.py) to a short, named list menus can offer. `make_ai_player`
builds an AIPlayer primed with a preset's skill -- still adaptive for
Player vs AI, or pinned via near-zero smoothing for AI vs AI."""

from .ai_player import AIPlayer
from .difficulty import PlayerModel, DifficultyController

# Ordered so menus can present them 0 (weakest) to max (strongest).
LEVELS = [
    ("Beginner", 0.05),
    ("Easy", 0.25),
    ("Medium", 0.5),
    ("Hard", 0.7),
    ("Expert", 0.9),
    ("Maximum", 1.0),
]

LEVEL_NAMES = [name for name, _ in LEVELS]
_LEVEL_MAP = dict(LEVELS)


def level_names():
    """Menu-friendly ordered list of difficulty names."""
    return list(LEVEL_NAMES)


def skill_for_level(name):
    if name not in _LEVEL_MAP:
        raise ValueError(f"Unknown difficulty level: {name!r}")
    return _LEVEL_MAP[name]


def make_ai_player(color, level_name, adaptive=True):
    """Build an AIPlayer for `color` starting at `level_name`'s skill.

    adaptive=True (Player vs AI): normal smoothing, so the AI still
    drifts toward matching how the human is actually playing.

    adaptive=False (AI vs AI, or anywhere there's no human move to
    learn from): a tiny smoothing constant keeps the estimate
    effectively pinned at the chosen level for the whole game.
    """
    skill = skill_for_level(level_name)
    smoothing = 0.2 if adaptive else 0.0001
    model = PlayerModel(smoothing=smoothing, initial_estimate=skill)
    return AIPlayer(color=color, player_model=model, difficulty=DifficultyController())
