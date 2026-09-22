"""The game loop: `play_game` handles all three modes (PvP, PvAI, AI vs
AI) by taking optional AIPlayer objects for either side -- a side with
no AIPlayer is a human, read from the terminal. Captured-piece
tracking, undo/redo, save/load, and in-game commands live here since
they're the same regardless of mode."""

import sys
import time
import queue
import threading
import datetime

from ..core.game import Game
from ..core.moves import Move
from . import ui
from .commands import parse_command, HELP_TEXT
from .guide import run_guide

AI_VS_AI_MOVE_DELAY = 0.6  # seconds paused after each move so it's watchable


class _BackgroundInputListener:
    """Reads lines from stdin on a background thread so AI vs AI can
    play automatically while still noticing a typed 'pause' or 'stop'
    without blocking on input() between every move.

    Only used when stdin is a real interactive terminal — in
    non-interactive contexts (tests, piped input) we skip it entirely
    so we never race with, or steal input from, whatever else is
    reading stdin.
    """

    def __init__(self):
        self._queue = queue.Queue()
        self._stopped = False
        self._thread = threading.Thread(target=self._read_loop, daemon=True)
        self._thread.start()

    def _read_loop(self):
        while not self._stopped:
            try:
                line = input()
            except (EOFError, RuntimeError):
                return
            self._queue.put(line.strip().lower())

    def poll(self):
        try:
            return self._queue.get_nowait()
        except queue.Empty:
            return None

    def stop(self):
        self._stopped = True


def _wait_watchably(listener, seconds):
    """Sleep for `seconds`, but in short slices so a pause/stop typed
    mid-wait is picked up promptly. Returns the first pending command
    seen, or None."""
    if listener is None:
        return None
    slices = max(1, int(seconds / 0.1))
    for _ in range(slices):
        command = listener.poll()
        if command:
            return command
        time.sleep(seconds / slices)
    return None


def _record_capture(board, move, captured_white, captured_black):
    """Inspect the board BEFORE a move is applied and, if the move is a
    capture, stash the captured piece in the right tray. Must be
    called before board.make_move()."""
    start_row, start_col = move.get_coordinates(move.start)
    end_row, end_col = move.get_coordinates(move.end)
    target = board.board[end_row][end_col]
    mover = board.board[start_row][start_col]

    if target is not None:
        (captured_white if target.color == "white" else captured_black).append(target)
        return

    # En passant: the captured pawn isn't on the destination square.
    if mover is not None and mover.symbol.upper() == "P" and target is None \
            and abs(end_col - start_col) == 1 and board.en_passant_target == (end_row, end_col):
        captured = board.board[start_row][end_col]
        if captured is not None:
            (captured_white if captured.color == "white" else captured_black).append(captured)


def _ai_label(color):
    return f"{color.upper()} AI"


def _offer_pgn_save(game, writer=print):
    """Record a completed AI vs AI game to a PGN file automatically,
    so a run isn't lost once the terminal window closes."""
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"aivai_game_{timestamp}.pgn"
    try:
        with open(filename, "w") as f:
            f.write(game.to_pgn())
        writer(f"Game recorded to {filename}.")
    except OSError as exc:
        writer(f"Could not record PGN: {exc}")


def _run_ai_turn(game, ai, settings, writer=print):
    """Let an AIPlayer make its move, printing the "thinking" display.
    Returns the Move played, or None if the AI had no legal move
    (game over)."""
    label = _ai_label(ai.color)
    if settings.show_ai_search_info:
        writer("\n".join(ui.ai_thinking_lines(label, thinking=True)))

    start = time.time()
    move = ai.choose_move(game.board)
    elapsed = time.time() - start

    if move is None:
        return None

    captured_white, captured_black = [], []
    _record_capture(game.board, move, captured_white, captured_black)
    game.make_move(move)

    if settings.show_ai_search_info and ai.last_search_stats is not None:
        stats = ai.last_search_stats
        writer("\n".join(ui.ai_thinking_lines(
            label, depth=stats.depth_reached, nodes=stats.total_nodes,
            evaluation=None, thinking=False,
        )))
        writer(f"({elapsed:.2f}s)")

    return move, captured_white, captured_black


