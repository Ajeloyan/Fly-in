from .models.graph import Graph
from .models.zone import Zone
from math import inf


class Pathfinder:
    def __init__(self) -> None:
        pass

    def find_path(self, graph: Graph) -> list[Zone]:
        assert graph.end is not None
        distances: dict[Zone, float] = {zone: (0 if zone == graph.start else
                                               inf) for zone in graph.zones.values()}
        came_from: dict[Zone, Zone] = {}
        unvisited = set(graph.zones.values())
        while unvisited:
            current = min(unvisited, key=lambda zone: distances[zone])
            unvisited.remove(current)
            for c in graph.adjacency[current.name]:
                neighbor = c.zone_b if c.zone_a == current else c.zone_a
                if neighbor.is_accessible() is False:
                    continue
                cost = distances[current] + neighbor.movement_cost()
                if cost < distances[neighbor]:
                    distances[neighbor] = cost
                    came_from[neighbor] = current
        current = graph.end
        path = [current]
        while current != graph.start:
            path.append(came_from[current])
            current = came_from[current]
        path.reverse()
        return path
