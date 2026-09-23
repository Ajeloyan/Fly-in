from .connection import Connection
from .zone import Zone
from enum import Enum


class Status(Enum):
    """Lifecycle state of a drone during the simulation."""
    IDLE = "idle"
    TRANSIT = "in_transit"
    DELIVERED = "delivered"


class Drone:
    """A single drone: its current position (zone or connection) and status."""
    def __init__(self,
                 current_zone: Zone | None,
                 current_connection: Connection | None,
                 status: Status,
                 drone_id: int) -> None:
        self.current_zone: Zone | None = current_zone
        self.current_connection: Connection | None = current_connection
        self.status = status
        self.drone_id = drone_id

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.current_zone}, {self.current_connection}, \
            {self.status}, {self.drone_id})"
