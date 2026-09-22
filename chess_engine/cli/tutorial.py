"""The Interactive Tutorial: a scripted, step-by-step first-time
experience using the engine's real command syntax and rule-checking.
reader/writer are injected (default input/print) so this can be
driven by tests without a real terminal."""

from ..core.board import Board
from ..core.moves import Move
from .commands import parse_command
from . import ui


def _prompt_move(reader, writer, expected_start, expected_end, board,
                  hint, max_attempts=None):
    """Ask for moves until the learner plays expected_start->expected_end
    (or any legal move, if expected_end is None — used for open-ended
    steps like 'try capturing the pawn')."""
    attempts = 0
    while True:
        raw = reader("> ")
        command = parse_command(raw)
        attempts += 1

        if command.name != "move":
            writer("Type a move like \"p e2 e4\", using the format shown above.")
            continue

        start, end = command.args["start"], command.args["end"]
        if start != expected_start or (expected_end is not None and end != expected_end):
            writer(f"Not quite — {hint}")
            if max_attempts and attempts >= max_attempts:
                writer(f"(Hint: try \"p {expected_start} {expected_end}\")")
            continue

        move = Move(start, end, promotion=command.args.get("promotion"))
        if not board.make_move(move):
            writer("That's the move I'm looking for, but it isn't legal here — try again.")
            continue

        return move


def run_tutorial(reader=input, writer=print, settings=None):
    use_unicode = getattr(settings, "use_unicode", True)

    writer("=" * 40)
    writer("       WELCOME TO THE CHESS ENGINE")
    writer("=" * 40)
    writer("")
    writer("This short tutorial will walk you through reading the board,")
    writer("making moves, and the engine's own commands. Let's begin.")
    reader("\n(press Enter to continue) ")

    # ---- Reading the board / coordinates -------------------------------
    board = Board()
    writer("")
    writer("Here's the starting position:")
    for line in ui.render_board(board, use_unicode=use_unicode):
        writer(line)
    writer("")
    writer("Columns (files) are labeled a-h, rows (ranks) 1-8. Every square")
    writer("has a name, like e4 or g7 — that's how you'll refer to squares")
    writer("when making moves.")
    reader("\n(press Enter to continue) ")

    # ---- Selecting a piece / first move ---------------------------------
    writer("")
    writer("Let's make your first move.")
    writer("")
    writer("Move the pawn from e2 to e4.")
    writer("")
    writer('Type it as: p e2 e4')
    writer("")
    _prompt_move(reader, writer, "e2", "e4", board,
                 "the pawn on e2 needs to go to e4.")
    writer("")
    writer("Correct! You've made your first chess move.")
    for line in ui.render_board(board, use_unicode=use_unicode):
        writer(line)
    reader("\n(press Enter to continue: capturing pieces) ")

    # ---- Capturing --------------------------------------------------------
    writer("")
    writer("Next lesson: capturing pieces.")
    writer("Black has just played a pawn to d5, right next to yours. Capture")
    writer("it by moving your pawn from e4 to d5 — pawns capture diagonally.")
    board.make_move(Move("d7", "d5"))
    writer("")
    for line in ui.render_board(board, use_unicode=use_unicode):
        writer(line)
    writer("")
    _prompt_move(reader, writer, "e4", "d5", board,
                 "capture by moving the e4 pawn diagonally to d5.")
    writer("")
    writer("Nice capture! That's how pawns take pieces.")
    reader("\n(press Enter to continue: check) ")

    # ---- Check --------------------------------------------------------------
    writer("")
    writer("Now let's look at check. Here's a simplified position:")
    board = Board()
    board.from_fen("4r2k/8/8/8/8/8/8/4K3 w - - 0 1")
    for line in ui.render_board(board, use_unicode=use_unicode):
        writer(line)
    writer("")
    writer("Black's rook on e8 attacks straight down the open e-file, right")
    writer("onto White's king on e1 — White is 'in check' and must respond")
    writer("immediately (move the king to safety, block the file, or capture")
    writer("the rook). Checkmate and stalemate build on this idea: checkmate")
    writer("is check with no way out; stalemate is no legal move at all, but")
    writer("NOT in check.")
    reader("\n(press Enter to continue: castling) ")

    # ---- Castling -----------------------------------------------------------
    writer("")
    writer("Castling lets you move your king to safety and bring a rook into")
    writer("play in one move. Here, White can castle kingside:")
    board = Board()
    board.from_fen("rnbqkbnr/pppppppp/8/8/8/5NP1/PPPPPPBP/RNBQK2R w KQkq - 0 1")
    for line in ui.render_board(board, use_unicode=use_unicode):
        writer(line)
    writer("")
    writer('Castle kingside by moving the king two squares: "p e1 g1"')
    writer("")
    _prompt_move(reader, writer, "e1", "g1", board,
                 "move the king from e1 to g1 to castle kingside.")
    writer("")
    writer("That's castling — the rook automatically hops to f1.")
    reader("\n(press Enter to continue: promotion) ")

    # ---- Promotion ------------------------------------------------------------
    writer("")
    writer("When a pawn reaches the far rank, it must promote. Here, White's")
    writer("pawn on e7 is one step from promoting:")
    board = Board()
    board.from_fen("k7/4P3/8/8/8/8/8/4K3 w - - 0 1")
    for line in ui.render_board(board, use_unicode=use_unicode):
        writer(line)
    writer("")
    writer('Promote to a Queen by adding "q" to your move: "p e7 e8 q"')
    writer("")
    _prompt_move(reader, writer, "e7", "e8", board,
                 "move the pawn from e7 to e8 and promote it.")
    writer("")
    writer("Promoted! You can also promote to a Rook, Bishop, or Knight by")
    writer("using r, b, or n instead of q.")
    reader("\n(press Enter to continue: engine commands) ")

    # ---- Engine commands ------------------------------------------------------
    writer("")
    writer("A few commands you'll use outside of moves:")
    writer("  help     - show the full command list")
    writer("  guide    - open the Guide Book")
    writer("  undo/redo - step backward/forward through the game")
    writer("  fen      - see the current position as FEN")
    writer("  quit     - leave the game and return to the main menu")
    reader("\n(press Enter to finish) ")

    writer("")
    writer("=" * 40)
    writer("   TUTORIAL COMPLETE — you're ready to play!")
    writer("=" * 40)
    reader("\n(press Enter to return to the main menu) ")
