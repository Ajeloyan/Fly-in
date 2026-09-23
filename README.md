*This project has been created as part of the 42 curriculum by ajeloyan.*

# Fly-in

## Description

Fly-in is a drone routing and simulation system. Given a map describing a network of
zones connected to each other, a starting hub, an ending hub and a number of drones,
the program computes how to route every drone from the start to the end zone in the
fewest possible simulation turns, while respecting per-zone and per-connection capacity
constraints, zone-type movement costs (normal / restricted / priority / blocked), and
turn-by-turn conflict resolution.

The project is entirely custom-built and object-oriented: no external graph library is
used, the parser, the graph, the pathfinding algorithm and the turn-based simulation
engine are all implemented from scratch in Python, with a graphical visualization built
on top of `arcade`.

## Instructions

Dependencies are managed with [uv](https://docs.astral.sh/uv/).

\`\`\`bash
make install        # install dependencies
make run             # launch the menu (pick a map from the GUI)
make run MAP=path/to/map.txt   # run a specific map directly (CLI simulation + visual playback)
make debug MAP=...   # same, but stepping through pdb
make lint            # flake8 + mypy
make lint-strict      # flake8 + mypy --strict
make clean            # remove __pycache__ / .mypy_cache
\`\`\`

Map files live under `maps/<easy|medium|hard|challenger>/`. See `maps/README.md` for a
description of each provided map, and the subject (`fly-in.pdf`) for the full map file
format specification.

## Algorithm explanation

> This section describes the approach — be ready to explain the reasoning and trade-offs
> behind each choice, not just recite what it does.

**Graph** (`flyin/models/graph.py`): zones are stored in a `dict[str, Zone]`, and an
adjacency list (`dict[str, list[Connection]]`) maps each zone name to the connections
touching it. `Zone` is a small class hierarchy (`Zone`, `RestrictedZone`, `BlockedZone`,
`PriorityZone`) so that movement cost and accessibility are polymorphic
(`movement_cost()`, `is_accessible()`) rather than handled with type-checking branches
scattered through the pathfinding/simulation code.

**Pathfinding** (`flyin/pathfinding.py`):
- `dijkstra(graph, source, target, excluded_connections=None, excluded_zones=None)`
  implements Dijkstra's algorithm from scratch (no `heapq`, a linear scan over the
  unvisited set is used to pick the next node — simple and fast enough for the map
  sizes involved). It supports excluding a set of connections/zones from the search,
  which is what makes it reusable as a building block for Yen's algorithm below.
- `yen(graph, source, target, k)` implements Yen's k-shortest-paths algorithm on top of
  `dijkstra`: starting from the single shortest path, it iteratively picks a "spur node"
  along the last found path, excludes the connection that path used right after that
  spur node (plus the nodes already visited on the root path, to avoid loops), and
  reruns Dijkstra from the spur node to the target. This produces up to `k` genuinely
  distinct shortest paths, sorted by cost.
- The reason a single shortest path is not enough: with only one path, every drone is
  serialized through the same bottleneck zones/connections even when the map has
  parallel routes available (see the `simple_fork` map, which has two symmetric paths).
  Distributing drones across several paths lets independent groups of drones move in
  parallel, directly reducing the number of simulation turns needed.

**Drone-to-path distribution** (`flyin/simulation.py`, `Simulation.__init__`): drones are
assigned to the `k` paths returned by `yen()` in round-robin (drone `i` gets path
`i % k`). This is a simple, easily-justifiable heuristic; it does not account for the
relative cost/capacity of each path, so on some maps it can be very slightly
sub-optimal compared to a single-path solution — but on maps with real parallel
capacity, it consistently reduces the total number of turns.

**Simulation** (`Simulation.launch()`): the simulation proceeds turn by turn. Each turn:
- Drones already "in flight" on a connection toward a restricted zone are moved into
  that zone first, if it has capacity (accounting for zone occupants *and* other
  drones already committed to the same connection — this prevents more drones from
  entering a restricted zone than it can actually hold).
- Drones on a normal-cost zone check the destination zone's capacity *and* the
  capacity already used on the connection they'd cross **this turn** (tracked in a
  per-turn dictionary that resets every turn), so `max_link_capacity` is respected for
  every connection, not just the ones leading into restricted zones.
- Movement costs are zone-type-dependent: normal/priority zones are entered directly in
  one turn; restricted zones are entered via the connection (the drone occupies the
  connection for one full turn before landing), matching the "must arrive next turn,
  can't wait on the connection" rule from the subject.

**Complexity**: Dijkstra here is `O(V^2)` per call (linear scan instead of a heap,
`V` = number of zones) — perfectly fine for the map sizes in this project. `yen(k)`
calls Dijkstra `O(k * V)` times in the worst case. The simulation loop is bounded by
the number of turns times the number of drones.

## Visual representation

Two forms of feedback are provided:
- **Terminal output**: each simulation turn is printed as a line of
  space-separated `D<id>-<zone>` (or `D<id>-<connection>` while a drone is in transit
  toward a restricted zone), following the format required by the subject.
- **Graphical interface** (`flyin/visual/`, built with `arcade`): a menu lets you pick a
  map category and a map; the simulation then replays turn by turn with zones drawn as
  colored circles (using the `color=` metadata from the map file when present),
  connections drawn as lines, and each drone shown as a labeled dot that smoothly
  interpolates between its start and target zone each turn — this makes it easy to see
  which drone is where, and to distinguish several drones passing through the same zone
  at different times rather than mistaking it for one drone stuck in place. A speed
  toggle (x1/x2) is available, and parse/simulation errors are shown directly on the map
  selection screen instead of crashing the program.

## Example

Input (`maps/easy/03_basic_capacity.txt`):
\`\`\`
# Easy Level 3: Basic capacity management
nb_drones: 4

start_hub: start 0 0 [color=green]
hub: bottleneck 1 0 [color=orange max_drones=2]
hub: wide_area 2 0 [color=blue max_drones=3]
end_hub: goal 3 0 [color=red]

connection: start-bottleneck [max_link_capacity=4]
connection: bottleneck-wide_area [max_link_capacity=4]
connection: wide_area-goal [max_link_capacity=4]
\`\`\`

Output:
\`\`\`
D1-bottleneck D2-bottleneck
D1-wide_area D2-wide_area D3-bottleneck D4-bottleneck
D1-goal D2-goal D3-wide_area D4-wide_area
D3-goal D4-goal
\`\`\`
(4 turns — meets the `<= 6` reference target for this map.)

## Resources

- [42's Fly-in subject](fly-in.pdf) and provided map documentation (`maps/README.md`)
- [Dijkstra's algorithm](https://en.wikipedia.org/wiki/Dijkstra%27s_algorithm)
- [Yen's k-shortest path algorithm](https://en.wikipedia.org/wiki/Yen%27s_algorithm)
- [`arcade` documentation](https://api.arcade.academy/)

### AI usage

IA was used to understand optimization about algorithms. It has been used too to write this Readme.
It has been used too to learn more about arcade library.