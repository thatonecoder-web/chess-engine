"""
ai_player.py
============

Public interface the game loop talks to. Everything adaptive-difficulty
related (skill tracking, depth/noise tuning) is wired together here so
the rest of the engine only ever needs to call:

    ai = AIPlayer(color="black")
    move = ai.choose_move(board)              # AI's turn
    ai.observe_player_move(board_before, move, board_after)  # after human moves

ASSUMPTIONS ABOUT YOUR BOARD/MOVE OBJECTS:
    board.turn -> "white" or "black" (the side to move)
    Move.__eq__/__hash__ compare by (start, end, promotion), so a move
    parsed from human input compares equal to the "same" move returned
    by move generation, even though they're different objects.
"""

import random

from .search import alpha_beta_search, get_top_n_moves, iterative_deepening_search
from .difficulty import PlayerModel, DifficultyController


def estimate_move_quality(board_before, player_move, search_depth=3):
    """
    Compare the move the human actually played against what the
    engine's own search considers best from that same position.

    Returns 0.0-1.0: 1.0 if the player found the engine's top move,
    scaling down toward 0.0 the further their move's resulting eval
    is from the best available eval.
    """
    color = board_before.turn
    maximizing = (color == "white")

    top_moves = get_top_n_moves(board_before, search_depth, n=5, maximizing=maximizing)
    if not top_moves:
        return 0.5  # no data (e.g. only one legal move) -> stay neutral

    best_score = top_moves[0][0]
    worst_score = top_moves[-1][0]
    score_range = abs(best_score - worst_score) or 1  # avoid divide-by-zero

    player_score = None
    for score, move in top_moves:
        if move == player_move:
            player_score = score
            break

    if player_score is None:
        # Player's move wasn't even in the top 5 considered -> treat as
        # the weakest observed quality this turn.
        return 0.0

    # Normalize so the best move -> 1.0, the worst of the top 5 -> 0.0.
    if maximizing:
        quality = (player_score - worst_score) / score_range
    else:
        quality = (worst_score - player_score) / score_range

    return max(0.0, min(1.0, quality))


def weighted_pick(candidates, noise):
    """
    Pick a move from `candidates` (list of (score, move), best-first).

    noise=0.0  -> always pick candidates[0] (the objectively best move)
    noise>0.0  -> increasingly likely to pick a lower-ranked candidate,
                  simulating imperfect play rather than a flat depth cut
    """
    if not candidates:
        return None

    if noise <= 0.0 or len(candidates) == 1:
        return candidates[0][1]

    # Weight earlier (better) candidates higher; noise shifts probability
    # mass toward later (worse) candidates.
    n = len(candidates)
    weights = [max(0.01, (n - i) - noise * i) for i in range(n)]
    total = sum(weights)
    weights = [w / total for w in weights]

    pick = random.choices(candidates, weights=weights, k=1)[0]
    return pick[1]


class AIPlayer:
    """
    Adaptive-difficulty chess AI.

    Rather than a fixed ELO/depth chosen once, this continuously
    re-estimates player skill after every human move and adjusts its
    own search depth and move-selection noise to match, so difficulty
    can rise or fall over the course of a single game.
    """

    def __init__(self, color="black", player_model=None, difficulty=None,
                 quality_check_depth=3):
        self.color = color
        self.player_model = player_model or PlayerModel()
        self.difficulty = difficulty or DifficultyController()
        self.quality_check_depth = quality_check_depth
        # SearchStats from the most recent choose_move call (nodes,
        # depth reached, time spent, ...), or None if the last move was
        # picked from a candidate pool instead (see choose_move below).
        self.last_search_stats = None

    def choose_move(self, board):
        """Select and return the AI's move for the current position."""
        skill = self.player_model.skill_estimate
        depth = self.difficulty.get_depth(skill)
        time_limit = self.difficulty.get_time_limit(skill)
        pool_size = self.difficulty.get_candidate_pool_size(skill)
        noise = self.difficulty.get_move_noise(skill)

        maximizing = (self.color == "white")

        if pool_size <= 1 or noise <= 0.0:
            # At the top of a difficulty level there's no pool to
            # sample from — just play the strongest move iterative
            # deepening finds within this level's time budget.
            #
            # perspective stays "white" (the default) here, NOT
            # self.color: alpha-beta's maximizing/minimizing alternation
            # (derived from whose turn it actually is) is what makes the
            # search correct for whichever side the AI is playing. Fixed
            # white-relative scoring is a fixed measuring stick; tying it
            # to self.color as well would double-flip the sign for Black
            # and hand the AI its own worst moves (this was a real bug,
            # caught by a mate-in-1 the Black AI refused to play).
            _, best_move, stats = iterative_deepening_search(
                board, max_depth=depth, time_limit=time_limit,
            )
            self.last_search_stats = stats
            return best_move

        self.last_search_stats = None
        candidates = get_top_n_moves(board, depth, n=pool_size, maximizing=maximizing)
        return weighted_pick(candidates, noise)

    def observe_player_move(self, board_before, player_move):
        """
        Call this right after the human plays `player_move` from
        `board_before` (i.e. before the move is applied), so the AI
        can score it against its own search and update skill_estimate.
        """
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
