class Move:
    def __init__(self, start, end, promotion=None):
        self.start = start
        self.end = end
        self.promotion = promotion

    def __str__(self):
        return f"{self.start} -> {self.end}"

    def get_coordinates(self, position):
        file = ord(position[0]) - ord("a")
        rank = 8 - int(position[1])

        return rank, file