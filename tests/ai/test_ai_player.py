"""Tests for AI/ai_player.py."""

from chess_engine.core.board import Board
from chess_engine.ai.ai_player import AIPlayer, estimate_move_quality, weighted_pick
from chess_engine.ai.difficulty import PlayerModel, DifficultyController


class TestAIPlayerChoosesLegalMoves:
    def test_white_ai_returns_legal_move(self):
        board = Board()
        difficulty = DifficultyController(min_depth=1, max_depth=2,
                                           min_time_limit=0.5, max_time_limit=1.0)
        ai = AIPlayer(color="white", difficulty=difficulty)
        move = ai.choose_move(board)
        legal = {(m.start, m.end) for m in board.get_legal_moves("white")}
        assert (move.start, move.end) in legal

    def test_black_ai_returns_legal_move(self):
        board = Board()
        board.make_move(board.get_legal_moves("white")[0])
        difficulty = DifficultyController(min_depth=1, max_depth=2,
                                           min_time_limit=0.5, max_time_limit=1.0)
        ai = AIPlayer(color="black", difficulty=difficulty)
        move = ai.choose_move(board)
        legal = {(m.start, m.end) for m in board.get_legal_moves("black")}
        assert (move.start, move.end) in legal

    def test_black_ai_takes_an_available_mate(self):
        # Regression test: an earlier bug tied search "perspective" to
        # the AI's own color, which caused a Black-playing AI to avoid
        # a mate it should have taken.
        board = Board()
        board.from_fen("rnbqkbnr/pppp1ppp/8/4p3/6P1/5P2/PPPPP2P/RNBQKBNR b KQkq - 0 2")
        difficulty = DifficultyController(min_depth=1, max_depth=1,
                                           min_time_limit=1.0, max_time_limit=1.0,
                                           candidate_pool_size=1)
        ai = AIPlayer(color="black", difficulty=difficulty)
        ai.player_model.skill_estimate = 1.0
        move = ai.choose_move(board)
        assert move.start == "d8" and move.end == "h4"

    def test_pool_based_choice_at_low_skill_stays_legal(self):
        board = Board()
        difficulty = DifficultyController(min_depth=1, max_depth=1,
                                           min_time_limit=0.5, max_time_limit=0.5,
                                           candidate_pool_size=3,
                                           min_noise=0.4, max_noise=0.4)
        ai = AIPlayer(color="white", difficulty=difficulty)
        ai.player_model.skill_estimate = 0.0
        move = ai.choose_move(board)
        legal = {(m.start, m.end) for m in board.get_legal_moves("white")}
        assert (move.start, move.end) in legal


class TestMoveQualityEstimation:
    def test_matching_the_engines_best_move_scores_high(self):
        board = Board()
        top = estimate_move_quality
        from chess_engine.ai.search import get_top_n_moves
        candidates = get_top_n_moves(board, depth=2, n=5, maximizing=True)
        best_move = candidates[0][1]
        quality = estimate_move_quality(board, best_move, search_depth=2)
        assert quality == 1.0

    def test_move_outside_considered_pool_scores_zero(self):
        board = Board()
        from chess_engine.ai.search import get_top_n_moves
        candidates = get_top_n_moves(board, depth=2, n=3, maximizing=True)
        considered = {(m.start, m.end) for _, m in candidates}
        legal = board.get_legal_moves("white")
        outside = next(m for m in legal if (m.start, m.end) not in considered)
        quality = estimate_move_quality(board, outside, search_depth=2)
        assert quality == 0.0


class TestPlayerModelIntegration:
    def test_observing_a_good_move_raises_skill_estimate(self):
        board = Board()
        ai = AIPlayer(color="black", player_model=PlayerModel(initial_estimate=0.5))
        from chess_engine.ai.search import get_top_n_moves
        candidates = get_top_n_moves(board, depth=2, n=5, maximizing=True)
        best_move = candidates[0][1]
        ai.observe_player_move(board, best_move)
        assert ai.current_skill_estimate > 0.5

    def test_reset_restores_initial_skill(self):
        ai = AIPlayer(color="black", player_model=PlayerModel(initial_estimate=0.5))
        ai.player_model.update(1.0)
        ai.reset()
        assert ai.current_skill_estimate == 0.5


class TestWeightedPick:
    def test_zero_noise_always_picks_best(self):
        candidates = [(100, "best"), (50, "mid"), (0, "worst")]
        for _ in range(10):
            assert weighted_pick(candidates, noise=0.0) == "best"

    def test_single_candidate_returned_regardless_of_noise(self):
        candidates = [(100, "only")]
        assert weighted_pick(candidates, noise=0.4) == "only"

    def test_empty_candidates_returns_none(self):
        assert weighted_pick([], noise=0.2) is None
