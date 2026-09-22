"""Terminal rendering: the board itself, its frame, and status panels
(turn indicator, check/mate banners, captured pieces, AI search info).
Nothing here mutates game state -- every function just draws."""

import os
import shutil

UNICODE_PIECES = {
    ("white", "P"): "\u2659", ("white", "N"): "\u2658", ("white", "B"): "\u2657",
    ("white", "R"): "\u2656", ("white", "Q"): "\u2655", ("white", "K"): "\u2654",
    ("black", "P"): "\u265F", ("black", "N"): "\u265E", ("black", "B"): "\u265D",
    ("black", "R"): "\u265C", ("black", "Q"): "\u265B", ("black", "K"): "\u265A",
}


def _piece_kind(piece):
    """Map a piece's stored symbol (which is case-coded by color) back
    to its uppercase kind letter, so we don't need isinstance checks."""
    return piece.symbol.upper()


def piece_glyph(piece, use_unicode=True):
    if piece is None:
        return "."
    if not use_unicode:
        return str(piece)
    return UNICODE_PIECES.get((piece.color, _piece_kind(piece)), str(piece))


def clear_screen():
    """Clear the terminal for a clean redraw. Falls back gracefully in
    non-interactive environments (tests, piped input) where clearing
    isn't meaningful."""
    try:
        os.system("cls" if os.name == "nt" else "clear")
    except Exception:
        pass


def terminal_width(default=60):
    try:
        return shutil.get_terminal_size((default, 20)).columns
    except Exception:
        return default


def render_board(board, use_unicode=True, highlight_squares=None, flip=False):
    """Return the board as a list of printable lines, framed with file
    and rank labels."""
    highlight_squares = highlight_squares or set()
    files = "abcdefgh"
    rows = range(8) if not flip else range(7, -1, -1)
    cols = range(8) if not flip else range(7, -1, -1)

    lines = []
    lines.append("    " + "  ".join(files if not flip else files[::-1]))
    lines.append("  \u250c" + "\u2500\u2500\u2500\u252c" * 7 + "\u2500\u2500\u2500\u2510")

    for row in rows:
        rank = 8 - row
        cells = []
        for col in cols:
            piece = board.board[row][col]
            square = f"{files[col]}{8 - row}"
            glyph = piece_glyph(piece, use_unicode=use_unicode)
            if square in highlight_squares:
                cells.append(f"[{glyph}]")
            else:
                cells.append(f" {glyph} ")
        row_str = "\u2502".join(cells)
        lines.append(f"{rank} \u2502{row_str}\u2502")
        if row != (7 if not flip else 0):
            lines.append("  \u251c" + "\u2500\u2500\u2500\u253c" * 7 + "\u2500\u2500\u2500\u2524")

    lines.append("  \u2514" + "\u2500\u2500\u2500\u2534" * 7 + "\u2500\u2500\u2500\u2518")
    lines.append("    " + "  ".join(files if not flip else files[::-1]))
    return lines


def render_captured(captured_white, captured_black, use_unicode=True):
    """captured_white/captured_black are lists of Piece objects taken
    FROM that color (i.e. captured_white = white pieces black has
    captured)."""
    def fmt(pieces):
        if not pieces:
            return "(none)"
        return " ".join(piece_glyph(p, use_unicode=use_unicode) for p in pieces)

    return [
        f"Captured (White): {fmt(captured_white)}",
        f"Captured (Black): {fmt(captured_black)}",
    ]


def status_banner(board):
    """One-line game status: whose turn, check/checkmate/stalemate."""
    turn = board.turn.capitalize()
    if board.is_checkmate(board.turn):
        winner = "Black" if board.turn == "white" else "White"
        return f"CHECKMATE — {winner} wins."
    if board.is_stalemate(board.turn):
        return "STALEMATE — draw."
    if board.is_in_check(board.turn):
        return f"{turn} to move — CHECK!"
    return f"{turn} to move"


def format_last_move(move, move_number=None, mover=None):
    if move is None:
        return "Last move: (none yet)"
    prefix = ""
    if move_number is not None and mover is not None:
        prefix = f"{move_number}{'.' if mover == 'white' else '...'} "
    promo = f"={move.promotion.upper()}" if getattr(move, "promotion", None) else ""
    return f"Last move: {prefix}{move.start}{move.end}{promo}"


def render_frame(board, title=None, last_move=None, move_number=None,
                  mover=None, captured_white=None, captured_black=None,
                  use_unicode=True, extra_lines=None, redraw=True):
    """Compose and print a full redraw of the game screen: title,
    board, last move, captured pieces, status, and any extra lines
    (e.g. AI thinking info) the caller wants shown."""
    if redraw:
        clear_screen()

    out = []
    if title:
        out.append(title)
        out.append("=" * min(len(title), terminal_width()))
    out.extend(render_board(board, use_unicode=use_unicode))
    out.append("")
    out.append(format_last_move(last_move, move_number, mover))
    if captured_white is not None or captured_black is not None:
        out.extend(render_captured(captured_white or [], captured_black or [],
                                    use_unicode=use_unicode))
    out.append(status_banner(board))
    if extra_lines:
        out.append("")
        out.extend(extra_lines)

    text = "\n".join(out)
    print(text)
    return text


def ai_thinking_lines(label, depth=None, nodes=None, evaluation=None, thinking=True):
    """Lines shown while/after an AI searches, matching the format the
    roadmap specifies:

        WHITE AI: Thinking...
        Depth: 8
        Nodes: 142,391
        Evaluation: +0.42
    """
    lines = [f"{label}: {'Thinking...' if thinking else 'Move played.'}"]
    if depth is not None:
        lines.append(f"Depth: {depth}")
    if nodes is not None:
        lines.append(f"Nodes: {nodes:,}")
    if evaluation is not None:
        sign = "+" if evaluation >= 0 else ""
        lines.append(f"Evaluation: {sign}{evaluation:.2f}")
    return lines


def print_banner(text, char="="):
    width = min(max(len(text) + 4, 20), terminal_width())
    print(char * width)
    print(text.center(width))
    print(char * width)
