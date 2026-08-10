from .models.zone import Zone, RestrictedZone, BlockedZone, PriorityZone
from .models.errors import ParseError
from .models.graph import Graph
from .models.connection import Connection
from .models.drone import Drone, Status
from pathlib import Path


class MapParser:

    def parse(self, filepath: str) -> tuple[Graph, list[Drone]]:
        graph = Graph()
        path = Path(filepath)
        nb_drones: int | None = None
        with path.open("r") as f:
            for line_number, raw_line in enumerate(f, start=1):
                line = raw_line.strip()
                if not line or line.startswith("#"):
                    continue

                prefix, _, rest = line.partition(":")
                rest = rest.strip()

                if prefix == "nb_drones":
                    try:
                        nb_drones = int(rest)
                    except ValueError:
                        raise ParseError(f"line {line_number}: invalid nb_drones value '{rest}'")
                    if nb_drones <= 0:
                        raise ParseError(f"line {line_number}: nb_drones must be positive,"
                                         f" got {nb_drones}")
                elif prefix in ("hub", "start_hub", "end_hub"):
                    name, x, y, metadata = self.parse_zone_line(rest, line_number)
                    if name in graph.zones:
                        raise ParseError(f"line {line_number}: duplicate zone name '{name}'")
                    max_drones_str = metadata.get("max_drones", "1")
                    try:
                        max_drones = int(max_drones_str)
                    except ValueError:
                        raise ParseError(f"line {line_number}: invalid max_drones value '{max_drones_str}'")
                    zone_type = metadata.get("zone", "normal")
                    if zone_type == "normal":
                        zone = Zone(name, x, y, max_drones)
                    elif zone_type == "restricted":
                        zone = RestrictedZone(name, x, y, max_drones)
                    elif zone_type == "blocked":
                        zone = BlockedZone(name, x, y, max_drones)
                    elif zone_type == "priority":
                        zone = PriorityZone(name, x, y, max_drones)
                    else:
                        raise ParseError(f"line {line_number}: unknown zone type '{zone_type}'")
                        
                    graph.add_zone(zone)

                    if prefix == "start_hub":
                        if graph.start is None:
                            graph.start = zone
                        else:
                            raise ParseError(f"line {line_number}: duplicate start hub value '{graph.start.name}'")
                    elif prefix == "end_hub":
                        if graph.end is None:
                            graph.end = zone
                        else:
                            raise ParseError(f"line {line_number}: duplicate end hub value '{graph.end.name}'")

                elif prefix == "connection":
                    zone_a, zone_b, metadata = self.parse_connection_line(rest, line_number)

                    zone_a_obj = graph.zones.get(zone_a)
                    if zone_a_obj is None:
                        raise ParseError(f"line {line_number}: connection references unknown zone '{zone_a}'")

                    zone_b_obj = graph.zones.get(zone_b)
                    if zone_b_obj is None:
                        raise ParseError(f"line {line_number}: connection references unknown zone '{zone_b}'")

                    max_link_capacity_str = metadata.get("max_link_capacity", "1")
                    try:
                        max_link_capacity = int(max_link_capacity_str)
                    except ValueError:
                        raise ParseError(f"line {line_number}: invalid max_link_capacity '{max_link_capacity_str}'")

                    connection = Connection(zone_a_obj, zone_b_obj, max_link_capacity)
                    graph.add_connection(connection)
                else:
                    continue
            if graph.start is None:
                raise ParseError("map file has no start hub")
            if graph.end is None:
                raise ParseError("map file has no end hub")
            if nb_drones is None:
                raise ParseError("nb_drones is missing")
        list_drones: list[Drone] = self.build_drones(graph.start, nb_drones)
        return graph, list_drones

    def extract_metadata(self, text: str) -> tuple[str, dict[str, str]]:
        if "[" in text:
            before, after = text.split("[", 1)
            after = after.rstrip("]")
        else:
            before = text
            after = ""

        metadata: dict[str, str] = {}
        for pair in after.split():
            key, value = pair.split("=", 1)
            metadata[key] = value
        return before, metadata

    def parse_zone_line(self, rest: str, line_number: int) -> tuple[str, int, int, dict[str, str]]:
        before, metadata = self.extract_metadata(rest)
        name, x_str, y_str = before.split()
        x = int(x_str)
        y = int(y_str)
        return name, x, y, metadata

    def parse_connection_line(self, rest: str, line_number: int) -> tuple[str, str, dict[str, str]]:
        before, metadata = self.extract_metadata(rest)
        try:
            zone_a, zone_b = before.split("-")
            zone_a = zone_a.strip()
            zone_b = zone_b.strip()
        except ValueError:
            raise ParseError(f"line {line_number}: connection must have 2 zones connected")
        return zone_a, zone_b, metadata

    def build_drones(self, start_zone: Zone, nb_drones: int) -> list[Drone]:
        list_drones: list[Drone] = []
        for i in range(nb_drones):
            drone = Drone(start_zone, None, Status.IDLE, i + 1)
            list_drones.append(drone)
        return list_drones
        