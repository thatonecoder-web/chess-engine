"""
difficulty.py
=============

Adaptive difficulty, as opposed to a fixed ELO/depth selection.

Two pieces:

    PlayerModel
        Tracks a running estimate of how well the human is playing,
        updated after each of their moves.

    DifficultyController
        Maps that skill estimate onto concrete search parameters
        (depth, move-selection noise) that ai_player.py uses when
        choosing its next move.

Nothing here talks to the board directly — it only deals in scores
that evaluation.py and search.py already produced, so it stays
reusable if you ever change how evaluation works.
"""


class PlayerModel:
    """
    Maintains a smoothed 0.0-1.0 estimate of player skill.

    0.0 = playing very weakly (frequent blunders)
    1.0 = playing very strongly (consistently near-optimal moves)

    Uses an exponential moving average so recent moves count more than
    moves from many turns ago — the AI should adapt within a game, not
    just average over its whole history.
    """

    def __init__(self, smoothing=0.2, initial_estimate=0.5):
        if not 0.0 < smoothing <= 1.0:
            raise ValueError("smoothing must be in (0.0, 1.0]")

        self.smoothing = smoothing
        self.skill_estimate = initial_estimate
        self.moves_observed = 0

    def update(self, move_quality):
        """
        move_quality: 0.0 (blunder) to 1.0 (matched the engine's own
        best move). See ai_player.estimate_move_quality for how this
        is computed from actual search results.
        """
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
    """
    Converts a PlayerModel's skill_estimate into concrete search
    parameters: how deep to search, and how much randomness to inject
    into move selection.

    Both scale linearly with skill_estimate by default — tune
    min_depth/max_depth to whatever your hardware can search in an
    acceptable time per move.
    """

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
        """
        Higher skill_estimate -> less noise -> AI plays closer to the
        objectively best move. Lower skill_estimate -> more noise ->
        AI more often picks a good-but-not-best move from the pool.
        """
        return self.max_noise - skill_estimate * (self.max_noise - self.min_noise)

    def get_candidate_pool_size(self, skill_estimate):
        """
        How many top moves to consider sampling from. Kept constant by
        default, but exposed here in case you want, e.g., a bigger
        pool at low skill (more room to pick a mediocre move) and a
        pool of 1 at max skill (always play the engine's best move).
        """
        return self.candidate_pool_size
