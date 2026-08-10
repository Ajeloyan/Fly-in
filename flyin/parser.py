from .models.errors import ParseError
from pathlib import Path


class MapParser:

    def parse(self, filepath: str) -> None:
        path = Path(filepath)
        with path.open("r") as f:
            for line_number, raw_line in enumerate(f, start=1):
                line = raw_line.strip()
                if not line or line.startswith("#"):
                    continue

                prefix, _, rest = line.partition(":")
                rest = rest.strip()

                if prefix == "nb_drones":
                    try:
                        nb_drones = int(rest)
                    except ValueError:
                        raise ParseError(f"line {line_number}: invalid nb_drones value '{rest}")
                    if nb_drones <= 0:
                        raise ParseError(f"line {line_number}: nb_drones must be positive,"
                                         f" got {nb_drones}")
                elif prefix in ("hub", "start_hub", "end_hub"):
                    name, x, y, metadata = self.parse_zone_line(rest, line_number)
                    print(f"parsed zone: {name} {x} {y} {metadata}")
                elif prefix == "connection":
                    zone_a, zone_b, metadata = self.parse_connection_line(rest, line_number)
                    print(f"parsed connection: zone_a = {zone_a}, zone_b = {zone_b}, metadata = {metadata}")
                else:
                    continue

    def extract_metadata(self, text: str) -> tuple[str, dict[str, str]]:
        if "[" in text:
            before, after = text.split("[", 1)
            after = after.rstrip("]")
        else:
            before = text
            after = ""

        metadata: dict[str, str] = {}
        for pair in after.split():
            key, value = pair.split("=", 1)
            metadata[key] = value
        return before, metadata

    def parse_zone_line(self, rest: str, line_number: int) -> tuple[str, int, int, dict[str, str]]:
        before, metadata = self.extract_metadata(rest)
        name, x_str, y_str = before.split()
        x = int(x_str)
        y = int(y_str)
        return name, x, y, metadata

    def parse_connection_line(self, rest: str, line_number: int) -> tuple[str, str, dict[str, str]]:
        before, metadata = self.extract_metadata(rest)
        try:
            zone_a, zone_b = before.split("-")
        except ValueError:
            raise ParseError(f"line {line_number}: connection must have 2 zones connected")
        return zone_a, zone_b, metadata
