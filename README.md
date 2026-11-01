*This project has been created as part of the 42 curriculum by ibouelba.*

# Fly-in: Drone Network Simulation & Routing

A Python-based simulation and pathfinding engine designed to route multiple drones across a structured graph network from a source hub to a destination hub while handling zone capacities, restricted node delays, and link traffic.

---

## Description

**Fly-in** is a route planning and graphical simulation tool. The objective is to efficiently route a fleet of drones from a designated `start_hub` to an `end_hub` across a complex map network. 

### Key Features & Project Goals:
- **Custom Map Parsing:** Reads custom map text files (`map.txt`) defining drone fleet sizes, start/end hubs, intermediate zones, zone capacities, and directional edge constraints.
- **Dynamic Pathfinding:** Computes shortest and alternative non-conflicting paths for multiple drones using an adjusted Dijkstra pathfinding algorithm with dynamic edge weighting to distribute traffic.
- **Interactive Visualizer:** Uses `pygame` to render the hub network, drone locations, active link traversals, and real-time step counts visually.
- **Turn-based Step Engine:** Advances simulation frames on keypress (Spacebar), enforcing node capacity constraints, speed penalties on restricted zones, and link congestion limits.

---

## Instructions

### Prerequisites
- Python 3.10+
- `pip` package manager
- System support for Pygame (display server required for visual execution)

### Installation & Execution

The project includes a `Makefile` to streamline set up, linting, and running:

1. **Install Dependencies:**
   ```bash
   make install

```

2. **Run the Simulation:**
```bash
make run

```


*(Note: By default, `main.py` parses `map.txt` located in the root directory).*
3. **Debug Mode:**
To run under Python's Interactive Debugger (`pdb`):
```bash
make debug

```


4. **Linting & Type Checking:**
* Standard checking (Flake8 & Mypy):
```bash
make lint

```


* Strict Mypy type checking:
```bash
make lint-strict

```




5. **Clean Temporary Cache:**
```bash
make clean

```



---

## Controls & Usage

* **`SPACE` Key:** Advances the simulation state by 1 step / move.
* **Window Resize:** Dynamically rescales the graph topology to fit the display area.
* **`Ctrl+C` in Terminal:** Gracefully terminates the application.

---

## Technical Choices & Algorithm Implementation

### 1. Network Parsing & Domain Architecture (`src/parser.py`, `src/data.py`)

* **Regex Parsing:** A custom line-by-line regex parser validates the structural framework of `map.txt`, verifying syntax for drone counts, hub declarations (with spatial `x, y` coordinates), zone attributes (`normal`, `restricted`, `priority`), link capacities, and custom metadata parameters.
* **Data Encapsulation:** `Network`, `Zone`, and `Drone` objects cleanly partition state management from execution logic.

### 2. Pathfinding Strategy (`src/logic.py`)

* **Dijkstra's Algorithm with Dynamic Penalties:**
* Base edge costs are adjusted according to target zone types (e.g., `restricted` zones add higher traverse costs, while `priority` zones reduce movement cost).
* To prevent all drones from stacking onto a single optimal route, each time Dijkstra computes a path for a drone, the traversal costs along that path are incrementally penalized (`+0.5`). Subsequent drones calculate paths over this updated cost matrix, naturally balancing traffic across alternate routes.



### 3. Step & Simulation Engine

* **Capacity & Zone Handling:** Drones track their step progress. Moving into a `restricted` zone imposes a `wait = 1` turn penalty before proceeding.
* **Occupancy Tracking:** Ensures zone drone capacity limits (`max_drones`) are never breached during intermediate movement steps.

---

## Visualization Features

The visualization component is built using **Pygame** (`src/simulation.py`):

* **Auto-Scaling Viewport:** Translates raw integer coordinates into normalized display space while preserving relative distances and centering content inside user-resizable windows.
* **Color-Coded Hubs & Nodes:** Renders zones using map-defined color properties (or fallback themes) along with clear textual identifiers.
* **Dynamic Drone Markers:** Represents drones as diamond shapes placed on top of current hub locations or interpolated onto connection vectors when traversing between hubs.
* **Move Counter HUD:** Real-time top-left display displaying the total step count elapsed to reach the goal state.

---

## Map Input & Output Example

### Input File Structure (`map.txt`)

```text
nb_drones: 3

start_hub: start 0 0 [zone=normal color=green]
hub: A 10 5 [zone=priority color=blue]
hub: B 10 -5 [zone=restricted color=orange]
end_hub: end 20 0 [zone=normal color=red]

connection: start-A [max_link_capacity=2]
connection: start-B [max_link_capacity=2]
connection: A-end [max_link_capacity=2]
connection: B-end [max_link_capacity=2]

```

### Expected Output & Behavior

1. **Initialization:**
* 3 drones are initialized at `Start`.
* Paths are generated: Drone 1 takes `Start -> A -> End`, Drone 2 takes `Start -> B -> End` (due to dynamic path penalization), Drone 3 routes via available bandwidth.


2. **Execution State on Display:**
* **Step 0:** Move Count = 0. All drones at `Start`.
* **Step 1:** Drones transition out along connections to `A` and `B`.
* **Step 2+:** Drone entering restricted zone `B` pauses for 1 extra tick before moving to `End`.
* **Completion:** Visual move counter halts incrementing as all drones reach `End`.



---

## Resources

### Classical References

* **Dijkstra's Algorithm:** [Dijkstra's Shortest Path Algorithm - GeeksforGeeks](https://www.geeksforgeeks.org/dijkstras-shortest-path-algorithm-greedy-algo-7/)
* **Pygame Documentation:** [Pygame API Reference](https://www.pygame.org/docs/)
* **Graph Theory & Pathfinding:** *Introduction to Algorithms* (Cormen, Leiserson, Rivest, Stein).

### AI Usage Transparency

* **Tasks & Scope:** AI tools were utilized to draft documentation, assist in optimizing graph cost adjustment logic, and refine clean-code linting configurations (`mypy` / `flake8` compliance).
* **Validation:** All generated algorithms, parser regex rules, and simulation step mechanics were manually verified, tested, and vetted against edge-case network topologies.