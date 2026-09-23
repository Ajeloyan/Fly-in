import arcade
from pathlib import Path
from .. parser import MapParser
from ..pathfinding import Pathfinder
from .. simulation import Simulation
from .simulation_view import SimulationView
from ..models.errors import FlyInError


class MapListView(arcade.View):
    """Lists the maps of one category and launches a simulation on click."""
    def __init__(self, category: str) -> None:
        super().__init__()
        self.category = category
        self.maps = sorted(Path(f"maps/{category}").glob("*.txt"))
        self.error_message: str | None = None

    def on_show_view(self) -> None:
        self.window.background_color = arcade.color.DARK_SLATE_GRAY

    def _button_box(self, i: int) -> tuple[float, float, float, float]:
        left = self.window.width / 2 - 150
        right = self.window.width / 2 + 150
        top = self.window.height - 100 - i * 50
        bottom = top - 50
        return left, right, bottom, top

    def _back_box(self) -> tuple[float, float, float, float]:
        left = 20
        right = 120
        bottom = self.window.height - 60
        top = self.window.height - 20
        return left, right, bottom, top

    def on_draw(self) -> None:
        self.clear()
        left, right, bottom, top = self._back_box()
        arcade.draw_lrbt_rectangle_filled(left, right, bottom, top, arcade.color.RED)
        arcade.draw_text("Back", (left + right) / 2, (bottom + top) / 2,
                         arcade.color.WHITE, 16, anchor_x="center", anchor_y="center")
        for i, map_path in enumerate(self.maps):
            left, right, bottom, top = self._button_box(i)
            arcade.draw_lrbt_rectangle_filled(left, right, bottom, top, arcade.color.BLUE_GRAY)
            arcade.draw_text(map_path.stem, (left + right) / 2, (bottom + top) / 2,
                             arcade.color.WHITE, 16, anchor_x="center", anchor_y="center")
        if self.error_message is not None:
            arcade.draw_text(self.error_message, self.window.width / 2, 30,
                             arcade.color.RED, 16, anchor_x="center", anchor_y="center")

    def on_mouse_press(self, x: float, y: float, button: int, modifiers: int) -> None:
        left, right, bottom, top = self._back_box()
        if left <= x <= right and bottom <= y <= top:
            from .menu_view import MenuView
            self.window.show_view(MenuView())
            return
        for i, map_path in enumerate(self.maps):
            left, right, bottom, top = self._button_box(i)
            if left <= x <= right and bottom <= y <= top:
                try:
                    graph, drones = MapParser().parse(str(map_path))
                    assert graph.end is not None
                    assert graph.start is not None
                    paths = Pathfinder().yen(graph, graph.start, graph.end, 4)
                    history = Simulation(drones, paths, graph).launch()
                except FlyInError as e:
                    self.error_message = str(e)
                    return
                for turn in history:
                    print(" ".join(turn))
                self.window.show_view(SimulationView(graph, history))
