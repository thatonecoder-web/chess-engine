from .board import Board
from .moves import Move
from .AI.ai_player import AIPlayer


def _choose_mode():
    print("1) Human vs Human")
    print("2) Human vs AI")
    choice = input("Select mode (1/2): ").strip()
    return "ai" if choice == "2" else "human"


def _choose_ai_color():
    choice = input("Play as White or Black? (w/b): ").strip().lower()
    return "black" if choice == "w" else "white"


def main():
    board = Board()
    mode = _choose_mode()

    ai_color = None
    ai = None
    if mode == "ai":
        ai_color = _choose_ai_color()
        ai = AIPlayer(color=ai_color)
        print(f"AI is playing {ai_color}.")

    while True:
        board.display()

        if board.is_game_over():
            if board.is_checkmate(board.turn):
                winner = "Black" if board.turn == "white" else "White"
                print(f"Checkmate — {winner} wins.")
            else:
                print("Stalemate — draw.")
            break

        print(f"{board.turn.capitalize()}'s turn")

        if ai is not None and board.turn == ai_color:
            move = ai.choose_move(board)
            if move is None:
                print("AI has no legal move.")
                break
            board.make_move(move)
            stats = ai.last_search_stats
            depth_note = f" (depth {stats.depth_reached}, {stats.nodes:,} nodes)" if stats else ""
            print(f"AI played: {move}{depth_note}")
            continue

        command = input("Move (e2 e4) or 'quit': ")

        if command.lower() == "quit":
            break

        parts = command.split()

        if len(parts) != 2:
            print("Invalid input. Use: e2 e4")
            continue

        board_before = board.copy()
        move = Move(parts[0], parts[1])

        if board.make_move(move):
            print(f"Moved: {move}")
            if ai is not None:
                ai.observe_player_move(board_before, move)
        else:
            print("Invalid move.")


if __name__ == "__main__":
    main()