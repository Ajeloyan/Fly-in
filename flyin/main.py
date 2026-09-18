from .parser import MapParser
from .models.errors import ParseError
from .simulation import Simulation
import sys
from .pathfinding import Pathfinder


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: python -m flyin.main <map_file>")
        sys.exit(1)

    filepath = sys.argv[1]
    try:
        graph, drones = MapParser().parse(filepath)
        pathfinder = Pathfinder()
        path = pathfinder.find_path(graph)
        sim = Simulation(drones, path, graph)
        sim.launch()
    except ParseError as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
