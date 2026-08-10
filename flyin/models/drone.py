from .connection import Connection
from .zone import Zone
from enum import Enum


class Status(Enum):
    IDLE = "idle"
    TRANSIT = "in_transit"
    DELIVERED = "delivered"


class Drone:
    def __init__(self,
                 current_zone: Zone | None,
                 current_connection: Connection | None,
                 status: Status,
                 drone_id: int) -> None:
        self.current_zone: Zone | None = current_zone
        self.current_connection: Connection | None = current_connection
        self.status = status
        self.id = drone_id
