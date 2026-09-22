class Move:
    def __init__(self, start, end, promotion=None):
        self.start = start
        self.end = end
        self.promotion = promotion

    def __str__(self):
        return f"{self.start} -> {self.end}"

    def __repr__(self):
        promo = f", promotion={self.promotion!r}" if self.promotion else ""
        return f"Move({self.start!r}, {self.end!r}{promo})"

    def __eq__(self, other):
        """Value equality on (start, end, promotion): move generation
        creates a fresh Move each call, so without this, a human's
        input move would never compare equal to the "same" move
        returned by search/generation."""
        if not isinstance(other, Move):
            return NotImplemented

        def _promo(p):
            return (p or "").lower()

        return (
            self.start == other.start
            and self.end == other.end
            and _promo(self.promotion) == _promo(other.promotion)
        )

    def __hash__(self):
        return hash((self.start, self.end, (self.promotion or "").lower()))

    def to_algebraic(self):
        """Compact square-pair notation, e.g. "e2e4"."""
        promotion = (self.promotion or "").lower()
        return f"{self.start}{self.end}{promotion}"

    def get_coordinates(self, position):
        file = ord(position[0]) - ord("a")
        rank = 8 - int(position[1])

        return rank, file