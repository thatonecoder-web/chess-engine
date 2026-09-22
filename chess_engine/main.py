"""Program entry point: `python -m chess_engine.main` starts the main
menu (chess_engine.cli.menu.main_menu)."""

from .cli.menu import main_menu


def main():
    try:
        main_menu()
    except KeyboardInterrupt:
        print("\nGoodbye!")


if __name__ == "__main__":
    main()
