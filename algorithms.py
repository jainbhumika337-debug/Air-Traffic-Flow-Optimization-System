
import heapq
import networkx as nx


def build_graph(airports, routes, blocked_routes=None, congestion=None):
    """Build an airport graph using distance and simulated congestion."""
    graph = nx.Graph()
    blocked_routes = blocked_routes or set()
    congestion = congestion or {}

    graph.add_nodes_from(airports.keys())

    for route in routes:
        source = route["source"]
        destination = route["destination"]
        route_key = tuple(sorted((source, destination)))

        if route_key in blocked_routes:
            continue

        distance = route["distance"]
        capacity = route["capacity"]
        traffic = congestion.get(route_key, 0)

        # Congestion adds a simulated time penalty to route cost.
        penalty = 100 * traffic / max(capacity, 1)
        cost = distance + penalty

        graph.add_edge(
            source,
            destination,
            distance=distance,
            capacity=capacity,
            traffic=traffic,
            weight=cost,
        )

    return graph


def dijkstra_route(graph, source, destination):
    """Find the minimum-cost route using Dijkstra's algorithm."""
    if source not in graph or destination not in graph:
        return None, float("inf")

    distances = {airport: float("inf") for airport in graph.nodes}
    previous = {}

    distances[source] = 0
    priority_queue = [(0, source)]

    while priority_queue:
        current_cost, current = heapq.heappop(priority_queue)

        if current_cost > distances[current]:
            continue

        if current == destination:
            break

        for neighbour, data in graph[current].items():
            new_cost = current_cost + data["weight"]

            if new_cost < distances[neighbour]:
                distances[neighbour] = new_cost
                previous[neighbour] = current
                heapq.heappush(
                    priority_queue, (new_cost, neighbour)
                )

    if distances[destination] == float("inf"):
        return None, float("inf")

    path = []
    current = destination

    while current != source:
        path.append(current)
        current = previous[current]

    path.append(source)
    path.reverse()

    return path, distances[destination]


import time
import math


def astar_route(graph, source, destination, positions):
    """Find a route using A* with straight-line coordinate heuristic."""

    def heuristic(airport):
        x1, y1 = positions[airport]
        x2, y2 = positions[destination]
        return math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)

    distances = {node: float("inf") for node in graph.nodes}
    previous = {}
    distances[source] = 0

    queue = [(heuristic(source), 0, source)]

    while queue:
        _, cost_so_far, current = heapq.heappop(queue)

        if cost_so_far != distances[current]:
            continue

        if current == destination:
            break

        for neighbour, data in graph[current].items():
            new_cost = cost_so_far + data["weight"]

            if new_cost < distances[neighbour]:
                distances[neighbour] = new_cost
                previous[neighbour] = current

                priority = new_cost + heuristic(neighbour)
                heapq.heappush(
                    queue, (priority, new_cost, neighbour)
                )

    if distances[destination] == float("inf"):
        return None, float("inf")

    path = []
    current = destination

    while current != source:
        path.append(current)
        current = previous[current]

    path.append(source)
    path.reverse()

    return path, distances[destination]


def compare_algorithms(graph, source, destination, positions):
    """Compare route results and execution time."""

    results = {}

    start = time.perf_counter()
    d_path, d_cost = dijkstra_route(graph, source, destination)
    d_time = (time.perf_counter() - start) * 1000

    start = time.perf_counter()
    a_path, a_cost = astar_route(
        graph, source, destination, positions
    )
    a_time = (time.perf_counter() - start) * 1000

    results["Dijkstra"] = {
        "path": d_path,
        "cost": d_cost,
        "time_ms": d_time,
    }

    results["A*"] = {
        "path": a_path,
        "cost": a_cost,
        "time_ms": a_time,
    }

    return results


def astar_route(graph, source, destination, positions):
    """Find the minimum-cost route using A* search."""
    import heapq

    # Distance-based heuristic scaled to remain admissible
    # for the current distance-plus-congestion cost model.
    min_ratio = 1.0

    for _, _, data in graph.edges(data=True):
        distance = data.get("distance", 0)
        weight = data.get("weight", distance)

        if distance > 0:
            min_ratio = min(min_ratio, weight / distance)

    def heuristic(airport):
        x1, y1 = positions[airport]
        x2, y2 = positions[destination]

        straight_line = (
            (x2 - x1) ** 2 + (y2 - y1) ** 2
        ) ** 0.5

        # Scale coordinates to approximately kilometres.
        return straight_line * 100 * min_ratio

    distances = {node: float("inf") for node in graph.nodes}
    previous = {}

    distances[source] = 0
    queue = [(heuristic(source), 0, source)]

    while queue:
        _, current_cost, current = heapq.heappop(queue)

        if current_cost > distances[current]:
            continue

        if current == destination:
            break

        for neighbour, data in graph[current].items():
            new_cost = current_cost + data["weight"]

            if new_cost < distances[neighbour]:
                distances[neighbour] = new_cost
                previous[neighbour] = current

                priority = new_cost + heuristic(neighbour)
                heapq.heappush(
                    queue, (priority, new_cost, neighbour)
                )

    if distances[destination] == float("inf"):
        return None, float("inf")

    path = []
    current = destination

    while current != source:
        path.append(current)
        current = previous[current]

    path.append(source)
    path.reverse()

    return path, distances[destination]


def compare_algorithms(graph, source, destination, positions):
    """Compare Dijkstra and A* execution time and route cost."""
    import time

    results = {}

    start = time.perf_counter()
    d_path, d_cost = dijkstra_route(graph, source, destination)
    d_time = (time.perf_counter() - start) * 1000

    start = time.perf_counter()
    a_path, a_cost = astar_route(
        graph, source, destination, positions
    )
    a_time = (time.perf_counter() - start) * 1000

    results["Dijkstra"] = {
        "path": d_path,
        "cost": d_cost,
        "time_ms": d_time,
    }

    results["A*"] = {
        "path": a_path,
        "cost": a_cost,
        "time_ms": a_time,
    }

    return results


def prim_mst(graph):
    """Find a Minimum Spanning Tree using Prim's algorithm."""
    import heapq

    if len(graph.nodes) == 0:
        return [], 0

    start = next(iter(graph.nodes))
    visited = {start}
    min_heap = []
    mst_edges = []
    total_distance = 0

    for neighbour, data in graph[start].items():
        distance = data.get("distance", data.get("weight", 1))
        heapq.heappush(
            min_heap,
            (distance, start, neighbour)
        )

    while min_heap and len(visited) < len(graph.nodes):
        distance, source, destination = heapq.heappop(min_heap)

        if destination in visited:
            continue

        visited.add(destination)
        mst_edges.append((source, destination, distance))
        total_distance += distance

        for neighbour, data in graph[destination].items():
            if neighbour not in visited:
                edge_distance = data.get(
                    "distance", data.get("weight", 1)
                )
                heapq.heappush(
                    min_heap,
                    (edge_distance, destination, neighbour)
                )

    return mst_edges, total_distance

