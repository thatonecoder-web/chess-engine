from .board import Board
from .moves import Move


def main():
    board = Board()

    while True:
        board.display()

        print(f"{board.turn.capitalize()}'s turn")

        command = input("Move (e2 e4) or 'quit': ")

        if command.lower() == "quit":
            break

        parts = command.split()

        if len(parts) != 2:
            print("Invalid input. Use: e2 e4")
            continue

        move = Move(parts[0], parts[1])

        if board.make_move(move):
            print(f"Moved: {move}")
        else:
            print("Invalid move.")


if __name__ == "__main__":
    main()