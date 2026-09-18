from .models.drone import Drone
from .models.zone import Zone, RestrictedZone
from .models.graph import Graph
from .models.connection import Connection
from .models.errors import AbsentConnectionError


class Simulation:
    def __init__(self, drones: list[Drone], path: list[Zone], graph: Graph) -> None:
        self.drones = drones
        self.path = path
        self.all_finished = False
        self.progress = {drone: 1 for drone in self.drones}
        self.graph = graph

    def launch(self) -> None:
        while not all(self.progress[drone] >= len(self.path) for drone in self.drones):
            turn = []
            for drone in self.drones:
                if self.progress[drone] >= len(self.path):
                    continue
                idx = self.progress[drone]
                zone = self.path[idx]
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
                        if connection.has_capacity():
                            drone.current_zone.remove_drone(drone)
                            connection.add_drone(drone)
                            turn.append(f"D{drone.drone_id}-{connection_name}")
                    else:
                        turn.append(f"D{drone.drone_id}-{zone.name}")
                        drone.current_zone.remove_drone(drone)
                        zone.add_drone(drone)
                        self.progress[drone] += 1
            print(" ".join(turn))

    def get_connection(self, zone_a: Zone, zone_b: Zone) -> Connection:
        for c in self.graph.adjacency[zone_a.name]:
            if (c.zone_a == zone_b and c.zone_b == zone_a) or \
                 (c.zone_b == zone_b and c.zone_a == zone_a):
                return c
        raise AbsentConnectionError(f"There is no connection between {zone_a} and {zone_b}")
