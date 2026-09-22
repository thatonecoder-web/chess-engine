"""The main menu: dispatches to a game (play.py), the Guide Book, the
Interactive Tutorial, or Settings, looping back until Exit."""

from .settings import Settings
from .play import play_game
from .guide import run_guide
from .tutorial import run_tutorial
from ..ai.difficulty_levels import level_names, make_ai_player
from . import ui

MENU_TEXT = """\
+----------------------------------------+
|            CHESS ENGINE                |
|                                        |
|  1. Player vs Player                   |
|  2. Player vs AI                       |
|  3. AI vs AI                           |
|                                        |
|  4. Interactive Tutorial               |
|  5. Guide Book                         |
|  6. Settings                           |
|  7. Exit                               |
+----------------------------------------+"""


def _choose_from_list(prompt, options):
    for i, option in enumerate(options, start=1):
        print(f"  {i}. {option}")
    while True:
        choice = input(prompt).strip()
        if choice.isdigit() and 1 <= int(choice) <= len(options):
            return options[int(choice) - 1]
        print(f"Please enter a number from 1 to {len(options)}.")


def _choose_side():
    choice = input("Play as White or Black? (w/b): ").strip().lower()
    return "black" if choice.startswith("b") else "white"


def _settings_menu(settings):
    while True:
        print()
        print("SETTINGS")
        print("=" * 40)
        for line in settings.describe():
            print(line)
        print("  0. Back to main menu")
        choice = input("\nToggle an option (number), or 0 to go back: ").strip()
        if choice == "0" or choice == "":
            return
        if not settings.toggle_option(choice):
            print("Please enter a number from the list above.")


def _run_pvp(settings):
    play_game("pvp", settings, title="Player vs Player")


def _run_pvai(settings):
    side = _choose_side()
    ai_side = "black" if side == "white" else "white"
    print()
    level = _choose_from_list("Select AI difficulty (number): ", level_names())
    ai = make_ai_player(ai_side, level, adaptive=True)
    print(f"\nYou are playing {side.capitalize()}. AI ({level}) plays {ai_side.capitalize()}.")
    input("(press Enter to start) ")

    white_ai = ai if ai_side == "white" else None
    black_ai = ai if ai_side == "black" else None
    play_game("pvai", settings, white_ai=white_ai, black_ai=black_ai,
              title=f"Player vs AI ({level})")


def _run_aivai(settings):
    print("White AI:")
    white_level = _choose_from_list("Select difficulty (number): ", level_names())
    print("\nBlack AI:")
    black_level = _choose_from_list("Select difficulty (number): ", level_names())

    white_ai = make_ai_player("white", white_level, adaptive=False)
    black_ai = make_ai_player("black", black_level, adaptive=False)

    print(f"\nWhite: {white_level}  vs  Black: {black_level}")
    input("(press Enter to start — the engines will play automatically) ")

    play_game("aivai", settings, white_ai=white_ai, black_ai=black_ai,
              title=f"AI vs AI — White ({white_level}) vs Black ({black_level})")


def main_menu():
    settings = Settings()

    while True:
        ui.clear_screen() if settings.clear_screen else None
        print(MENU_TEXT)
        choice = input("\nSelect an option: ").strip()

        if choice == "1":
            _run_pvp(settings)
        elif choice == "2":
            _run_pvai(settings)
        elif choice == "3":
            _run_aivai(settings)
        elif choice == "4":
            run_tutorial(settings=settings)
        elif choice == "5":
            run_guide()
        elif choice == "6":
            _settings_menu(settings)
        elif choice == "7" or choice.lower() in ("exit", "quit", "q"):
            print("Goodbye!")
            return
        else:
            print("Please select an option from the menu (1-7).")
            input("(press Enter to continue) ")
