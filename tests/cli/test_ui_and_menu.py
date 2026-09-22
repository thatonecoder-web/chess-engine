"""Tests for the v0.2.6-v0.3.0 terminal UI, menu, and helper modules."""

import os

from chess_engine.core.board import Board
from chess_engine.cli.settings import Settings
from chess_engine.cli import ui, commands
from chess_engine.cli.guide import run_guide, TOPICS
from chess_engine.cli.tutorial import run_tutorial
from chess_engine.cli.play import play_game
from chess_engine.ai.difficulty_levels import level_names, skill_for_level, make_ai_player


def _scripted_io(lines):
    remaining = iter(lines)

    def reader(prompt=""):
        return next(remaining, "0")

    def writer(text=""):
        pass

    return reader, writer


class TestCommands:
    def test_move_command(self):
        cmd = commands.parse_command("p e2 e4")
        assert cmd.name == "move"
        assert cmd.args == {"start": "e2", "end": "e4"}

    def test_move_command_with_promotion(self):
        cmd = commands.parse_command("p e7 e8 q")
        assert cmd.args["promotion"] == "q"

    def test_known_bare_command(self):
        assert commands.parse_command("undo").name == "undo"
        assert commands.parse_command("QUIT").name == "quit"

    def test_command_with_args(self):
        cmd = commands.parse_command("save mygame.json")
        assert cmd.name == "save"
        assert cmd.args == ["mygame.json"]

    def test_unrecognized_input(self):
        cmd = commands.parse_command("banana")
        assert cmd.name is None

    def test_empty_input(self):
        cmd = commands.parse_command("   ")
        assert cmd.name is None
        assert cmd.args == []


class TestUI:
    def test_render_board_shape(self):
        board = Board()
        lines = ui.render_board(board)
        # 8 ranks + top labels + bottom labels + top/bottom border + 7 separators
        assert len(lines) == 8 + 2 + 2 + 7
        assert "a" in lines[0]

    def test_ascii_fallback_has_no_unicode_glyphs(self):
        board = Board()
        text = "\n".join(ui.render_board(board, use_unicode=False))
        for glyph in ui.UNICODE_PIECES.values():
            assert glyph not in text

    def test_status_banner_start_position(self):
        board = Board()
        assert "White to move" in ui.status_banner(board)

    def test_status_banner_checkmate(self):
        board = Board()
        board.from_fen("rnb1kbnr/pppp1ppp/8/4p3/6Pq/5P2/PPPPP2P/RNBQKBNR w KQkq - 0 1")
        assert "CHECKMATE" in ui.status_banner(board)

    def test_ai_thinking_lines_format(self):
        lines = ui.ai_thinking_lines("WHITE AI", depth=8, nodes=142391, evaluation=0.42)
        joined = "\n".join(lines)
        assert "Depth: 8" in joined
        assert "142,391" in joined
        assert "+0.42" in joined


class TestDifficultyLevels:
    def test_level_names_ordered_weakest_to_strongest(self):
        names = level_names()
        assert names[0] == "Beginner"
        assert names[-1] == "Maximum"
        assert skill_for_level(names[0]) < skill_for_level(names[-1])

    def test_make_ai_player_pinned_for_ai_vs_ai(self):
        ai = make_ai_player("black", "Hard", adaptive=False)
        skill_before = ai.player_model.skill_estimate
        # A very low-quality "observed" move shouldn't meaningfully move
        # a pinned (near-zero smoothing) estimate.
        ai.player_model.update(0.0)
        assert abs(ai.player_model.skill_estimate - skill_before) < 0.01

    def test_make_ai_player_adapts_when_requested(self):
        ai = make_ai_player("white", "Medium", adaptive=True)
        skill_before = ai.player_model.skill_estimate
        ai.player_model.update(0.0)
        assert ai.player_model.skill_estimate < skill_before


class TestGuide:
    def test_topics_nonempty(self):
        assert len(TOPICS) > 10
        for title, body in TOPICS:
            assert title and body

    def test_guide_viewer_navigates_and_returns(self):
        reader, writer = _scripted_io(["1", "", "0"])
        run_guide(reader=reader, writer=writer)  # should not raise or hang

    def test_guide_viewer_rejects_bad_input_then_exits(self):
        reader, writer = _scripted_io(["99", "0"])
        run_guide(reader=reader, writer=writer)


class TestTutorial:
    def test_full_tutorial_walkthrough(self):
        reader, writer = _scripted_io([
            "", "",
            "p e2 e4", "",
            "p e4 d5", "",
            "",
            "p e1 g1", "",
            "p e7 e8 q", "",
            "", "",
        ])
        run_tutorial(reader=reader, writer=writer, settings=Settings())


class TestPlayLoop:
    def test_pvp_quit_immediately(self, monkeypatch):
        settings = Settings()
        settings.clear_screen = False
        monkeypatch.setattr("builtins.input", lambda prompt="": "quit")
        game = play_game("pvp", settings, title="t")
        assert game.history.get_all_moves() == []

    def test_pvp_move_and_undo_redo(self, monkeypatch, tmp_path):
        settings = Settings()
        settings.clear_screen = False
        script = iter(["p e2 e4", "undo", "redo", "quit"])
        monkeypatch.setattr("builtins.input", lambda prompt="": next(script))
        game = play_game("pvp", settings, title="t")
        assert [m.to_algebraic() for m in game.history.get_all_moves()] == ["e2e4"]

    def test_pvp_save_and_load(self, monkeypatch, tmp_path):
        settings = Settings()
        settings.clear_screen = False
        save_path = str(tmp_path / "game.json")
        script = iter([
            "p e2 e4", f"save {save_path}", "",
            "p e7 e5", f"load {save_path}", "",
            "quit",
        ])
        monkeypatch.setattr("builtins.input", lambda prompt="": next(script))
        game = play_game("pvp", settings, title="t")
        assert os.path.exists(save_path)
        assert [move.to_algebraic() for move in game.history.get_all_moves()] == ["e2e4"]

    def test_aivai_plays_to_completion_and_records_pgn(self, monkeypatch, tmp_path):
        from chess_engine.ai.difficulty_levels import make_ai_player

        monkeypatch.chdir(tmp_path)
        settings = Settings()
        settings.clear_screen = False
        settings.show_ai_search_info = False
        white_ai = make_ai_player("white", "Beginner", adaptive=False)
        black_ai = make_ai_player("black", "Beginner", adaptive=False)

        game = play_game("aivai", settings, white_ai=white_ai, black_ai=black_ai, title="t")
        assert game.board.is_game_over()
        pgn_files = list(tmp_path.glob("aivai_game_*.pgn"))
        assert len(pgn_files) == 1
