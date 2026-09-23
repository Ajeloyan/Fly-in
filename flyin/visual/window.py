import arcade
from .menu_view import MenuView


class Window(arcade.Window):
    """The application's top-level arcade window, showing an initial view."""
    def __init__(self, initial_view: arcade.View | None = None) -> None:
        super().__init__(2000, 1200, "Fly-in")
        if initial_view is None:
            self.show_view(MenuView())
        else:
            self.show_view(initial_view)
