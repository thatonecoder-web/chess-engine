"""Parses the text a player types during a game into a structured
command -- the single source of truth for the engine's command syntax
(also documented in the Guide Book -- see guide.py).

Recognized commands:
    p <from> <to> [promotion]   make a move, e.g. "p e2 e4" or "p e7 e8 q"
    moves [square]              list legal moves (optionally from one square)
    history                     show the move list so far
    undo                        undo the last move
    redo                        redo the last undone move
    fen                         show the current position as FEN
    save <filename>             save the game to a JSON file
    load <filename>             load a game from a JSON file
    help                        show this command list
    guide                       open the Guide Book
    quit                        leave the game and return to the main menu
"""

from collections import namedtuple

Command = namedtuple("Command", ["name", "args"])

KNOWN_COMMANDS = (
    "move", "moves", "history", "undo", "redo", "fen",
    "save", "load", "help", "guide", "quit",
)

HELP_TEXT = """Commands:
  p <from> <to> [promo]   make a move, e.g. "p e2 e4" (promo: q/r/b/n, e.g. "p e7 e8 q")
  moves [square]          list legal moves, optionally from one square (e.g. "moves e2")
  history                 show the moves played so far
  undo                    undo the last move
  redo                    redo the last undone move
  fen                     show the current position as FEN
  save <filename>         save the game to a file
  load <filename>         load a game from a file
  help                    show this list
  guide                   open the Guide Book
  quit                    leave this game and return to the main menu"""


def parse_command(raw):
    """Parse one line of player input into a Command.

    Returns Command(name=None, args=[]) for empty/unrecognized input
    so callers can uniformly check `.name` without raising.
    """
    text = (raw or "").strip()
    if not text:
        return Command(None, [])

    parts = text.split()
    head = parts[0].lower()

    if head == "p" and len(parts) >= 3:
        args = {"start": parts[1].lower(), "end": parts[2].lower()}
        if len(parts) >= 4:
            args["promotion"] = parts[3].lower()
        return Command("move", args)

    if head in KNOWN_COMMANDS:
        return Command(head, parts[1:])

    return Command(None, parts)
