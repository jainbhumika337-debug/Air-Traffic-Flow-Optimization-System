
import heapq
import math
import time


def dijkstra_route(graph, source, destination):
    """Find the shortest route using Dijkstra's algorithm."""

    if source not in graph or destination not in graph:
        return None, float("inf")

    distances = {node: float("inf") for node in graph.nodes}
    previous = {}

    distances[source] = 0
    queue = [(0, source)]

    while queue:
        current_cost, current = heapq.heappop(queue)

        if current_cost > distances[current]:
            continue

        if current == destination:
            break

        for neighbour, data in graph[current].items():
            weight = data.get("weight", 1)

            if weight < 0:
                raise ValueError(
                    "Dijkstra requires non-negative edge weights."
                )

            new_cost = current_cost + weight

            if new_cost < distances[neighbour]:
                distances[neighbour] = new_cost
                previous[neighbour] = current
                heapq.heappush(queue, (new_cost, neighbour))

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


def astar_route(graph, source, destination, positions):
    """Find a route using A* search with an admissible heuristic."""

    if source not in graph or destination not in graph:
        return None, float("inf")

    # Use a conservative heuristic scale based on edge weights.
    # The heuristic becomes zero if reliable coordinates are unavailable.
    min_ratio = float("inf")

    for _, _, data in graph.edges(data=True):
        distance = data.get("distance")

        if distance is None or distance <= 0:
            continue

        weight = data.get("weight", distance)

        if weight >= 0:
            min_ratio = min(min_ratio, weight / distance)

    if not math.isfinite(min_ratio):
        min_ratio = 0

    def heuristic(airport):
        if airport not in positions or destination not in positions:
            return 0

        x1, y1 = positions[airport]
        x2, y2 = positions[destination]

        straight_line = math.sqrt(
            (x2 - x1) ** 2 + (y2 - y1) ** 2
        )

        # Coordinates are assumed to use the same scale as
        # the project's existing coordinate-to-distance conversion.
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
            weight = data.get("weight", 1)

            if weight < 0:
                raise ValueError(
                    "A* requires non-negative edge weights."
                )

            new_cost = current_cost + weight

            if new_cost < distances[neighbour]:
                distances[neighbour] = new_cost
                previous[neighbour] = current

                priority = new_cost + heuristic(neighbour)

                heapq.heappush(
                    queue,
                    (priority, new_cost, neighbour)
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
    """Compare Dijkstra and A* route costs and execution times."""

    results = {}

    start = time.perf_counter()
    d_path, d_cost = dijkstra_route(
        graph, source, destination
    )
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

    if len(graph.nodes) == 0:
        return [], 0

    start = next(iter(graph.nodes))
    visited = {start}
    min_heap = []
    mst_edges = []
    total_distance = 0

    for neighbour, data in graph[start].items():
        distance = data.get(
            "distance",
            data.get("weight", 1)
        )

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
            if neighbour in visited:
                continue

            edge_distance = data.get(
                "distance",
                data.get("weight", 1)
            )

            heapq.heappush(
                min_heap,
                (edge_distance, destination, neighbour)
            )

    return mst_edges, total_distance
