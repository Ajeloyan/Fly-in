import arcade
from ..models.graph import Graph


class SimulationView(arcade.View):
    def __init__(self, graph: Graph, history: list[list[str]]) -> None:
        super().__init__()
        self.graph = graph
        self.history = history

        xs = [zone.x for zone in graph.zones.values()]
        ys = [zone.y for zone in graph.zones.values()]
        self.min_x = min(xs)
        self.max_x = max(xs)
        self.min_y = min(ys)
        self.max_y = max(ys)

    def _zone_color(self, zone) -> tuple[int, int, int]:
        if zone.color is None:
            return arcade.color.WHITE
        return getattr(arcade.color, zone.color.upper(), arcade.color.WHITE)

    def on_show_view(self) -> None:
        self.window.background_color = arcade.color.DARK_BLUE

    def on_draw(self) -> None:
        self.clear()
        for zone in self.graph.zones.values():
            for c in self.graph.adjacency[zone.name]:
                x1, y1 = self._to_screen(c.zone_a)
                x2, y2 = self._to_screen(c.zone_b)
                arcade.draw_line(x1, y1, x2, y2, arcade.color.GRAY)
        for zone in self.graph.zones.values():
            x, y = self._to_screen(zone)
            arcade.draw_circle_filled(x, y, 15, self._zone_color(zone))

    def _to_screen(self, zone) -> tuple[float, float]:
        margin = 50
        width = self.window.width - 2 * margin
        height = self.window.height - 2 * margin
        x_range = self.max_x - self.min_x or 1
        y_range = self.max_y - self.min_y or 1
        screen_x = margin + (zone.x - self.min_x) / x_range * width
        screen_y = margin + (zone.y - self.min_y) / y_range * height
        return screen_x, screen_y
