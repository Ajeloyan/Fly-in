from .models.drone import Drone
from .models.zone import Zone


class Simulation:
    def __init__(self, drones: list[Drone], path: list[Zone]) -> None:
        self.drones = drones
        self.path = path
        self.all_finished = False

    def launch(self):
        for i in range(1, len(self.path)):
            for drone in self.drones:
                zone = self.path[i]
                if zone.has_capacity():
                    print(f"D{drone.drone_id}-{zone.name}")
                    drone.current_zone.remove_drone(drone)
                    zone.add_drone(drone)

