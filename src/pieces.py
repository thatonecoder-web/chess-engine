class Piece:
    def __init__(self, symbol, color):
        self.symbol = symbol
        self.color = color

    def __str__(self):
        return self.symbol


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