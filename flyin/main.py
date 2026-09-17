from .parser import MapParser
from .models.errors import ParseError
from .simulation import Simulation
import sys


def main():
    if len(sys.argv) < 2:
        print("Usage: python -m flyin.main <map_file>")
        sys.exit(1)

    filepath = sys.argv[1]
    try:
        graph, drones = MapParser().parse(filepath)
        path = [graph.start, graph.zones["waypoint1"], graph.zones["waypoint2"], graph.end]
        sim = Simulation(drones, path, graph)
        sim.launch()
    except ParseError as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()