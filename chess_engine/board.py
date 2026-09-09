from .check import move_leaves_king_in_check, is_square_attacked
from .rules import is_valid_move

from .pieces import Pawn, Knight, Bishop, Rook, Queen, King
from .moves import Move


class Board:
    def __init__(self):
        self.board = self._create_board()
        self.turn = "white"
        self.previous_move = None
        self.en_passant_target = None

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

        for row in range(8):
            for col in range(8):
                piece = board[row][col]
                if piece is not None:
                    piece.has_moved = False

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

    def _is_castling_move(self, piece, start, end):
        if not isinstance(piece, King):
            return False

        start_row, start_col = start
        end_row, end_col = end

        # The king moves horizontally from e-file to c/g-file.
        return (
            start_row == (7 if piece.color == "white" else 0)
            and start_col == 4
            and end_row == start_row
            and abs(end_col - start_col) == 2
        )

    def _can_castle(self, move):
        start_row, start_col = move.get_coordinates(move.start)
        end_row, end_col = move.get_coordinates(move.end)

        piece = self.board[start_row][start_col]
        if piece is None or not isinstance(piece, King):
            return False

        if piece.has_moved:
            return False

        if start_row != (7 if piece.color == "white" else 0):
            return False

        if start_col != 4:
            return False

        opponent = "black" if piece.color == "white" else "white"

        # If the king is already in check, legal castle is impossible.
        if is_square_attacked(self, start_row, start_col, opponent):
            return False

        if end_col == 6:
            rook_col = 7
            rook = self.board[start_row][rook_col]
            if not isinstance(rook, Rook) or rook.color != piece.color:
                return False
            if rook.has_moved:
                return False
            if self.board[start_row][5] is not None or self.board[start_row][6] is not None:
                return False
            path = [(start_row, 5), (start_row, 6)]

        elif end_col == 2:
            rook_col = 0
            rook = self.board[start_row][rook_col]
            if not isinstance(rook, Rook) or rook.color != piece.color:
                return False
            if rook.has_moved:
                return False
            if self.board[start_row][1] is not None or self.board[start_row][2] is not None or self.board[start_row][3] is not None:
                return False
            path = [(start_row, 3), (start_row, 2)]

        else:
            return False

        # Reject when the path or destination square is attacked.
        for row, col in path:
            if is_square_attacked(self, row, col, opponent):
                return False

        if is_square_attacked(self, end_row, end_col, opponent):
            return False

        return True

    def _promote_pawn(self, piece, move):
        if not isinstance(piece, Pawn):
            return piece

        end_row, end_col = move.get_coordinates(move.end)
        promotion = (move.promotion or "q").lower()
        color = piece.color

        if color == "white" and end_row == 0:
            if promotion == "r":
                return Rook("R", color)
            if promotion == "b":
                return Bishop("B", color)
            if promotion == "n":
                return Knight("N", color)
            return Queen("Q", color)

        if color == "black" and end_row == 7:
            if promotion == "r":
                return Rook("r", color)
            if promotion == "b":
                return Bishop("b", color)
            if promotion == "n":
                return Knight("n", color)
            return Queen("q", color)

        return piece

    def make_move(self, move):
        start_row, start_col = move.get_coordinates(move.start)
        end_row, end_col = move.get_coordinates(move.end)

        piece = self.board[start_row][start_col]
        target = self.board[end_row][end_col]

        if piece is None:
            return False

        if piece.color != self.turn:
            return False

        if target is not None and target.color == piece.color:
            return False

        # Castling branch: enforce and move rook automatically.
        castle_move = self._is_castling_move(piece, (start_row, start_col), (end_row, end_col))
        if castle_move:
            if not self._can_castle(move):
                return False

        # En passant branch: only legal if pawn diagonal capture lands on empty square and target is correct.
        elif (
            isinstance(piece, Pawn)
            and target is None
            and abs(end_col - start_col) == 1
            and abs(end_row - start_row) == 1
        ):
            if self.en_passant_target != (end_row, end_col):
                return False

            captured = self.board[start_row][end_col]
            if captured is None or not isinstance(captured, Pawn) or captured.color == piece.color:
                return False

        # Generic movement validation. Castling is permitted through the castle branch; for non-castling,
        # we let the regular rules engine decide whether the shape is legal.
        if not castle_move and not is_valid_move(self, (start_row, start_col), (end_row, end_col)):
            return False

        # Cannot let your own king remain in check after the move.
        if move_leaves_king_in_check(self, (start_row, start_col), (end_row, end_col)):
            return False

        # Rook relocation for castling.
        if castle_move:
            if end_col == 6:
                rook_col = 7
                rook_target_col = 5
            else:
                rook_col = 0
                rook_target_col = 3

            rook = self.board[start_row][rook_col]
            self.board[start_row][rook_target_col] = rook
            self.board[start_row][rook_col] = None
            rook.has_moved = True

        # Remove the captured pawn for en passant.
        if (
            isinstance(piece, Pawn)
            and target is None
            and abs(end_col - start_col) == 1
            and abs(end_row - start_row) == 1
            and self.en_passant_target == (end_row, end_col)
        ):
            self.board[start_row][end_col] = None

        # Execute common move.
        self.board[end_row][end_col] = piece
        self.board[start_row][start_col] = None

        # Promotion.
        if isinstance(piece, Pawn) and (end_row == 0 or end_row == 7):
            self.board[end_row][end_col] = self._promote_pawn(piece, move)

        # Record movement history for king and rook.
        piece.has_moved = True
        if isinstance(piece, Rook):
            piece.has_moved = True
        if isinstance(piece, King):
            piece.has_moved = True

        # Track the square available for the next en passant response.
        if isinstance(piece, Pawn) and abs(end_row - start_row) == 2:
            self.en_passant_target = ((start_row + end_row) // 2, start_col)
        else:
            self.en_passant_target = None

        # Advance turn and remember this move.
        self.turn = "black" if self.turn == "white" else "white"
        self.previous_move = move

        return True
