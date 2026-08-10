# Fly-in — Handoff de session (à coller dans une nouvelle conversation Claude)

## Contexte du projet
Projet école 42 "Fly-in" : système de routage de drones à travers un réseau de zones connectées.
Python, full OOP obligatoire, AUCUNE lib de graphe autorisée (networkx, graphlib interdits), flake8 + mypy strict exigés.
Sujet complet dans `fly-in.pdf` à la racine du projet.
Soutenance orale à la fin → je dois pouvoir justifier CHAQUE ligne de mon code.

## CONTRAINTE CRITIQUE — comment travailler avec moi
**Je ne veux PAS que tu écrives le code à ma place.** Je veux comprendre chaque ligne que j'écris.
- Guide-moi par questions (façon socratique), ne me donne pas la solution directement.
- Quand je propose du code faux ou une mauvaise approche, explique pourquoi c'est faux via des questions, pas juste "corrige comme ça".
- Avance par petits incréments testables.
- Explique le "pourquoi" derrière les choix de design.
- Si je dis "je ne vais pas juste copier ça sinon je mets des bouts que je ne comprends pas" → c'est mon état d'esprit permanent sur ce projet.

## État actuel du code (au moment du handoff)

### Modèles (`flyin/models/`)
- **`zone.py`** : `Zone` (base, `is_accessible() -> bool`, `movement_cost() -> int`, `__repr__` via `self.__class__.__name__`) + sous-classes `RestrictedZone` (movement_cost=2), `BlockedZone` (is_accessible=False), `PriorityZone` (pass). Polymorphisme fonctionnel et testé.
- **`drone.py`** : `Drone(current_zone: Zone|None, current_connection: Connection|None, status: Status, drone_id: int)`. Attribut renommé `self.id` → `self.drone_id` (évite de masquer le builtin `id()`). A un `__repr__`. `Status` est un `Enum` (IDLE, TRANSIT, DELIVERED).
- **`graph.py`** : `Graph` avec `self.zones: dict[str, Zone]`, `self.adjacency: dict[str, list[Connection]]`, `self.start: Zone|None`, `self.end: Zone|None`. `add_zone(zone)`, `add_connection(connection)` (ajoute la connexion dans l'adjacency des DEUX zones). `__repr__` défini.
- **`connection.py`** : `Connection(zone_a: Zone, zone_b: Zone, max_link_capacity: int = 1)`. Simple, pas encore de logique d'occupation.
- **`errors.py`** : `ParseError(Exception)`, juste `pass`.

### Parser (`flyin/parser.py`)
`MapParser.parse(filepath) -> tuple[Graph, list[Drone]]` — lit le fichier map ligne par ligne, gère :
- `nb_drones: N` (validation positive)
- `hub:` / `start_hub:` / `end_hub:` avec métadonnées `[zone=... max_drones=...]` → crée le bon type de `Zone` polymorphe
- `connection: a-b [max_link_capacity=...]` → résout les zones réelles via `graph.zones.get(...)`, crée `Connection`, `graph.add_connection(...)`
- Construit `list[Drone]` via `build_drones(start_zone, nb_drones)`, tous en `Status.IDLE` sur `graph.start`

**Validations déjà implémentées (session en cours) :**
1. ✅ Noms de zone dupliqués → `ParseError` (`if name in graph.zones: raise ...`)
2. ✅ `start_hub`/`end_hub` dupliqués → `ParseError` (pattern nested if/else : si `graph.start`/`graph.end` déjà assigné, raise, sinon assigne)
3. 🔲 **EN COURS, PAS ENCORE FAIT** : connexions dupliquées (`a-b` déclarée deux fois, ou une fois `a-b` et une fois `b-a` doivent être détectées comme la même connexion et rejetées). On était en train de guider la réflexion sur : utiliser `graph.adjacency[zone_a_obj.name]` (liste des `Connection` déjà existantes pour cette zone) et vérifier si l'une d'elles mène déjà vers `zone_b_obj`, dans le bloc `elif prefix == "connection":` de `parser.py`, avant `graph.add_connection(connection)`.

### `flyin/main.py`
Version debug temporaire : parse le fichier passé en argv, `print(graph)` / `print(drones)`, gère `ParseError` proprement avec `sys.exit(1)`. Ce N'EST PAS le format de sortie final requis (`D<ID>-<zone>` par tour) — ça c'est le moteur de simulation, pas encore écrit.

### Maps de test
`maps/easy/01_linear_path.txt` et `maps/hard/01_maze_nightmare.txt` (contient restricted/priority/max_link_capacity, `nb_drones: 8`). Les deux passent le parsing actuel sans erreur.

## Ce qui reste à faire (roadmap, dans l'ordre logique)
1. **Finir la validation du parser** : connexions dupliquées (en cours, voir ci-dessus)
2. Logique d'occupation dans les modèles : combien de drones sont actuellement dans une zone/connexion, méthodes pour vérifier si on peut y entrer (capacité `max_drones` / `max_link_capacity`)
3. `simulation.py` : boucle de tours, règles de mouvement/attente, gestion des connexions "restricted" (2 tours ?), respect des capacités, génération de l'output `D<ID>-<zone_ou_connection>` par tour
4. `pathfinding.py` : algo (probablement BFS/Dijkstra pondéré, PAS de lib de graphe), stratégie de scheduling multi-drones
5. Affichage visuel avec Arcade (`visual/`), découplé du moteur de simulation
6. README.md avec toutes les sections obligatoires du sujet
7. Lint : `make lint` / `make lint-strict` (flake8 + mypy strict) — pas encore fait, volontairement repoussé
8. Docstrings PEP 257 — volontairement repoussées aussi

## Notes de style / feedback à retenir
- Préfère if/elif à un dict de mapping pour la sélection de sous-classe (jugé "pas très lisible" par moi)
- `.strip()` plutôt que `.replace(" ", "")` pour nettoyer les espaces
- Toujours vérifié via `python3 -m flyin.main <map>` après chaque changement
