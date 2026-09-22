# v0.3.1 Release Notes

## Overview

v0.2.5 finished the AI. This release covers everything since: a
terminal app built around it (v0.2.6-v0.3.0), then a reorg of the
codebase itself (v0.3.1) now that it's outgrown a flat file list.

**Release date:** 09.30.2026

---

## v0.2.6 - Terminal UI foundation

Board rendering moved into `cli/ui.py`: Unicode pieces (♔ ♕ ♖ ♗ ♘ ♙ /
♚ ♛ ♜ ♝ ♞ ♟) with a plain-ASCII fallback, file/rank labels, boxed
borders, a turn indicator, and check/checkmate/stalemate status. The
`p e2 e4` move syntax stayed the same - it just runs through a shared
parser (`cli/commands.py`) now so every mode uses the same commands.

## v0.2.7 - Menu and game modes

Added the main menu (`cli/menu.py`): Player vs Player, Player vs AI,
AI vs AI, Tutorial, Guide Book, Settings.

Difficulty presets (`ai/difficulty_levels.py`) map named levels
(Beginner through Maximum) onto the AI's continuous skill scale. In
Player vs AI that estimate keeps adapting to the human as before; in
AI vs AI it's pinned for the whole game so the two chosen difficulties
actually mean something relative to each other.

AI vs AI plays out on its own - a background thread listens for
`pause`/`stop` so you're not stuck pressing Enter after every move.
It shows depth/nodes/eval while each side thinks and writes a PGN of
the finished game automatically.

The game loop itself moved onto the `Game` class instead of a bare
`Board`, which is why undo/redo/save/load - already written, just
never wired up - work in every mode now.

## v0.2.8 - Guide Book

A 17-topic manual in `cli/guide.py`, covering the rules through FEN
and the engine's own commands. Its "Engine Commands" section shares
text with the in-game `help` command so the two can't drift apart.
Open it from the main menu, or type `guide` mid-game.

## v0.2.9 - Interactive Tutorial

A scripted first-time walkthrough in `cli/tutorial.py`: reading the
board, making a move, capturing, check, castling, promotion, then the
commands. It runs on the real `Board`/`Move` classes, so nothing about
it is simulated - what you type there is exactly what you'd type in a
real game.

## v0.3.0 - Settings, captured pieces, full commands

A `Settings` object (`cli/settings.py`) toggles Unicode/ASCII display,
clean redraws, captured-piece display, and AI search stats, and takes
effect immediately wherever it's checked. Captures are now tracked and
shown for both sides, including en passant. The command set settled
into `p`, `moves`, `history`, `undo`, `redo`, `fen`, `save`, `load`,
`help`, `guide`, `quit`, with consistent error handling everywhere.

Tests for all of the above live in `tests/cli/test_ui_and_menu.py` -
command parsing, board rendering, the tutorial and guide flows end to
end, and a full AI vs AI game played to completion.

## v0.3.1 - Package reorganization

`chess_engine/` had grown to 15+ files in one folder. It's now three
subpackages by what the code actually does:

- `core/` - board, moves, pieces, rules, check, game, perft. No AI, no UI.
- `ai/` - evaluation, search, move ordering, difficulty, ai_player,
  benchmarks. Renamed from `AI/` for consistent lowercase naming.
- `cli/` - menu, play, commands, guide, tutorial, settings, ui.

`tests/` mirrors it: `core/`, `ai/`, `cli/` (was `ai-tests/` before).

The top-level `from chess_engine import ...` API didn't change -
`Board`, `Move`, `Game`, `Settings`, `main_menu`, etc. still work the
same. `python -m chess_engine.main` still works too. No functional
change; all 140 tests pass before and after.

---

## Known limitations

- AI vs AI's pause/stop only works from a real terminal - stdin has to
  be an interactive TTY for the background listener to start. It
  still plays to completion without one, just without the interrupt.
- Both AI vs AI and Player vs AI are local and single-process.
- "Board-size/display configuration," from the original plan, became
  the Unicode/ASCII and redraw toggles in Settings rather than an
  actually resizable board - it's always 8x8.
- Still no bitboards or transposition table (see RELEASE_v0.2.5.md).

## Breaking changes

Import paths below the top level changed:

- `chess_engine.board` etc. -> `chess_engine.core.board` etc.
- `chess_engine.AI.*` -> `chess_engine.ai.*`
- `chess_engine.ui`/`.commands`/`.guide`/`.menu`/`.play`/`.settings`/`.tutorial` -> `chess_engine.cli.*`

Unaffected: `from chess_engine import Board, Move, Game, GameHistory,
Settings, main_menu, perft, perft_divide, run_perft_test`, and
`python -m chess_engine.main`.
