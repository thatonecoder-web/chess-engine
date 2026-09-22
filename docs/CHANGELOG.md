# Changelog

## v0.1.0 — Project Foundation

└─ Repo structure, README, license, changelog

## v0.1.1 — Basic Board

├─ Piece classes

├─ Board representation

└─ ASCII board display

## v0.1.2 — Move Representation

├─ Basic `Move` class

├─ Start and end square tracking

├─ Chess coordinate conversion

└─ Move string representation

## v0.1.3 — Basic Move Execution

├─ Move pieces from one square to another

├─ Piece capturing

├─ Empty-square validation

├─ Turn tracking

├─ Prevent moving the opponent's pieces

├─ Prevent capturing your own pieces

└─ Basic interactive move input

## v0.1.4 — Piece Movement Rules

├─ Basic movement rules for all pieces

├─ Pawn movement and captures

├─ Knight movement

├─ Bishop movement

├─ Rook movement

├─ Queen movement

├─ King movement

├─ Path obstruction detection

└─ Initial movement-rule test coverage

## v0.1.5 — Check & Game State Detection

├─ King-in-check detection

├─ Piece attack detection

├─ Prevent moves that leave the king in check

├─ Checkmate detection

├─ Stalemate detection

└─ Initial check/checkmate test coverage

## v0.1.6 — Advanced Chess Rules

├─ Added pawn promotion with default queen promotion and piece-symbol selection

├─ Added legal en-passant detection with an en-passant target remembered from the previous two-step pawn move

├─ Added castling support for kingside and queenside, including rook movement and king safety checks

├─ Extended the board state object to remember previous move and en-passant target data

├─ Kept package import behavior stable while updating the project structure

└─ Verified the full pytest suite remains green for the requested release

## v0.1.7 — Move & Game State Improvements

├─ Added robust attack detection for pawn attacks, king attacks, and reliable check edge cases

├─ Added legal move generation for a side and reused it for checkmate and stalemate detection

├─ Centralized legality checks around move validation and coordinate rejection for invalid/out-of-board moves

├─ Improved game-state detection to distinguish check, checkmate, and stalemate more clearly

└─ Expanded test coverage for pawn checks, king attacks, pins, castling through attacked squares,
en passant exposing the king, promotion while in check, and checkmate/stalemate edge cases

## v0.1.8 — Position Representation & Notation

├─ Added FEN (Forsyth-Edwards Notation) position generation

├─ Added FEN position parsing and loading

├─ Added FEN validation for board state, active color, castling rights, en-passant target, and move counters

├─ Added Algebraic Notation support for representing individual chess moves

├─ Added FEN-based position testing for arbitrary board states

└─ Expanded regression test coverage for FEN parsing, FEN generation, and algebraic move notation

## v0.1.9 — Game Records & Engine Validation

├─ Added move history tracking with move numbers and game state information

├─ Added PGN (Portable Game Notation) parsing and generation

├─ Added PGN game metadata support for players, event, site, date, result, and other standard tags

├─ Added complete game replay from PGN move sequences

├─ Added recursive Perft testing for validating legal move generation

├─ Added standard starting-position Perft test cases

├─ Added tactical and special-rule Perft positions covering castling, en passant, promotion, checks, and pins

├─ Added move-generation regression tests based on Perft results

├─ Added JSON-based save files for preserving resumable game state

├─ Added save/load commands for terminal gameplay

├─ Added undo and redo functionality using recorded game state

└─ Expanded test coverage for PGN parsing, game replay, Perft validation, move history, and game persistence

## v0.2.0 — AI Engine

├─ Added new `chess_engine/ai/` module for the from-scratch chess AI

├─ Added evaluation function based on material count and piece-square tables

├─ Added Minimax search with alpha-beta pruning

├─ Added move ordering with captures and checks prioritized for search efficiency

├─ Added selectable difficulty levels from 0 to max

└─ Added `AIPlayer` interface for integration with the existing game loop

## v0.2.5 — AI Engine Complete

├─ Completed the from-scratch chess AI system, wired against the engine's real Board/Move/Piece classes (the v0.2.0 AI module was scaffolding written against an assumed interface that didn't match)

├─ Advanced position evaluation
│  ├─ Material evaluation
│  ├─ Piece-square tables
│  ├─ Center control
│  ├─ Piece development
│  ├─ King safety
│  └─ Pawn structure

├─ Advanced search
│  ├─ Minimax
│  ├─ Alpha-beta pruning
│  ├─ Iterative deepening
│  └─ Quiescence search

├─ Advanced move ordering
│  ├─ Captures (MVV-LVA, including en passant)
│  ├─ Checks
│  ├─ Promotions
│  ├─ Killer moves
│  └─ History-based ordering

├─ Added configurable search depth and difficulty

├─ Added search limits and AI time management

├─ Added AI search statistics
│  ├─ Nodes searched
│  ├─ Search depth
│  ├─ Evaluation score
│  └─ Search time

├─ Added deterministic search behavior for identical positions

├─ Added comprehensive AI regression tests

├─ Added tactical test positions

├─ Added AI performance benchmarks

├─ Fixed `Move` equality (`__eq__`/`__hash__`), so a move parsed from input or a fresh move-generation pass compares correctly against a move from another search — this had silently broken move-quality tracking

├─ Improved handling of:
│  ├─ Checkmate
│  ├─ Stalemate
│  ├─ Castling
│  ├─ En passant
│  └─ Promotion

├─ Verified AI compatibility with FEN and PGN systems

