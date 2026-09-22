"""Public AI interface: `AIPlayer.choose_move(board)` and
`AIPlayer.observe_player_move(board_before, move)`, with adaptive
difficulty (skill tracking, depth/noise tuning) wired together here."""

import random

from .search import alpha_beta_search, get_top_n_moves, iterative_deepening_search
from .difficulty import PlayerModel, DifficultyController


def estimate_move_quality(board_before, player_move, search_depth=3):
    """How good was `player_move`? 1.0 = engine's top choice, scaling
    down to 0.0 for the weakest of its top 5 candidates."""
    color = board_before.turn
    maximizing = (color == "white")

    top_moves = get_top_n_moves(board_before, search_depth, n=5, maximizing=maximizing)
    if not top_moves:
        return 0.5  # only one legal move available; stay neutral

    best_score = top_moves[0][0]
    worst_score = top_moves[-1][0]
    score_range = abs(best_score - worst_score) or 1

    player_score = None
    for score, move in top_moves:
        if move == player_move:
            player_score = score
            break

    if player_score is None:
        return 0.0  # not even in the top 5 considered

    if maximizing:
        quality = (player_score - worst_score) / score_range
    else:
        quality = (worst_score - player_score) / score_range

    return max(0.0, min(1.0, quality))


def weighted_pick(candidates, noise):
    """Pick from `candidates` (best-first). noise=0.0 always picks the
    best; higher noise increasingly favors lower-ranked candidates."""
    if not candidates:
        return None

    if noise <= 0.0 or len(candidates) == 1:
        return candidates[0][1]

    n = len(candidates)
    weights = [max(0.01, (n - i) - noise * i) for i in range(n)]
    total = sum(weights)
    weights = [w / total for w in weights]

    pick = random.choices(candidates, weights=weights, k=1)[0]
    return pick[1]


class AIPlayer:
    """Adaptive-difficulty chess AI: re-estimates player skill after
    every human move and adjusts its own search depth/noise to match."""

    def __init__(self, color="black", player_model=None, difficulty=None,
                 quality_check_depth=3):
        self.color = color
        self.player_model = player_model or PlayerModel()
        self.difficulty = difficulty or DifficultyController()
        self.quality_check_depth = quality_check_depth
        self.last_search_stats = None  # None when the last move came from a candidate pool, not a full search

    def choose_move(self, board):
        """Select and return the AI's move for the current position."""
        skill = self.player_model.skill_estimate
        depth = self.difficulty.get_depth(skill)
        time_limit = self.difficulty.get_time_limit(skill)
        pool_size = self.difficulty.get_candidate_pool_size(skill)
        noise = self.difficulty.get_move_noise(skill)

        maximizing = (self.color == "white")

        if pool_size <= 1 or noise <= 0.0:
            # Top of a difficulty level: play the strongest move found.
            # perspective stays "white" here, NOT self.color -- scores
            # are always white-relative; maximizing/minimizing already
            # handles whose turn it is. Tying perspective to self.color
            # too double-flips the sign for Black (a real bug once: the
            # Black AI refused an available mate-in-1).
            _, best_move, stats = iterative_deepening_search(
                board, max_depth=depth, time_limit=time_limit,
            )
            self.last_search_stats = stats
            return best_move

        self.last_search_stats = None
        candidates = get_top_n_moves(board, depth, n=pool_size, maximizing=maximizing)
        return weighted_pick(candidates, noise)

    def observe_player_move(self, board_before, player_move):
        """Call right after a human plays `player_move` from `board_before`
        (pre-move state) to score it and update the skill estimate."""
        quality = estimate_move_quality(board_before, player_move,
                                         search_depth=self.quality_check_depth)
        self.player_model.update(quality)

    def reset(self):
        """Call at the start of a new game."""
        self.player_model.reset()

    @property
    def current_skill_estimate(self):
        return self.player_model.skill_estimate

    @property
    def current_depth(self):
        return self.difficulty.get_depth(self.player_model.skill_estimate)
