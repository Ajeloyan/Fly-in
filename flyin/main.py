from .parser import MapParser
from .models.errors import ParseError
import sys


def main():
    if len(sys.argv) < 2:
        print("Usage: python -m flyin.main <map_file>")
        sys.exit(1)

    filepath = sys.argv[1]
    try:
        MapParser().parse(filepath)
    except ParseError as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()