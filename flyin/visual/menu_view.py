import arcade

CATEGORIES = ["easy", "medium", "hard", "challenger"]


class MenuView(arcade.View):
    """The landing screen: lets the user pick a map difficulty category."""
    def on_show_view(self) -> None:
        self.window.background_color = arcade.color.DARK_SLATE_GRAY

    def _button_box(self, i: int) -> tuple[float, float, float, float]:
        left = self.window.width / 2 - 100
        right = self.window.width / 2 + 100
        top = self.window.height - 500 - i * 80
        bottom = top - 50
        return left, right, bottom, top

    def on_draw(self) -> None:
        self.clear()
        arcade.draw_text("FLY-IN", self.window.width / 2, self.window.height - 200,
                         arcade.color.BRONZE, 48, anchor_x="center", font_name="Kenney Blocks")
        for i, category in enumerate(CATEGORIES):
            left, right, bottom, top = self._button_box(i)
            arcade.draw_lrbt_rectangle_filled(left, right, bottom, top, arcade.color.BLUE_GRAY)
            arcade.draw_text(category, (left + right) / 2, (bottom + top) / 2,
                             arcade.color.WHITE, 18, anchor_x="center", anchor_y="center")

    def on_mouse_press(self, x: float, y: float, button: int, modifiers: int) -> None:
        for i, category in enumerate(CATEGORIES):
            left, right, bottom, top = self._button_box(i)
            if left <= x <= right and bottom <= y <= top:
                from .map_list_view import MapListView
                self.window.show_view(MapListView(category))
