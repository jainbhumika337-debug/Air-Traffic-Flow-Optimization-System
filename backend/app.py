import requests
from flask import request
from flask import Flask, jsonify
from flask_cors import CORS
from database import get_db_connection

app = Flask(__name__)
CORS(app)


@app.route("/", methods=["GET"])
def home():
    return jsonify({
        "message": "Air Traffic Optimization API is running",
        "status": "success"
    })


@app.route("/api/health", methods=["GET"])
def health():
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        cursor.execute("SELECT 1")
        cursor.fetchone()
        cursor.close()
        connection.close()

        return jsonify({
            "status": "healthy",
            "database": "connected"
        })

    except Exception as error:
        app.logger.exception("Database health check failed")
        return jsonify({
            "status": "error",
            "message": "Database connection failed"
        }), 500


@app.route("/api/airports", methods=["GET"])
def get_airports():
    connection = None
    cursor = None

    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)

        cursor.execute("""
            SELECT airport_id, airport_name, airport_code,
                   city, latitude, longitude
            FROM airports
            ORDER BY airport_name
        """)

        airports = cursor.fetchall()

        # Convert database decimal values into JSON-friendly numbers.
        for airport in airports:
            for field in ("latitude", "longitude"):
                if airport[field] is not None:
                    airport[field] = float(airport[field])

        return jsonify({
            "status": "success",
            "count": len(airports),
            "airports": airports
        })

    except Exception:
        app.logger.exception("Failed to fetch airports")
        return jsonify({
            "status": "error",
            "message": "Could not fetch airports"
        }), 500

    finally:
        if cursor is not None:
            cursor.close()
        if connection is not None and connection.is_connected():
            connection.close()

@app.route("/api/routes", methods=["GET"])
def get_routes():
    connection = None
    cursor = None

    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)

        cursor.execute("""
            SELECT
                r.route_id,
                a1.airport_name AS source,
                a2.airport_name AS destination,
                r.distance_km,
                r.capacity,
                r.is_blocked
            FROM routes r
            JOIN airports a1
                ON r.source_airport_id = a1.airport_id
            JOIN airports a2
                ON r.destination_airport_id = a2.airport_id
            ORDER BY r.route_id
        """)

        routes = cursor.fetchall()

        for route in routes:
            route["distance_km"] = float(route["distance_km"])
            route["is_blocked"] = bool(route["is_blocked"])

        return jsonify({
            "status": "success",
            "count": len(routes),
            "routes": routes
        })

    except Exception:
        app.logger.exception("Failed to fetch routes")
        return jsonify({
            "status": "error",
            "message": "Could not fetch routes"
        }), 500

    finally:
        if cursor is not None:
            cursor.close()
        if connection is not None and connection.is_connected():
            connection.close()


@app.route("/api/optimize", methods=["POST"])
def optimize_route():
    connection = None
    cursor = None

    try:
        data = request.get_json(silent=True) or {}

        source = data.get("source")
        destination = data.get("destination")

        if not source or not destination:
            return jsonify({
                "status": "error",
                "message": "Source and destination are required"
            }), 400

        if source == destination:
            return jsonify({
                "status": "success",
                "route": [source],
                "total_distance_km": 0,
                "message": "Source and destination are the same"
            })

        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)

        cursor.execute("""
            SELECT airport_id, airport_name
            FROM airports
        """)
        airports = cursor.fetchall()

        airport_ids = {
            airport["airport_name"]: airport["airport_id"]
            for airport in airports
        }

        if source not in airport_ids or destination not in airport_ids:
            return jsonify({
                "status": "error",
                "message": "Invalid source or destination airport"
            }), 400

        cursor.execute("""
            SELECT
                a1.airport_name AS source,
                a2.airport_name AS destination,
                r.distance_km,
                r.is_blocked
            FROM routes r
            JOIN airports a1
                ON r.source_airport_id = a1.airport_id
            JOIN airports a2
                ON r.destination_airport_id = a2.airport_id
        """)

        routes = cursor.fetchall()

        import networkx as nx

        graph = nx.Graph()

        for airport in airports:
            graph.add_node(airport["airport_name"])

        for route in routes:
            if not route["is_blocked"]:
                graph.add_edge(
                    route["source"],
                    route["destination"],
                    weight=float(route["distance_km"])
                )

        if not nx.has_path(graph, source, destination):
            return jsonify({
                "status": "error",
                "message": "No available route between these airports"
            }), 404

        shortest_route = nx.shortest_path(
            graph,
            source=source,
            target=destination,
            weight="weight"
        )

        total_distance = nx.shortest_path_length(
            graph,
            source=source,
            target=destination,
            weight="weight"
        )

        return jsonify({
            "status": "success",
            "algorithm": "Dijkstra",
            "route": shortest_route,
            "total_distance_km": round(total_distance, 2)
        })

    except Exception:
        app.logger.exception("Route optimization failed")
        return jsonify({
            "status": "error",
            "message": "Route optimization failed"
        }), 500

    finally:
        if cursor is not None:
            cursor.close()

        if connection is not None and connection.is_connected():
            connection.close()

            
@app.route("/api/routes/<int:route_id>/block", methods=["PATCH"])
def update_route_status(route_id):
    connection = None
    cursor = None

    try:
        data = request.get_json(silent=True) or {}
        is_blocked = data.get("is_blocked")

        if not isinstance(is_blocked, bool):
            return jsonify({
                "status": "error",
                "message": "is_blocked must be true or false"
            }), 400

        connection = get_db_connection()
        cursor = connection.cursor()

        cursor.execute(
            """
            UPDATE routes
            SET is_blocked = %s
            WHERE route_id = %s
            """,
            (is_blocked, route_id)
        )

        if cursor.rowcount == 0:
            connection.rollback()
            return jsonify({
                "status": "error",
                "message": "Route not found or status unchanged"
            }), 404

        connection.commit()

        return jsonify({
            "status": "success",
            "route_id": route_id,
            "is_blocked": is_blocked
        })

    except Exception:
        if connection is not None:
            connection.rollback()

        app.logger.exception("Failed to update route status")
        return jsonify({
            "status": "error",
            "message": "Could not update route status"
        }), 500

    finally:
        if cursor is not None:
            cursor.close()

        if connection is not None and connection.is_connected():
            connection.close()



if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)
