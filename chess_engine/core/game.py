"""Game record and history tracking for chess games."""

from copy import deepcopy
from .board import Board
from .moves import Move


class GameHistory:
    """Track game moves and state history for replay, undo/redo, and PGN support."""

    def __init__(self):
        self.moves = []
        self.board_states = []  # FEN at each move
        self.move_numbers = []
        self.current_index = -1

    def add_move(self, move, board):
        """Record a move and the resulting board state, truncating the
        redo stack if we're not at the end of the history."""
        self.current_index += 1

        if self.current_index < len(self.moves):
            self.moves = self.moves[:self.current_index]
            self.board_states = self.board_states[:self.current_index]
            self.move_numbers = self.move_numbers[:self.current_index]

        self.moves.append(move)
        self.board_states.append(board.to_fen())
        # move numbers run 1, 1, 2, 2, 3, 3, ... -- increments on black's move
        if len(self.move_numbers) == 0:
            self.move_numbers.append(1)
        else:
            last_move_number = self.move_numbers[-1]
            if len(self.moves) % 2 == 0:
                self.move_numbers.append(last_move_number + 1)
            else:
                self.move_numbers.append(last_move_number)

    def can_undo(self):
        return self.current_index >= 0

    def can_redo(self):
        return self.current_index < len(self.moves) - 1

    def undo(self, board):
        """Undo the last move and restore the board state."""
        if not self.can_undo():
            return False

        if self.current_index == 0:
            board.__init__()
        else:
            board.from_fen(self.board_states[self.current_index - 1])

        self.current_index -= 1
        return True

    def redo(self, board):
        if not self.can_redo():
            return False

        self.current_index += 1
        move = self.moves[self.current_index]
        board.make_move(move)
        return True

    def get_current_move_number(self):
        if self.current_index < 0:
            return 1
        return self.move_numbers[self.current_index]

    def get_all_moves(self):
        return self.moves.copy()

    def get_moves_up_to_current(self):
        """Return moves up to and including the current position."""
        return self.moves[:self.current_index + 1]


class Game:
    """Represent a complete chess game with board, history, and metadata."""

    def __init__(self):
        self.board = Board()
        self.initial_fen = self.board.to_fen()
        self.history = GameHistory()
        self.metadata = {
            "Event": "?",
            "Site": "?",
            "Date": "????.??.??",
            "Round": "?",
            "White": "?",
            "Black": "?",
            "Result": "*",
        }

    def make_move(self, move):
        """Make a move and record it in history."""
        if not self.board.make_move(move):
            return False
        self.history.add_move(move, self.board)
        return True

    def undo(self):
        return self.history.undo(self.board)

    def redo(self):
        return self.history.redo(self.board)

    def set_metadata(self, key, value):
        self.metadata[key] = value

    def get_metadata(self, key):
        return self.metadata.get(key, "?")

    def to_pgn(self):
        """Generate a PGN (Portable Game Notation) string of the game."""
        lines = []

        for key in ["Event", "Site", "Date", "Round", "White", "Black", "Result"]:
            value = self.metadata.get(key, "?")
            lines.append(f'[{key} "{value}"]')

        lines.append("")

        move_text = []
        moves = self.history.get_all_moves()
        for i, move in enumerate(moves):
            move_number = i // 2 + 1
            if i % 2 == 0:
                move_text.append(f"{move_number}.")
            move_text.append(move.to_algebraic())

        lines.append(" ".join(move_text))
        lines.append(self.metadata.get("Result", "*"))

        return "\n".join(lines)

    def from_pgn(self, pgn_text):
        """Parse a PGN string and load the game."""
        lines = pgn_text.split("\n")
        in_header = True
        moves_section = []

        for line in lines:
            line = line.strip()
            if not line:
                in_header = False
                continue

            if in_header and line.startswith("["):
                key_start = line.find("[") + 1
                key_end = line.find(" ")
                value_start = line.find('"') + 1
                value_end = line.rfind('"')

                if key_end > key_start and value_end > value_start:
                    key = line[key_start:key_end]
                    value = line[value_start:value_end]
                    self.metadata[key] = value

            elif not in_header:
                moves_section.append(line)

        moves_text = " ".join(moves_section)
        tokens = moves_text.split()

        for token in tokens:
            if token.endswith(".") or token == "*":  # move numbers like "1."
                continue

            if len(token) == 4 and token[0].isalpha() and token[2].isalpha():
                move = Move(token[0:2], token[2:4])
                if not self.make_move(move):
                    raise ValueError(f"Illegal move: {token}")

    def save_to_file(self, filename):
        """Save the game to a file in JSON format."""
        import json

        data = {
            "metadata": self.metadata,
            "moves": [m.to_algebraic() for m in self.history.get_moves_up_to_current()],
            "initial_fen": self.initial_fen,
            "final_fen": self.board.to_fen(),
        }

        with open(filename, "w") as f:
            json.dump(data, f, indent=2)

    def load_from_file(self, filename):
        """Load a game from a JSON file."""
        import json

        with open(filename, "r") as f:
            data = json.load(f)

        metadata = data.get("metadata", {})
        if not isinstance(metadata, dict):
            raise ValueError("metadata must be an object")

        moves = data.get("moves", [])
        if not isinstance(moves, list) or any(not isinstance(item, str) for item in moves):
            raise ValueError("moves must be a list of strings")

        loaded_game = Game()
        loaded_game.metadata.update(metadata)
        initial_fen = data.get("initial_fen")
        if initial_fen is not None:
            loaded_game.board.from_fen(initial_fen)
            loaded_game.initial_fen = initial_fen

        for move_str in moves:
            if len(move_str) not in (4, 5):
                raise ValueError(f"Invalid move: {move_str}")
            promotion = move_str[4] if len(move_str) == 5 else None
            move = Move(move_str[0:2], move_str[2:4], promotion=promotion)
            if not loaded_game.make_move(move):
                raise ValueError(f"Illegal move: {move_str}")

        final_fen = data.get("final_fen")
        if final_fen is not None and loaded_game.board.to_fen() != final_fen:
            raise ValueError("saved position does not match the move history")

        self.metadata = loaded_game.metadata
        self.board = loaded_game.board
        self.history = loaded_game.history
