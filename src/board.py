from .pieces import Pawn, Knight, Bishop, Rook, Queen, King


class Board:
    def __init__(self):
        self.board = self._create_board()

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