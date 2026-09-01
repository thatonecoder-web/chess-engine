from src.moves import Move


def test_move_creation():
    move = Move("e2", "e4")

    assert move.start == "e2"
    assert move.end == "e4"


def test_move_string():
    move = Move("e2", "e4")

    assert str(move) == "e2 -> e4"


def test_coordinate_conversion():
    move = Move("e2", "e4")

    assert move.get_coordinates("e2") == (6, 4)
    assert move.get_coordinates("e4") == (4, 4)