├─ Integrated the completed AI system with the game loop

└─ Verified the complete pytest suite before release

## v0.2.6 — Terminal UI Foundation

├─ Added `chess_engine/ui.py` for all terminal rendering, separate from game logic

├─ Unicode chess-piece rendering
│  ├─ ♔ ♕ ♖ ♗ ♘ ♙ piece display (with an ASCII fallback via Settings)
│  ├─ Coordinate labels (files a-h, ranks 1-8)
│  └─ Boxed board borders and consistent spacing

├─ Turn indicator and check / checkmate / stalemate status line

├─ Last-move display, shown above the board on every redraw

├─ Clean terminal redraw each turn (toggleable in Settings)

└─ Preserved the `p <from> <to> [promotion]` move syntax (e.g. `p e2 e4`, `p e7 e8 q`),
   now handled by a shared `commands.py` parser used by every mode

## v0.2.7 — Game Modes & Main Menu

├─ Added `chess_engine/menu.py` with the main menu system
│  ├─ Player vs Player
│  ├─ Player vs AI (with difficulty selection)
│  ├─ AI vs AI
│  ├─ Interactive Tutorial
│  ├─ Guide Book
│  ├─ Settings
│  └─ Exit

├─ Added `chess_engine/AI/difficulty_levels.py`: named difficulty presets
│  (Beginner -> Maximum) bridging the adaptive skill-estimate system to a
│  fixed menu choice, usable both adaptively (Player vs AI) and pinned
│  (AI vs AI)

├─ AI vs AI mode
│  ├─ Select White AI difficulty and Black AI difficulty independently
│  ├─ Engines play automatically (background input listener for
│  │  pause/stop, so watching doesn't require pressing Enter every move)
│  ├─ Live search info display (depth, nodes, evaluation) while each side thinks
│  ├─ Pause / resume and stop-game controls
│  └─ Completed games recorded to a PGN file automatically

└─ Rewrote `chess_engine/main.py` and `chess_engine/play.py`: the game loop
   now runs on the `Game` class (undo/redo/PGN/save/load all wired into
   live play, not just the library API) instead of a bare `Board` loop

## v0.2.8 — Guide Book

├─ Added `chess_engine/guide.py`: a built-in, browsable chess manual
│  ├─ How Chess Works, The Chessboard, Chess Pieces, Legal Moves, Capturing
│  ├─ Check, Checkmate, Stalemate
│  ├─ Castling, En Passant, Promotion
│  ├─ Algebraic Notation, FEN
│  ├─ Playing Against the AI, AI Difficulty
│  ├─ Engine Commands (shared text with the in-game `help` command)
│  └─ How to Use This Engine

└─ Reachable from the main menu and, mid-game, via the `guide` command

## v0.2.9 — Interactive Tutorial

├─ Added `chess_engine/tutorial.py`: a scripted first-time walkthrough
│  ├─ Reading the board and coordinates
│  ├─ Selecting a piece and making a first move
│  ├─ Capturing a piece
│  ├─ Understanding check
│  ├─ Learning castling
│  ├─ Learning promotion
│  └─ Engine commands, then back to the main menu

└─ Uses the real Board/Move classes throughout, so what's practiced in
   the tutorial is exactly the real move syntax and rule-checking

## v0.3.0 — Complete Terminal Chess Experience

├─ Added `chess_engine/settings.py`: a Settings screen covering Unicode
│  vs ASCII display, clean-redraw on/off, captured-piece display, and
│  AI search-statistics display, threaded through menu -> play -> ui

├─ Added captured-piece tracking and display (including en passant captures)

├─ Added a move counter and game-status panel to every redraw

├─ Full command system: `p`, `moves`, `history`, `undo`, `redo`, `fen`,
│  `save`, `load`, `help`, `guide`, `quit` — documented in both the
│  in-game `help` command and the Guide Book's "Engine Commands" topic

├─ Centralized error handling for illegal moves, bad commands, and
│  save/load failures, with consistent messaging across all modes

├─ Polished main-menu box, AI-vs-AI setup flow, and Settings screen

└─ Bumped package version to 0.3.0

## v0.3.1 — Package Reorganization

├─ Split the flat `chess_engine/` module list into three subpackages so
│  the codebase scrolls and navigates like its actual shape:
│  ├─ `chess_engine/core/` — board, moves, pieces, rules, check, game, perft
│  │  (pure chess: no AI, no terminal UI)
│  ├─ `chess_engine/ai/` — renamed from `AI/` for consistent lowercase
│  │  package naming; evaluation, search, move ordering, difficulty,
│  │  difficulty_levels, ai_player, benchmarks
│  └─ `chess_engine/cli/` — menu, play loop, commands, guide, tutorial,
│     settings, ui (everything terminal-facing)

├─ Mirrored the split in `tests/`: `tests/core/`, `tests/ai/`, `tests/cli/`
│  (renamed from `tests/ai-tests/`)

├─ Updated every internal import accordingly; `chess_engine/__init__.py`
│  still re-exports the same public API (`Board`, `Move`, `Game`,
│  `GameHistory`, `Settings`, `main_menu`, etc.), so existing
│  `from chess_engine import ...` usage is unaffected

├─ `chess_engine/main.py` stays at the package root as the entry point
│  (`python -m chess_engine.main` unchanged); it now delegates to
│  `chess_engine.cli.menu`

└─ No functional changes — full test suite (140 tests) passes unchanged;
   this is purely a structural cleanup
