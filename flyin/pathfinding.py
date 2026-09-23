from .models.graph import Graph
from .models.zone import Zone, RestrictedZone
from math import inf
from .models.errors import UnreachableEndError, AbsentConnectionError
from .models.connection import Connection


class Pathfinder:
    def __init__(self) -> None:
        pass

    def dijkstra(self, graph: Graph,
                 source: Zone,
                 target: Zone,
                 excluded_connections: set[Connection] | None = None,
                 excluded_zones: set[Zone] | None = None) -> list[Zone]:
        assert target is not None
        distances: dict[Zone, float] = {zone: (0 if zone == source else
                                               inf) for zone in graph.zones.values()}
        came_from: dict[Zone, Zone] = {}
        unvisited = set(graph.zones.values())
        while unvisited:
            current = min(unvisited, key=lambda zone: distances[zone])
            unvisited.remove(current)
            for c in graph.adjacency[current.name]:
                neighbor = c.zone_b if c.zone_a == current else c.zone_a
                if (excluded_connections and c in excluded_connections) or (excluded_zones and
                                                                            neighbor in
                                                                            excluded_zones):
                    continue
                if neighbor.is_accessible() is False:
                    continue
                cost = distances[current] + neighbor.movement_cost()
                if cost < distances[neighbor]:
                    distances[neighbor] = cost
                    came_from[neighbor] = current
        if distances[target] == inf:
            raise UnreachableEndError("End hub is Unreachable, map is incorrect")
        current = target
        path = [current]
        while current != source:
            path.append(came_from[current])
            current = came_from[current]
        path.reverse()
        return path

    def yen(self, graph: Graph, source: Zone, target: Zone, k: int) -> list[list[Zone]]:
        A = [self.dijkstra(graph, source, target)]
        B: list[list[Zone]] = []

        for _ in range(1, k):
            previous_path = A[-1]
            for i in range(len(previous_path) - 1):
                spur_node = previous_path[i]
                root_path = previous_path[:i + 1]

                excluded_connections = set()
                for p in A:
                    if p[:i + 1] == root_path:

                        excluded_connections.add(self.get_connection(graph, p[i], p[i + 1]))

                excluded_zones = set(root_path[:-1])

                try:
                    spur_path = self.dijkstra(graph, spur_node, target,
                                              excluded_connections, excluded_zones)
                except UnreachableEndError:
                    continue

                total_path = root_path[:-1] + spur_path
                if total_path not in A and total_path not in B:
                    B.append(total_path)

            if not B:
                break

            B.sort(key=lambda p: self._path_cost(p))
            A.append(B.pop(0))

        return A

    def get_connection(self, graph: Graph, zone_a: Zone, zone_b: Zone) -> Connection:
        for c in graph.adjacency[zone_a.name]:
            if (c.zone_a == zone_a and c.zone_b == zone_b) or \
                 (c.zone_a == zone_b and c.zone_b == zone_a):
                return c
        raise AbsentConnectionError(f"Connection {c} doesn't exists")

    def _path_cost(self, path: list[Zone]) -> int:
        count = 0
        for zone in path:
            if isinstance(zone, RestrictedZone):
                count += 1
            count += 1
        return count

    def find_path(self, graph: Graph) -> list[Zone]:
        assert graph.end is not None
        assert graph.start is not None
        return self.dijkstra(graph, graph.start, graph.end)
