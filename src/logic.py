import sys
from heapq import heappush, heappop
from data import Drone, Zone, Network


class SolutionLogic:
    def __init__(self, network) -> None:
        self.network = network
        self.drones = Drone.init_drones(network['nb_drones'])
        self.zones = Zone.init_zones(network)
        graph = self.prepare_graph()
        self.graph = graph['zones']
        self.src = graph['src']
        self.dest = graph['dest']
        self.move_count = 0
        paths = []
        for drone in self.drones:
            sol = self.dijkstra()
            if sol not in paths:
                paths.append(sol)
        for i, drone in enumerate(self.drones):
            drone.path = paths[i % len(paths)]

    def dijkstra(self):
        inf = sys.maxsize
        node_data = {key: {'cost': inf, 'pred': []}
                     for key in self.graph.keys()}
        node_data[self.src]['cost'] = 0
        visited = set()
        min_heap = [(0, self.src)]

        while min_heap:
            current_cost, tmp = heappop(min_heap)
            if tmp == self.dest:
                break
            if tmp in visited:
                continue

            visited.add(tmp)

            for neighbor in self.graph[tmp]:
                if neighbor not in visited:
                    cost = node_data[tmp]['cost'] + self.graph[tmp][neighbor]

                    if cost < node_data[neighbor]['cost']:
                        node_data[neighbor]['cost'] = cost
                        node_data[neighbor]['pred'] = (node_data[tmp]['pred'] +
                                                       [tmp])

                        heappush(min_heap, (cost, neighbor))
        sol = node_data[self.dest]['pred'] + [self.dest]
        for curr_node, next_node in zip(sol, sol[1:]):
            self.graph[curr_node][next_node] += 0.5
        rev_sol = sol[::-1]
        for curr_node, next_node in zip(rev_sol, rev_sol[1:]):
            self.graph[curr_node][next_node] += 0.5
        return sol

    def next_move(self) -> None:
        for drone in self.drones:
            if drone.path_idx >= len(drone.path):
                continue
            if drone.wait > 0:
                drone.wait -= 1
                continue
            if drone.connection_to is not None:
                drone.position = drone.connection_to
                drone.connection_from = None
                drone.connection_to = None
                drone.path_idx += 1
                target_zone = self.zones.get(drone.position)
                if target_zone is not None and\
                   target_zone.type == 'restricted':
                    drone.wait = 1
                continue

            target_name = drone.path[drone.path_idx]
            curr_zone = self.zones.get(drone.position)
            target_zone = self.zones.get(target_name)
            if curr_zone is None or target_zone is None:
                continue
            if target_zone.curr_drones >= target_zone.capacity:
                continue

            if target_zone.type == 'restricted':
                curr_zone.curr_drones -= 1
                target_zone.curr_drones += 1
                drone.connection_from = curr_zone.name
                drone.connection_to = target_zone.name
                continue

            curr_zone.curr_drones -= 1
            target_zone.curr_drones += 1
            drone.position = target_zone.name
            drone.path_idx += 1

    def prepare_graph(self) -> dict:
        graph_data = {'zones': {}}
        for name, zone in self.zones.items():
            graph_data['zones'][name] = zone.neighbors
        graph_data['src'] = self.network['start_hub']
        graph_data['dest'] = self.network['end_hub']
        return graph_data


if __name__ == "__main__":
    network = Network.parse("01_the_impossible_dream.txt")
    solution = SolutionLogic(network)
    solutions = []
