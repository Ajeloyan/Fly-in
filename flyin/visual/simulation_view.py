import arcade
from ..models.graph import Graph
from ..models.zone import Zone
from arcade.types import Color


class SimulationView(arcade.View):
    def __init__(self, graph: Graph, history: list[list[str]]) -> None:
        super().__init__()
        self.graph = graph
        self.history = history
        assert graph.start is not None
        xs = [zone.x for zone in graph.zones.values()]
        ys = [zone.y for zone in graph.zones.values()]
        self.min_x = min(xs)
        self.max_x = max(xs)
        self.min_y = min(ys)
        self.max_y = max(ys)
        self.drone_positions: dict[int, tuple[float, float]] = {}
        self.drone_starts: dict[int, tuple[float, float]] = {}
        self.drone_targets: dict[int, tuple[float, float]] = {}
        for turn in history:
            for move in turn:
                drone_id = int(move[1:].split("-")[0])
                if drone_id not in self.drone_positions:
                    start_pos = self._to_screen(graph.start)
                    self.drone_positions[drone_id] = start_pos
                    self.drone_starts[drone_id] = start_pos
                    self.drone_targets[drone_id] = start_pos
        self.current_turn = 0
        self.timer = 0.0
        self.speed: float = 1.0

    def _zone_color(self, zone: Zone) -> Color:
        if zone.color is None:
            return arcade.color.BLACK
        return getattr(arcade.color, zone.color.upper(), arcade.color.BLACK)

    def on_show_view(self) -> None:
        self.window.background_color = arcade.color.BANANA_MANIA

    def on_draw(self) -> None:
        self.clear()
        for zone in self.graph.zones.values():
            for c in self.graph.adjacency[zone.name]:
                x1, y1 = self._to_screen(c.zone_a)
                x2, y2 = self._to_screen(c.zone_b)
                arcade.draw_line(x1, y1, x2, y2, arcade.color.GRAY)
        for zone in self.graph.zones.values():
            x, y = self._to_screen(zone)
            arcade.draw_circle_filled(x, y, 30, self._zone_color(zone))
        for pos in self.drone_positions.values():
            arcade.draw_circle_filled(pos[0], pos[1], 16, arcade.color.MAGENTA)
        arcade.draw_text(
         f"Turn: {min(self.current_turn, len(self.history))}",
         10, self.window.height - 30, arcade.color.BLACK, 16)
        arcade.draw_text("Press ESC to return to menu", self.window.width - 10, self.window.height
                         - 30, arcade.color.BLACK, 14, anchor_x="right")
        x1_color = arcade.color.GREEN if self.speed == 1.0 else arcade.color.BLACK
        x2_color = arcade.color.GREEN if self.speed == 2.0 else arcade.color.BLACK
        arcade.draw_text("x1", self.window.width - 90, self.window.height - 80, x1_color, 16)
        arcade.draw_text("x2", self.window.width - 40, self.window.height - 80, x2_color, 16)

    def _to_screen(self, zone: Zone) -> tuple[float, float]:
        margin = 50
        width = self.window.width - 2 * margin
        height = self.window.height - 2 * margin
        x_range = self.max_x - self.min_x or 1
        y_range = self.max_y - self.min_y or 1
        screen_x = margin + (zone.x - self.min_x) / x_range * width
        screen_y = margin + (zone.y - self.min_y) / y_range * height
        return screen_x, screen_y

    def _parse_move(self, move: str) -> tuple[int, tuple[float, float]]:
        drone_part, target = move.split("-", 1)
        drone_id = int(drone_part[1:])
        zone = self.graph.zones.get(target)
        if zone is not None:
            return drone_id, self._to_screen(zone)
        zone_a_name, zone_b_name = target.split("-")
        x1, y1 = self._to_screen(self.graph.zones[zone_a_name])
        x2, y2 = self._to_screen(self.graph.zones[zone_b_name])
        return drone_id, ((x1 + x2) / 2, (y1 + y2) / 2)

    def on_update(self, delta_time: float) -> None:
        self.timer += delta_time * self.speed
        t = min(self.timer / 1.0, 1.0)
        for drone_id in self.drone_positions:
            start_x, start_y = self.drone_starts[drone_id]
            target_x, target_y = self.drone_targets[drone_id]
            x = start_x + (target_x - start_x) * t
            y = start_y + (target_y - start_y) * t
            self.drone_positions[drone_id] = (x, y)

        if self.timer >= 1.0 and self.current_turn < len(self.history):
            self.timer = 0.0
            self.drone_starts = dict(self.drone_targets)
            for move in self.history[self.current_turn]:
                drone_id, pos = self._parse_move(move)
                self.drone_targets[drone_id] = pos
            self.current_turn += 1

    def on_key_press(self, key: int, modifiers: int) -> None:
        if key == arcade.key.ESCAPE:
            from .menu_view import MenuView
            self.window.show_view(MenuView())

    def on_mouse_press(self, x: float, y: float, button: int, modifiers: int) -> None:
        button_y = self.window.height - 80
        if button_y - 10 <= y <= button_y + 20:
            if self.window.width - 95 <= x <= self.window.width - 65:
                self.speed = 1.0
            elif self.window.width - 45 <= x <= self.window.width - 15:
                self.speed = 2.0
