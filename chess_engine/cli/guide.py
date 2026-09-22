"""The built-in Guide Book: a chess manual plus a reference for the
engine's own commands, browsable from the main menu or the "guide"
command mid-game. TOPICS is plain (title, body) data so it can be
listed or rendered by more than one caller."""

from .commands import HELP_TEXT

TOPICS = [
    ("How Chess Works",
     "Chess is played on an 8x8 board between two players, White and Black.\n"
     "White always moves first, and players alternate turns. Each type of\n"
     "piece moves differently, and the goal is to checkmate your opponent's\n"
     "king — put it under attack with no legal way to escape."),

    ("The Chessboard",
     "The board has 8 files (columns), labeled a-h left to right from White's\n"
     "side, and 8 ranks (rows), labeled 1-8 bottom to top from White's side.\n"
     "Every square has a unique name formed from its file and rank, e.g. e4.\n"
     "White's pieces start on ranks 1-2, Black's on ranks 7-8."),

    ("Chess Pieces",
     "Each side starts with 16 pieces:\n"
     "  King (1)   - moves one square in any direction\n"
     "  Queen (1)  - moves any number of squares in any direction\n"
     "  Rook (2)   - moves any number of squares horizontally or vertically\n"
     "  Bishop (2) - moves any number of squares diagonally\n"
     "  Knight (2) - moves in an L-shape: two squares one way, one square\n"
     "               perpendicular, and can jump over other pieces\n"
     "  Pawn (8)   - moves forward one square (two from its starting square),\n"
     "               captures one square diagonally forward, and cannot move\n"
     "               backward"),

    ("Legal Moves",
     "A move is only legal if it follows that piece's movement pattern, does\n"
     "not move through other pieces (except the Knight), does not land on a\n"
     "piece of your own color, and does not leave your own king in check."),

    ("Capturing",
     "Capturing an opponent's piece is done by moving one of your pieces to\n"
     "the square that piece occupies (following your piece's normal movement\n"
     "rules). The captured piece is removed from the board. Pawns are the\n"
     "exception: they capture diagonally, not in the direction they move."),

    ("Check",
     "A king is 'in check' when it is under attack by an opponent's piece.\n"
     "You must get out of check immediately — by moving the king to safety,\n"
     "blocking the attack with another piece, or capturing the attacker. You\n"
     "may never make a move that leaves your own king in check."),

    ("Checkmate",
     "Checkmate occurs when a king is in check and there is no legal move\n"
     "that removes the check. This ends the game immediately — the side\n"
     "delivering checkmate wins."),

    ("Stalemate",
     "Stalemate occurs when the side to move is NOT in check but has no\n"
     "legal move available. This ends the game immediately as a draw — no\n"
     "one wins."),

    ("Castling",
     "Castling is a special king-and-rook move: the king moves two squares\n"
     "toward a rook, and that rook moves to the square the king crossed.\n"
     "It is only legal if neither piece has moved yet, no pieces stand\n"
     "between them, the king is not currently in check, and the king does\n"
     "not pass through or land on a square under attack.\n"
     "Command: use the normal move syntax with the king's start and end\n"
     "square, e.g. \"p e1 g1\" for White's kingside castle."),

    ("En Passant",
     "If an opponent's pawn moves two squares forward from its starting\n"
     "square and lands beside one of your pawns, you may capture it 'in\n"
     "passing' as if it had only moved one square. This capture must be\n"
     "made immediately, on your very next move, or the right is lost."),

    ("Promotion",
     "When a pawn reaches the far rank (rank 8 for White, rank 1 for Black),\n"
     "it must be promoted to a Queen, Rook, Bishop, or Knight of the same\n"
     "color. To choose, add the piece letter to your move, e.g. \"p e7 e8 q\"\n"
     "promotes to a Queen. Leaving it off defaults to a Queen."),

    ("Algebraic Notation",
     "This engine uses square-pair notation for input and history: a move\n"
     "is written as its start square followed by its end square, e.g. e2e4\n"
     "for a pawn moving from e2 to e4. This is simpler than full Standard\n"
     "Algebraic Notation (SAN, e.g. \"Nf3\") but describes the same moves."),

    ("FEN",
     "FEN (Forsyth-Edwards Notation) is a compact way to describe a full\n"
     "board position — piece placement, whose turn it is, castling rights,\n"
     "the en passant target square, and move counters — as one line of\n"
     "text. Use the \"fen\" command to see the current position's FEN, which\n"
     "you can save or share and later reload."),

    ("Playing Against the AI",
     "Choose \"Player vs AI\" from the main menu, pick which color you'd\n"
     "like to play, and select a difficulty level. The AI adapts as the\n"
     "game goes on: it re-estimates how well you're playing after every\n"
     "move and adjusts its own strength to stay a fair match."),

    ("AI Difficulty",
     "Difficulty ranges from Beginner (shallow, fairly random search) to\n"
     "Maximum (deep search, always plays what it judges the objectively\n"
     "strongest move). In Player vs AI, difficulty is a starting point that\n"
     "adapts to you; in AI vs AI, each side's difficulty stays fixed for\n"
     "the whole game so you can compare engines fairly."),

    ("Engine Commands", HELP_TEXT),

    ("How to Use This Engine",
     "From the main menu, pick a mode to start playing, the Interactive\n"
     "Tutorial if this is your first time, or the Guide Book (this manual)\n"
     "at any point. During a game, type moves as \"p <from> <to>\", or use\n"
     "any of the commands listed under 'Engine Commands' — type \"help\"\n"
     "any time you forget them."),
]

TOPIC_TITLES = [title for title, _ in TOPICS]


def run_guide(reader=input, writer=print):
    """Interactive Guide Book viewer.

    reader/writer are injected so tests (and any future non-terminal
    front end) can drive this without real stdin/stdout.
    """
    while True:
        writer("")
        writer("=" * 40)
        writer("           GUIDE BOOK")
        writer("=" * 40)
        for i, title in enumerate(TOPIC_TITLES, start=1):
            writer(f"  {i:>2}. {title}")
        writer("   0. Back to menu")
        writer("")
        choice = reader("Select a topic (number), or 0 to go back: ").strip()

        if choice in ("0", ""):
            return

        if not choice.isdigit() or not (1 <= int(choice) <= len(TOPICS)):
            writer("Please enter a number from the list above.")
            continue

        title, body = TOPICS[int(choice) - 1]
        writer("")
        writer("-" * 40)
        writer(title)
        writer("-" * 40)
        writer(body)
        reader("\n(press Enter to return to the topic list) ")
