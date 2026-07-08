import sys
from heapq import heapify, heappush


class SolutionLogic:
    def __init__(self) -> None:
        pass

    # make the metadata usable for the dijkstra algorithm
    def prepare_graph(self, network: dict):
        hubs: list(dict)
        hubs.append(network['start_hub'])
        hubs += network['hubs']
        hubs.append(network['end_hub'])
        connections = network['connections']
        graph: dict
        graph['hubs'] = dict()
        for hub in hubs:
            cost = graph['hubs'][hub['name']]
            for conn in connections:
                if hub['name'] == conn['start']:
                    cost = 2 if network['hubs'][conn['end']][''] == "restricted" else 1

    # the dijkstra algorithm
    def dijkstra(self, graph: dict, src: str, dest: str) -> None:
        inf = sys.maxsize
        node_data = {key: {'cost': inf, 'pred': []} for key in graph.keys()}
        node_data[src]['cost'] = 0
        visited = []
        temp = src
        min_heap = []
        for i in range(len(node_data) - 1):
            if temp not in visited:
                visited.append(temp)
                min_heap = []
                for j in graph[temp]:
                    if j not in visited:
                        cost = node_data[temp]['cost'] + graph[temp][j]
                        if cost < node_data[j]['cost']:
                            node_data[j]['cost'] = cost
                            node_data[j]['pred'] = node_data[temp]['pred'] + list(temp)
                        heappush(min_heap, (node_data[j]['cost'], j))
            heapify(min_heap)
            temp = min_heap[0][1]
        print("Shortest Distance: " + str(node_data[dest]['cost']))
        print("Shortest Path: " + str(node_data[dest]['pred'] + list(dest)))


if __name__ == "__main__":
    graph = {
        'hubs': {
            'A': {'B': 2, 'C': 4},
            'B': {'A': 2, 'C': 3, 'D': 8},
            'C': {'A': 4, 'B': 3, 'E': 5, 'D': 2},
            'D': {'B': 8, 'C': 2, 'E': 11, 'F': 22},
            'E': {'C': 5, 'D': 11, 'F': 1},
            'F': {'D': 22, 'E': 1}
        },
        'src': 'A',
        'dest': 'F'
    }
    solution = SolutionLogic()
    solution.dijkstra(graph['hubs'], graph['src'], graph['dest'])
