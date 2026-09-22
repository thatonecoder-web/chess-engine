"""Session-wide display/gameplay settings, editable from the Settings
menu. A single mutable Settings object is threaded through the menu,
play loop, and UI so a change takes effect immediately."""

from dataclasses import dataclass


@dataclass
class Settings:
    use_unicode: bool = True          # Unicode glyphs vs plain ASCII letters
    clear_screen: bool = True         # Clean redraw each turn vs scrolling log
    show_captured: bool = True        # Captured-piece tray under the board
    show_ai_search_info: bool = True  # Depth/nodes/eval while AI is "thinking"

    def toggle(self, field_name):
        setattr(self, field_name, not getattr(self, field_name))

    def describe(self):
        return [
            f"1. Unicode pieces:        {'On' if self.use_unicode else 'Off (ASCII letters)'}",
            f"2. Clean terminal redraw: {'On' if self.clear_screen else 'Off (scrolling log)'}",
            f"3. Captured-piece display:{' On' if self.show_captured else ' Off'}",
            f"4. AI search statistics:  {'On' if self.show_ai_search_info else 'Off'}",
        ]

    FIELD_BY_OPTION = {
        "1": "use_unicode",
        "2": "clear_screen",
        "3": "show_captured",
        "4": "show_ai_search_info",
    }

    def toggle_option(self, option):
        field = self.FIELD_BY_OPTION.get(option)
        if field is None:
            return False
        self.toggle(field)
        return True
