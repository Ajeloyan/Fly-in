from .parser import MapParser
from .models.errors import ParseError
from .simulation import Simulation
import sys
from .pathfinding import Pathfinder
from .visual.window import Window
import arcade
from .visual.simulation_view import SimulationView
from .visual.menu_view import MenuView


def main() -> None:
    if len(sys.argv) >= 2:
        filepath = sys.argv[1]
        try:
            graph, drones = MapParser().parse(filepath)
            pathfinder = Pathfinder()
            path = pathfinder.find_path(graph)
            sim = Simulation(drones, path, graph)
            history = sim.launch()
            for turn in history:
                print(" ".join(turn))
        except ParseError as e:
            print(f"Error: {e}")
            sys.exit(1)
        window = Window()
        window.show_view(SimulationView(graph, history))
    else:
        window = Window()
        window.show_view(MenuView())
    arcade.run()
    print(type(arcade.color.BLACK))


if __name__ == "__main__":
    main()
