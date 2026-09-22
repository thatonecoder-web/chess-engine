"""Adaptive difficulty: PlayerModel tracks a running skill estimate
from the human's moves; DifficultyController maps that estimate onto
concrete search parameters (depth, noise) for ai_player.py. Neither
talks to the board directly -- both work from scores already produced
by evaluation.py/search.py."""


class PlayerModel:
    """A smoothed 0.0 (weak/blundering) - 1.0 (near-optimal) estimate
    of player skill, via an exponential moving average so recent moves
    count more than moves from many turns ago."""

    def __init__(self, smoothing=0.2, initial_estimate=0.5):
        if not 0.0 < smoothing <= 1.0:
            raise ValueError("smoothing must be in (0.0, 1.0]")

        self.smoothing = smoothing
        self.skill_estimate = initial_estimate
        self.moves_observed = 0

    def update(self, move_quality):
        """move_quality: 0.0 (blunder) to 1.0 (matched the engine's own
        best move) -- see ai_player.estimate_move_quality."""
        move_quality = max(0.0, min(1.0, move_quality))
        self.skill_estimate = (
            self.smoothing * move_quality
            + (1 - self.smoothing) * self.skill_estimate
        )
        self.moves_observed += 1

    def reset(self, initial_estimate=0.5):
        """Call at the start of a new game so skill from a previous
        game doesn't carry over."""
        self.skill_estimate = initial_estimate
        self.moves_observed = 0


class DifficultyController:
    """Converts a skill_estimate into concrete search parameters
    (depth, move-selection noise), scaling linearly by default."""

    def __init__(self, min_depth=1, max_depth=6,
                 min_noise=0.0, max_noise=0.4,
                 candidate_pool_size=3,
                 min_time_limit=1.0, max_time_limit=8.0):
        self.min_depth = min_depth
        self.max_depth = max_depth
        self.min_noise = min_noise
        self.max_noise = max_noise
        self.candidate_pool_size = candidate_pool_size
        self.min_time_limit = min_time_limit
        self.max_time_limit = max_time_limit

    def get_depth(self, skill_estimate):
        """Higher skill_estimate -> deeper search -> stronger play.

        This is a CEILING passed to iterative deepening as `max_depth`,
        not a fixed depth the search always reaches — get_time_limit()
        below is what actually decides how far iterative deepening gets
        to go before it has to return its best move so far.
        """
        depth = self.min_depth + skill_estimate * (self.max_depth - self.min_depth)
        return round(depth)

    def get_time_limit(self, skill_estimate):
        """Seconds of "thinking time" for one move's iterative-deepening
        search. Higher skill_estimate -> more time -> deeper in practice,
        since get_depth()'s ceiling is rarely reached at low depths but
        the search still has to stop somewhere against a strong player.
        """
        return self.min_time_limit + skill_estimate * (self.max_time_limit - self.min_time_limit)

    def get_move_noise(self, skill_estimate):
        """Higher skill -> less noise -> closer to the objectively
        best move; lower skill -> more likely to pick a good-but-not-
        best move from the pool."""
        return self.max_noise - skill_estimate * (self.max_noise - self.min_noise)

    def get_candidate_pool_size(self, skill_estimate):
        """How many top moves to sample from. Constant by default, but
        exposed for e.g. a bigger pool at low skill and 1 at max."""
        return self.candidate_pool_size
