
import networkx as nx

from algorithms import (
    dijkstra_route,
    astar_route,
    compare_algorithms,
    prim_mst,
)


def test_shortest_path_algorithms():
    graph = nx.Graph()

    graph.add_edge("Delhi", "Jaipur", weight=280, distance=280)
    graph.add_edge("Delhi", "Ahmedabad", weight=950, distance=950)
    graph.add_edge("Ahmedabad", "Jaipur", weight=365, distance=365)

    positions = {
        "Delhi": (0, 0),
        "Jaipur": (2, 1),
        "Ahmedabad": (3, 0),
    }

    dijkstra_path, dijkstra_cost = dijkstra_route(
        graph, "Delhi", "Jaipur"
    )

    astar_path, astar_cost = astar_route(
        graph, "Delhi", "Jaipur", positions
    )

    assert dijkstra_path == ["Delhi", "Jaipur"]
    assert dijkstra_cost == 280

    assert astar_path == dijkstra_path
    assert astar_cost == dijkstra_cost

    print("PASS: Dijkstra finds the shortest route.")
    print("PASS: A* finds the same optimal route.")


def test_unreachable_destination():
    graph = nx.Graph()
    graph.add_edge("Delhi", "Jaipur", weight=280, distance=280)
    graph.add_node("Mumbai")

    path, cost = dijkstra_route(graph, "Delhi", "Mumbai")

    assert path is None
    assert cost == float("inf")

    print("PASS: Unreachable destination is handled.")


def test_algorithm_comparison():
    graph = nx.Graph()
    graph.add_edge("Delhi", "Jaipur", weight=280, distance=280)

    positions = {
        "Delhi": (0, 0),
        "Jaipur": (1, 1),
    }

    results = compare_algorithms(
        graph, "Delhi", "Jaipur", positions
    )

    assert results["Dijkstra"]["cost"] == 280
    assert results["A*"]["cost"] == 280
    assert results["Dijkstra"]["time_ms"] >= 0
    assert results["A*"]["time_ms"] >= 0

    print("PASS: Algorithm comparison returns valid results.")


def test_prim_mst():
    graph = nx.Graph()

    graph.add_edge("A", "B", weight=2, distance=2)
    graph.add_edge("B", "C", weight=3, distance=3)
    graph.add_edge("A", "C", weight=10, distance=10)

    mst_edges, total_distance = prim_mst(graph)

    assert len(mst_edges) == 2
    assert total_distance == 5

    print("PASS: Prim's MST returns the expected tree.")


if __name__ == "__main__":
    test_shortest_path_algorithms()
    test_unreachable_destination()
    test_algorithm_comparison()
    test_prim_mst()

    print("\nAll algorithm tests passed!")
