from .models.drone import Drone
from .models.zone import Zone


class Simulation:
    def __init__(self, drones: list[Drone], path: list[Zone]) -> None:
        self.drones = drones
        self.path = path
        self.all_finished = False
        self.progress = {drone: 1 for drone in self.drones}

    def launch(self):
        while not all(self.progress[drone] >= len(self.path) for drone in self.drones):
            turn = []
            for drone in self.drones:
                if self.progress[drone] >= len(self.path):
                    continue
                idx = self.progress[drone]
                zone = self.path[idx]
                if zone.has_capacity():
                    turn.append(f"D{drone.drone_id}-{zone.name}")
                    drone.current_zone.remove_drone(drone)
                    zone.add_drone(drone)
                    self.progress[drone] += 1
            print(" ".join(turn))
