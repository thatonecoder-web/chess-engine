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
        """Two moves are equal when they describe the same square-pair
        move with the same promotion choice, regardless of whether they
        are the same object.

        Move-generation (generate_legal_moves) creates a fresh Move
        instance every time it runs, so without value equality here,
        comparing a move from one search/generation pass against a move
        from another (e.g. a human's input move against the AI's own
        candidate list) would always fail — even for the "same" move.
        """
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
        """Return a simple algebraic-ish one-line notation for a move.

        The engine uses a compact square-pair string for portability and
        testability while the full SAN parser can be layered on later.
        """

        return f"{self.start}{self.end}"

    def get_coordinates(self, position):
        file = ord(position[0]) - ord("a")
        rank = 8 - int(position[1])

        return rank, file