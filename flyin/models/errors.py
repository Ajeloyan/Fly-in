class FlyInError(Exception):
    pass


class ParseError(FlyInError):
    pass


class ZoneFullError(FlyInError):
    pass


class ConnectionFullError(FlyInError):
    pass


class AbsentDroneError(FlyInError):
    pass
