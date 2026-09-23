class FlyInError(Exception):
    """Base class for all domain errors raised by this project."""


class ParseError(FlyInError):
    """Raised when a map file is malformed or violates the format's constraints."""


class ZoneFullError(FlyInError):
    """Raised when a drone tries to enter a zone that has no remaining capacity."""


class ConnectionFullError(FlyInError):
    """Raised when a drone tries to enter a connection that has no remaining capacity."""


class AbsentDroneError(FlyInError):
    """Raised when trying to remove a drone from a zone/connection it isn't in."""


class AbsentConnectionError(FlyInError):
    """Raised when no connection exists between two zones that were expected to be linked."""


class UnreachableEndError(FlyInError):
    """Raised when the end hub cannot be reached from the start hub."""
