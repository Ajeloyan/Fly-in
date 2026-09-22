import arcade
from pathlib import Path
from ..parser import MapParser
from ..simulation import Simulation
from ..pathfinding import Pathfinder
from .simulation_view import SimulationView


class MenuView(arcade.View):
    def __init__(self) -> None:
        super().__init__()
        self.maps = sorted(Path("maps").rglob("*.txt"))

    def on_show_view(self) -> None:
        self.window.background_color = arcade.color.BANANA_MANIA

    def on_draw(self) -> None:
        self.clear()
        for i, map_path in enumerate(self.maps):
            y = self.window.height - 50 - i * 30
            arcade.draw_text(str(map_path), 50, y, arcade.color.WHITE, 16)

    def on_mouse_press(self, x: float, y: float, button: int, modifiers: int) -> None:
        for i, map_path in enumerate(self.maps):
            line_y = self.window.height - 50 - i * 30
            if abs(y - line_y) <= 15:
                graph, drones = MapParser().parse(str(map_path))
                path = Pathfinder().find_path(graph)
                history = Simulation(drones, path, graph).launch()
                for turn in history:
                    print(" ".join(turn))
                self.window.show_view(SimulationView(graph, history))
