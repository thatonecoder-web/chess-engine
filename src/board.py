from .pieces import Pawn, Knight, Bishop, Rook, Queen, King
from .moves import Move


class Board:
    def __init__(self):
        self.board = self._create_board()
        self.turn = "white"

    def _create_board(self):
        board = [[None for _ in range(8)] for _ in range(8)]

        # Black pieces
        board[0] = [
            Rook("r", "black"),
            Knight("n", "black"),
            Bishop("b", "black"),
            Queen("q", "black"),
            King("k", "black"),
            Bishop("b", "black"),
            Knight("n", "black"),
            Rook("r", "black"),
        ]

        board[1] = [
            Pawn("p", "black") for _ in range(8)
        ]

        # White pieces
        board[6] = [
            Pawn("P", "white") for _ in range(8)
        ]

        board[7] = [
            Rook("R", "white"),
            Knight("N", "white"),
            Bishop("B", "white"),
            Queen("Q", "white"),
            King("K", "white"),
            Bishop("B", "white"),
            Knight("N", "white"),
            Rook("R", "white"),
        ]

        return board

    def display(self):
        print("  a b c d e f g h")

        for row in range(8):
            rank = 8 - row

            pieces = []

            for piece in self.board[row]:
                pieces.append(str(piece) if piece else ".")

            print(f"{rank} {' '.join(pieces)}")

        print()

    def make_move(self, move):
        start_row, start_col = move.get_coordinates(move.start)
        end_row, end_col = move.get_coordinates(move.end)

        piece = self.board[start_row][start_col]
        target = self.board[end_row][end_col]

        # No piece at starting position
        if piece is None:
            return False

        # Wrong player's turn
        if piece.color != self.turn:
            return False

        # Cannot capture your own piece
        if target is not None and target.color == self.turn:
            return False

        # Move the piece
        self.board[end_row][end_col] = piece
        self.board[start_row][start_col] = None

        # Switch turns
        self.turn = "black" if self.turn == "white" else "white"

        return True