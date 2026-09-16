class Piece:
    def __init__(self, symbol, color):
        self.symbol = symbol
        self.color = color
        self.has_moved = False

    def __str__(self):
        return self.symbol

    def clone(self):
        """Return an independent copy of this piece.

        Used by Board.copy() so search can explore hypothetical lines
        without mutating (via has_moved) the pieces on the "real" board.
        """
        new_piece = self.__class__(self.symbol, self.color)
        new_piece.has_moved = self.has_moved
        return new_piece


class Pawn(Piece):
    pass


class Knight(Piece):
    pass


class Bishop(Piece):
    pass


class Rook(Piece):
    pass


class Queen(Piece):
    pass


class King(Piece):
    pass