from __future__ import annotations
from typing import TYPE_CHECKING
from .errors import ZoneFullError, AbsentDroneError

if TYPE_CHECKING:
    from .drone import Drone


class Zone:
    """A named location in the map graph, with position, color and drone capacity."""
    def __init__(self, name: str, x: int, y: int,
                 max_drones: int = 1, unlimited_capacity: bool = False,
                 color: str | None = None) -> None:
        self.name = name
        self.x = x
        self.y = y
        self.max_drones = max_drones
        self.current_drones: list[Drone] = []
        self.unlimited_capacity: bool = unlimited_capacity
        self.color = color

    def is_accessible(self) -> bool:
        """Return whether drones may ever enter this zone."""
        return True

    def movement_cost(self) -> int:
        """Return the number of turns it costs to move into this zone."""
        return 1

    def has_capacity(self) -> bool:
        """Return whether this zone can currently hold one more drone."""
        if self.unlimited_capacity is True:
            return True
        return len(self.current_drones) < self.max_drones

    def add_drone(self, drone: Drone) -> None:
        """Place `drone` in this zone, raising ZoneFullError if it has no capacity."""
        if not self.has_capacity():
            raise ZoneFullError(f"{self} is already full")
        else:
            self.current_drones.append(drone)
            drone.current_zone = self

    def remove_drone(self, drone: Drone) -> None:
        """Remove `drone` from this zone, raising AbsentDroneError if it isn't here."""
        if drone not in self.current_drones:
            raise AbsentDroneError(f"{drone} isn't currently in {self}")
        else:
            self.current_drones.remove(drone)
            drone.current_zone = None

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.name}, {self.x}, {self.y})"


class RestrictedZone(Zone):
    """A zone that costs 2 turns to enter and requires transiting its connection."""
    def movement_cost(self) -> int:
        return 2


class BlockedZone(Zone):
    """A zone that drones may never enter or pass through."""
    def is_accessible(self) -> bool:
        return False


class PriorityZone(Zone):
    """A zone that costs 1 turn to enter and should be preferred by pathfinding."""
