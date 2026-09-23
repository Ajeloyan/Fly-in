from .connection import Connection
from .zone import Zone


class Graph:
    """The full map: zones, their connections, and the start/end hubs."""
    def __init__(self) -> None:
        self.zones: dict[str, Zone] = {}
        self.adjacency: dict[str, list[Connection]] = {}
        self.start: Zone | None = None
        self.end: Zone | None = None

    def add_zone(self, zone: Zone) -> None:
        """Register `zone` in the graph and initialize its adjacency list."""
        self.zones[zone.name] = zone
        self.adjacency[zone.name] = []

    def add_connection(self, connection: Connection) -> None:
        """Register `connection` in the adjacency lists of both zones it links."""
        self.adjacency[connection.zone_a.name].append(connection)
        self.adjacency[connection.zone_b.name].append(connection)

    def __repr__(self) -> str:
        return f"{self.zones}, {self.start}, {self.end}"
