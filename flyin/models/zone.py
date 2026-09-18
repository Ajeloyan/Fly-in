from __future__ import annotations
from typing import TYPE_CHECKING
from .errors import ZoneFullError, AbsentDroneError

if TYPE_CHECKING:
    from .drone import Drone


class Zone:
    def __init__(self, name: str, x: int, y: int,
                 max_drones: int = 1, unlimited_capacity: bool = False) -> None:
        self.name = name
        self.x = x
        self.y = y
        self.max_drones = max_drones
        self.current_drones: list[Drone] = []
        self.unlimited_capacity: bool = unlimited_capacity

    def is_accessible(self) -> bool:
        return True

    def movement_cost(self) -> int:
        return 1

    def has_capacity(self) -> bool:
        if self.unlimited_capacity is True:
            return True
        return len(self.current_drones) < self.max_drones

    def add_drone(self, drone: Drone) -> None:
        if not self.has_capacity():
            raise ZoneFullError(f"{self} is already full")
        else:
            self.current_drones.append(drone)
            drone.current_zone = self

    def remove_drone(self, drone: Drone) -> None:
        if drone not in self.current_drones:
            raise AbsentDroneError(f"{drone} isn't currently in {self}")
        else:
            self.current_drones.remove(drone)
            drone.current_zone = None

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.name}, {self.x}, {self.y})"


class RestrictedZone(Zone):
    def movement_cost(self) -> int:
        return 2


class BlockedZone(Zone):
    def is_accessible(self) -> bool:
        return False


class PriorityZone(Zone):
    pass
