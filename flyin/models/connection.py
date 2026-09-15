from __future__ import annotations
from .zone import Zone
from typing import TYPE_CHECKING
from .errors import ConnectionFullError, AbsentDroneError

if TYPE_CHECKING:
    from .drone import Drone


class Connection:
    def __init__(self, zone_a: Zone, zone_b: Zone, max_link_capacity: int = 1) -> None:
        self.zone_a = zone_a
        self.zone_b = zone_b
        self.max_link_capacity = max_link_capacity
        self.current_drones: list[Drone] = []

    def add_drone(self, drone: Drone) -> None:
        if len(self.current_drones) >= self.max_link_capacity:
            raise ConnectionFullError(f"{self} is already full")
        else:
            self.current_drones.append(drone)
            drone.current_connection = self

    def remove_drone(self, drone: Drone) -> None:
        if drone not in self.current_drones:
            raise AbsentDroneError(f"{drone} isn't currently in {self}")
        else:
            self.current_drones.remove(drone)
            drone.current_connection = None

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.zone_a}, {self.zone_b})"
