from __future__ import annotations

import sys
from heapq import heappop, heappush
from typing import Any, TypedDict

from src.data import Drone, Zone


class NodeData(TypedDict):
    """Shortest-path bookkeeping for a graph node."""

    cost: float
    pred: list[str]


class SolutionLogic:
    """Compute drone routes and advance the simulation state."""

    def __init__(self, network: dict[str, Any]) -> None:
        """Initialize the routing logic for a parsed network."""
        self.network = network
        self.drones = Drone.init_drones(network["nb_drones"],
                                        network["start_hub"])
        self.zones = Zone.init_zones(network)
        graph = self.prepare_graph()
        self.graph = graph["zones"]
        self.src = graph["src"]
        self.dest = graph["dest"]
        self.move_count = 0
        paths: list[list[str]] = []
        for _ in range(2 if len(self.drones) > 1 else 1):
            sol = self.dijkstra()
            if sol not in paths:
                paths.append(sol)
        for i, drone in enumerate(self.drones):
            drone.path = paths[i % len(paths)]

    def dijkstra(self) -> list[str]:
        """Compute a path from the start hub to the end hub."""
        inf = sys.maxsize
        node_data: dict[str, NodeData] = {
            key: {"cost": float(inf), "pred": []}
            for key in self.graph.keys()
        }
        node_data[self.src]["cost"] = 0.0
        visited: set[str] = set()
        min_heap: list[tuple[float, str]] = [(0, self.src)]

        while min_heap:
            current_cost, tmp = heappop(min_heap)
            if tmp == self.dest:
                break
            if tmp in visited:
                continue

            visited.add(tmp)

            for neighbor in self.graph[tmp]:
                if self.network['zones'][neighbor]['zone_type'] == 'blocked':
                    continue
                if neighbor not in visited:
                    cost = node_data[tmp]["cost"] + self.graph[tmp][neighbor]

                    if cost < node_data[neighbor]["cost"]:
                        node_data[neighbor]["cost"] = cost
                        node_data[neighbor]["pred"] = (
                            node_data[tmp]["pred"] + [tmp]
                        )

                        heappush(min_heap, (cost, neighbor))
        sol = node_data[self.dest]["pred"] + [self.dest]
        for curr_node, next_node in zip(sol, sol[1:]):
            self.graph[curr_node][next_node] += 0.5
        rev_sol = sol[::-1]
        for curr_node, next_node in zip(rev_sol, rev_sol[1:]):
            self.graph[curr_node][next_node] += 0.5
        if len(sol) < 2:
            raise ValueError(
                "No valid path found from start hub to end hub."
            )
        return sol

    def next_move(self) -> None:
        """Advance all drones by one simulation step."""
        start_zone = self.network["start_hub"]

        link_occupancy: dict = {}
        for d in self.drones:
            if d.connection_from and d.connection_to:
                key = (d.connection_from, d.connection_to)
                link_occupancy[key] = link_occupancy.get(key, 0) + 1

        for drone in self.drones:
            if drone.connection_to is not None and \
                    self.zones[drone.connection_to].type == "restricted":
                self._complete_drone_transit(drone)
                continue

            if drone.path_idx >= len(drone.path):
                continue

            if drone.path and drone.path[0] == start_zone:
                drone.path.pop(0)
                if drone.path_idx >= len(drone.path):
                    continue

            target_name = drone.path[drone.path_idx]
            curr_zone = self.zones.get(drone.position)
            target_zone = self.zones.get(target_name)

            if not curr_zone or not target_zone:
                continue

            effective_occupancy = (target_zone.curr_drones +
                                   getattr(target_zone, "reserved_drones", 0))
            if (target_zone.name != start_zone and
                    effective_occupancy >= target_zone.capacity):
                continue

            link_key = (curr_zone.name, target_zone.name)
            max_link_capacity = curr_zone.connections[target_zone.name][0]
            if link_occupancy.get(link_key, 0) >= max_link_capacity:
                continue

            if target_zone.type == "restricted":
                drone.connection_from = curr_zone.name
                drone.connection_to = target_zone.name
                link_occupancy[link_key] = link_occupancy.get(link_key, 0) + 1
                curr_zone.curr_drones -= 1
                target_zone.reserved_drones += 1
            else:
                curr_zone.curr_drones -= 1
                target_zone.curr_drones += 1
                drone.position = target_zone.name
                drone.path_idx += 1
                drone.connection_from = None
                drone.connection_to = None
                link_occupancy[link_key] = link_occupancy.get(link_key, 0) + 1

    def _complete_drone_transit(self, drone: Drone) -> None:
        """Complete movement for a drone entering a restricted zone."""
        drone.position = drone.connection_to or ""
        drone.connection_from = None
        drone.connection_to = None
        drone.path_idx += 1

        target_zone = self.zones.get(drone.position)
        if target_zone:
            current_reserved = getattr(target_zone, "reserved_drones", 1)
            target_zone.reserved_drones = max(0, current_reserved - 1)
            target_zone.curr_drones += 1

    def prepare_graph(self) -> dict[str, Any]:
        """Extract the graph structure used by the path finder."""
        graph_data: dict[str, Any] = {"zones": {}}
        for name, zone in self.zones.items():
            graph_data["zones"][name] = zone.neighbors
        graph_data["src"] = self.network["start_hub"]
        graph_data["dest"] = self.network["end_hub"]
        return graph_data
