import heapq

def dijkstra(graph, source_node):
    distances_from_source = {node: float('inf') for node in graph}
    distances_from_source[source_node] = 0
    previous_nodes = {node: None for node in graph}
    visited = set()
    to_visit = [(0, source_node)]

    while to_visit:
        current_distance, current_node = heapq.heappop(to_visit)

        if current_node in visited:
            continue

        for neighbor, weight in graph[current_node].items():
            if neighbor in visited:
                continue

            distance = current_distance + weight
            if distance < distances_from_source[neighbor]:
                distances_from_source[neighbor] = distance
                previous_nodes[neighbor] = current_node
                heapq.heappush(to_visit, (distance, neighbor))

            visited.add(current_node)

    return distances_from_source, previous_nodes

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
    distances, previous_nodes = dijkstra(graph['hubs'], graph['src'])
    print("Total Distance:", distances) # shortest distance to all nodes
    print("Previous nodes:", previous_nodes) # previous node to all nodes based on the shortest path
