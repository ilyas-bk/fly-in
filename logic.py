import sys
from heapq import heappush, heappop
from data import Drone, Zone, Network
import json


class SolutionLogic:
    def __init__(self, network) -> None:
        self.network = network
        self.drones = Drone.init_drones(network['nb_drones'])
        self.zones = Zone.init_zones(network)
        graph = self.prepare_graph()
        self.graph = graph['zones']
        self.src = graph['src']
        self.dest = graph['dest']
        paths = []
        for drone in self.drones:
            sol = self.dijkstra()
            if sol not in paths:
                paths.append(sol)
        for i, drone in enumerate(self.drones):
            drone.path = paths[i % len(paths)]

    def dijkstra(self):
        inf = sys.maxsize
        node_data = {key: {'cost': inf, 'pred': []} for key in self.graph.keys()}
        node_data[self.src]['cost'] = 0
        visited = set()
        min_heap = [(0, self.src)]

        while min_heap:
            current_cost, temp = heappop(min_heap)
            if temp == self.dest:
                break
            if temp in visited:
                continue

            visited.add(temp)

            for neighbor in self.graph[temp]:
                if neighbor not in visited:
                    cost = node_data[temp]['cost'] + self.graph[temp][neighbor]

                    if cost < node_data[neighbor]['cost']:
                        node_data[neighbor]['cost'] = cost
                        node_data[neighbor]['pred'] = node_data[temp]['pred'] + [temp]

                        heappush(min_heap, (cost, neighbor))
        # increase solution cost to get an alternative path
        sol = node_data[self.dest]['pred'] + [self.dest]
        for curr_node, next_node in zip(sol, sol[1:]):
            self.graph[curr_node][next_node] += 0.5
        rev_sol = sol[::-1]
        for curr_node, next_node in zip(rev_sol, rev_sol[1:]):
            self.graph[curr_node][next_node] += 0.5
        return sol

    def next_move(self) -> None:
        for drone in self.drones:
            for zone in self.zones:
                if drone.path_idx < len(drone.path) \
                    and zone.name == drone.path[drone.path_idx] \
                    and zone.curr_drones < zone.capacity:
                    for z in self.zones:
                        if z.name == drone.position:
                            z.curr_drones -= 1
                    drone.position = drone.path[drone.path_idx]
                    zone.curr_drones += 1
                    drone.path_idx += 1
                    break

            # if drone.path_idx >= len(drone.path):
            #     continue

            # if getattr(drone, 'wait', 0) > 0:
            #     drone.wait -= 1
            #     continue

            # target_name = drone.path[drone.path_idx]
            # curr_zone = next((z for z in self.zones if z.name == drone.position), None)
            # target_zone = next((z for z in self.zones if z.name == target_name), None)
            # if curr_zone is None or target_zone is None:
            #     continue
            # curr_zone.curr_drones -= 1
            # target_zone.curr_drones += 1
            # drone.position = target_zone.name
            # drone.path_idx += 1
            # if curr_zone.type == 'restricted':
            #     drone.wait = 1

    def prepare_graph(self) -> dict:
        graph_data = {}
        graph_data['zones'] = {}
        for zone in self.zones:
            graph_data['zones'][zone.name] = zone.neighbors
        graph_data['src'] = self.network['start_hub']
        graph_data['dest'] = self.network['end_hub']
        return graph_data

if __name__ == "__main__":
    network = Network.parse("01_the_impossible_dream.txt")
    solution = SolutionLogic(network)
    solutions = []
