from .models.drone import Drone
from .models.zone import Zone, RestrictedZone
from .models.graph import Graph
from .models.connection import Connection
from .models.errors import AbsentConnectionError


class Simulation:
    """Runs the turn-by-turn drone simulation over one or more precomputed paths."""
    def __init__(self, drones: list[Drone], paths: list[list[Zone]], graph: Graph) -> None:
        self.drones = drones
        self.path = paths
        self.all_finished = False
        self.progress = {drone: 1 for drone in self.drones}
        self.graph = graph
        self.drone_paths: dict[Drone, list[Zone]] = {}
        for i, drone in enumerate(drones):
            self.drone_paths[drone] = paths[i % len(paths)]

    def launch(self) -> list[list[str]]:
        """Run the simulation to completion, returning the per-turn move history
        (each turn as a list of "D<id>-<zone>" / "D<id>-<connection>" strings)."""
        history: list[list[str]] = []
        while not all(self.progress[drone] >= len(self.drone_paths[drone])
                      for drone in self.drones):
            turn = []
            connections_used_this_turn: dict[Connection, int] = {}
            for drone in self.drones:
                if self.progress[drone] >= len(self.drone_paths[drone]):
                    continue
                idx = self.progress[drone]
                zone = self.drone_paths[drone][idx]
                if drone.current_connection is not None:
                    drone.current_connection.remove_drone(drone)
                    zone.add_drone(drone)
                    turn.append(f"D{drone.drone_id}-{zone.name}")
                    self.progress[drone] += 1
                    continue
                assert drone.current_zone is not None
                if zone.has_capacity():
                    if isinstance(zone, RestrictedZone):
                        connection_name = f"{drone.current_zone.name}-{zone.name}"
                        connection = self.get_connection(drone.current_zone, zone)
                        occupied_or_incoming = len(zone.current_drones) + \
                            len(connection.current_drones)
                        if occupied_or_incoming < zone.max_drones and connection.has_capacity():
                            drone.current_zone.remove_drone(drone)
                            connection.add_drone(drone)
                            turn.append(f"D{drone.drone_id}-{connection_name}")
                    elif zone.has_capacity():
                        connection = self.get_connection(drone.current_zone, zone)
                        used = connections_used_this_turn.get(connection, 0)
                        if used < connection.max_link_capacity:
                            connections_used_this_turn[connection] = used + 1
                            turn.append(f"D{drone.drone_id}-{zone.name}")
                            drone.current_zone.remove_drone(drone)
                            zone.add_drone(drone)
                            self.progress[drone] += 1
            history.append(turn)
        return history

    def get_connection(self, zone_a: Zone, zone_b: Zone) -> Connection:
        """Return the connection linking `zone_a` and `zone_b` in this simulation's graph."""
        for c in self.graph.adjacency[zone_a.name]:
            if (c.zone_a == zone_b and c.zone_b == zone_a) or \
                 (c.zone_b == zone_b and c.zone_a == zone_a):
                return c
        raise AbsentConnectionError(f"There is no connection between {zone_a} and {zone_b}")
