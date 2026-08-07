class Zone:
    def __init__(self, name: str, x: int, y: int, max_drones: int = 1) -> None:
        self.name = name
        self.x = x
        self.y = y
        self.max_drones = max_drones

    def is_accessible(self) -> bool:
        return True

    def movement_cost(self) -> int:
        return 1


class RestrictedZone(Zone):
    def movement_cost(self) -> int:
        return 2


class BlockedZone(Zone):
    def is_accessible(self) -> bool:
        return False


class PriorityZone(Zone):
    pass
