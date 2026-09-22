"""Tests for AI/difficulty.py."""

import pytest

from chess_engine.ai.difficulty import PlayerModel, DifficultyController


class TestPlayerModel:
    def test_initial_estimate(self):
        model = PlayerModel(initial_estimate=0.5)
        assert model.skill_estimate == 0.5
        assert model.moves_observed == 0

    def test_update_moves_toward_observed_quality(self):
        model = PlayerModel(smoothing=0.5, initial_estimate=0.5)
        model.update(1.0)
        assert model.skill_estimate == pytest.approx(0.75)
        assert model.moves_observed == 1

    def test_update_clamps_out_of_range_quality(self):
        model = PlayerModel(smoothing=0.5, initial_estimate=0.5)
        model.update(5.0)  # should clamp to 1.0
        assert model.skill_estimate == pytest.approx(0.75)

    def test_reset_restores_initial_estimate(self):
        model = PlayerModel(initial_estimate=0.5)
        model.update(1.0)
        model.update(1.0)
        model.reset()
        assert model.skill_estimate == 0.5
        assert model.moves_observed == 0

    def test_rejects_invalid_smoothing(self):
        with pytest.raises(ValueError):
            PlayerModel(smoothing=0.0)
        with pytest.raises(ValueError):
            PlayerModel(smoothing=1.5)


class TestDifficultyController:
    def test_depth_scales_with_skill(self):
        controller = DifficultyController(min_depth=1, max_depth=6)
        assert controller.get_depth(0.0) == 1
        assert controller.get_depth(1.0) == 6
        assert controller.get_depth(0.0) < controller.get_depth(1.0)

    def test_time_limit_scales_with_skill(self):
        controller = DifficultyController(min_time_limit=1.0, max_time_limit=8.0)
        assert controller.get_time_limit(0.0) == pytest.approx(1.0)
        assert controller.get_time_limit(1.0) == pytest.approx(8.0)
        assert controller.get_time_limit(0.0) < controller.get_time_limit(1.0)

    def test_noise_decreases_with_skill(self):
        controller = DifficultyController(min_noise=0.0, max_noise=0.4)
        assert controller.get_move_noise(0.0) == pytest.approx(0.4)
        assert controller.get_move_noise(1.0) == pytest.approx(0.0)

    def test_candidate_pool_size_is_configurable(self):
        controller = DifficultyController(candidate_pool_size=5)
        assert controller.get_candidate_pool_size(0.3) == 5
        assert controller.get_candidate_pool_size(0.9) == 5