def play_game(mode, settings, white_ai=None, black_ai=None, title="Chess Engine"):
    """Run one game to completion (or until the player quits).

    mode: "pvp", "pvai", or "aivai" — only affects framing text and
    whether pause/stop controls apply; the actual turn logic is driven
    entirely by whether white_ai/black_ai are set for each side.
    """
    game = Game()
    captured_white = []  # White pieces that have been captured
    captured_black = []  # Black pieces that have been captured
    paused = False

    listener = None
    if mode == "aivai" and hasattr(sys.stdin, "isatty") and sys.stdin.isatty():
        listener = _BackgroundInputListener()

    def ai_for(color):
        return white_ai if color == "white" else black_ai

    while True:
        board = game.board
        extra = []
        if mode == "aivai":
            if paused:
                extra.append("[PAUSED — type 'resume' to continue, 'stop' to end the game]")
            elif listener is not None:
                extra.append("(playing automatically — type 'pause' or 'stop' + Enter anytime)")

        ui.render_frame(
            board, title=title,
            last_move=board.previous_move,
            move_number=game.history.get_current_move_number(),
            mover=("black" if board.turn == "white" else "white") if board.previous_move else None,
            captured_white=captured_white if settings.show_captured else None,
            captured_black=captured_black if settings.show_captured else None,
            use_unicode=settings.use_unicode,
            extra_lines=extra,
            redraw=settings.clear_screen,
        )

        if board.is_game_over():
            if board.is_checkmate(board.turn):
                winner = "Black" if board.turn == "white" else "White"
                print(f"\nCheckmate — {winner} wins.")
                game.set_metadata("Result", "1-0" if winner == "White" else "0-1")
            else:
                print("\nStalemate — draw.")
                game.set_metadata("Result", "1/2-1/2")
            if mode == "aivai":
                _offer_pgn_save(game)
            if listener is not None:
                listener.stop()
            return game

        current_ai = ai_for(board.turn)

        # ---- AI vs AI pause/stop controls -------------------------------
        if mode == "aivai":
            if paused:
                if listener is not None:
                    cmd = listener.poll()
                    if cmd is None:
                        time.sleep(0.1)
                        continue
                else:
                    cmd = input("Paused — type 'resume' or 'stop': ").strip().lower()

                if cmd in ("resume", "r", ""):
                    if cmd == "":
                        continue
                    paused = False
                elif cmd in ("stop", "s", "quit", "q"):
                    print("Game stopped.")
                    if listener is not None:
                        listener.stop()
                    return game
                continue

        if current_ai is not None:
            if mode == "aivai":
                # Plays automatically — a background listener (real
                # terminals only) lets 'pause'/'stop' interrupt without
                # blocking each move on an Enter press.
                command = _wait_watchably(listener, AI_VS_AI_MOVE_DELAY)
                if command in ("pause", "p"):
                    paused = True
                    continue
                if command in ("stop", "s", "quit", "q"):
                    print("Game stopped.")
                    if listener is not None:
                        listener.stop()
                    return game

            result = _run_ai_turn(game, current_ai, settings)
            if result is None:
                print(f"{_ai_label(current_ai.color)} has no legal move.")
                if mode == "aivai":
                    _offer_pgn_save(game)
                if listener is not None:
                    listener.stop()
                return game
            move, cw, cb = result
            captured_white.extend(cw)
            captured_black.extend(cb)
            continue

        # ---- Human turn --------------------------------------------------
        raw = input("Your move ('help' for commands): ")
        command = parse_command(raw)

        if command.name is None:
            print("Unrecognized input. Type 'help' for the command list.")
            continue

        if command.name == "quit":
            return game

        if command.name == "help":
            print(HELP_TEXT)
            input("\n(press Enter to continue) ")
            continue

        if command.name == "guide":
            run_guide()
            continue

        if command.name == "fen":
            print(board.to_fen())
            input("\n(press Enter to continue) ")
            continue

        if command.name == "history":
            moves = game.history.get_all_moves()
            if not moves:
                print("(no moves played yet)")
            else:
                print(" ".join(m.to_algebraic() for m in moves))
            input("\n(press Enter to continue) ")
            continue

        if command.name == "moves":
            legal = board.get_legal_moves(board.turn)
            if command.args:
                square = command.args[0].lower()
                legal = [m for m in legal if m.start == square]
            if not legal:
                print("(no legal moves)" if command.args else "(no legal moves — game should be over)")
            else:
                print(", ".join(m.to_algebraic() for m in legal))
            input("\n(press Enter to continue) ")
            continue

        if command.name == "undo":
            if game.undo():
                print("Move undone.")
            else:
                print("Nothing to undo.")
            continue

        if command.name == "redo":
            if game.redo():
                print("Move redone.")
            else:
                print("Nothing to redo.")
            continue

        if command.name == "save":
            filename = command.args[0] if command.args else "game.json"
            try:
                game.save_to_file(filename)
                print(f"Saved to {filename}.")
            except OSError as exc:
                print(f"Could not save: {exc}")
            input("\n(press Enter to continue) ")
            continue

        if command.name == "load":
            if not command.args:
                print("Usage: load <filename>")
                input("\n(press Enter to continue) ")
                continue
            try:
                game.load_from_file(command.args[0])
                captured_white, captured_black = [], []
                print(f"Loaded {command.args[0]}.")
            except (OSError, ValueError) as exc:
                print(f"Could not load: {exc}")
            input("\n(press Enter to continue) ")
            continue

        if command.name == "move":
            args = command.args
            move = Move(args["start"], args["end"], promotion=args.get("promotion"))
            board_before = board.copy()
            new_cw, new_cb = [], []
            _record_capture(board, move, new_cw, new_cb)
            if game.make_move(move):
                captured_white.extend(new_cw)
                captured_black.extend(new_cb)
                opponent_ai = ai_for("black" if board_before.turn == "white" else "white")
                if opponent_ai is not None:
                    opponent_ai.observe_player_move(board_before, move)
            else:
                print("Illegal move.")
                input("\n(press Enter to continue) ")
            continue
