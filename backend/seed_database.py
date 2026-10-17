import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from database import get_db_connection
from airports import AIRPORTS, ROUTES

# Approximate coordinates used by the existing project map
POSITIONS = {
    "Delhi": (77.1, 28.6),
    "Mumbai": (72.9, 19.1),
    "Jaipur": (75.8, 26.9),
    "Chennai": (80.3, 13.1),
    "Bengaluru": (77.6, 13.0),
    "Hyderabad": (78.5, 17.4),
    "Kolkata": (88.4, 22.6),
    "Ahmedabad": (72.6, 23.0),
}

connection = None
cursor = None

try:
    connection = get_db_connection()
    cursor = connection.cursor()

    # Insert airports without creating duplicates
    airport_ids = {}

    for name, details in AIRPORTS.items():
        code = details["code"]
        longitude, latitude = POSITIONS[name]

        cursor.execute(
            """
            INSERT INTO airports
                (airport_name, airport_code, city, latitude, longitude)
            VALUES (%s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE
                airport_code = VALUES(airport_code),
                city = VALUES(city),
                latitude = VALUES(latitude),
                longitude = VALUES(longitude)
            """,
            (name, code, name, latitude, longitude),
        )

        cursor.execute(
            "SELECT airport_id FROM airports WHERE airport_name = %s",
            (name,),
        )
        airport_ids[name] = cursor.fetchone()[0]

    # Insert routes without creating duplicate airport pairs
    for route in ROUTES:
        source_id = airport_ids[route["source"]]
        destination_id = airport_ids[route["destination"]]

        cursor.execute(
            """
            INSERT INTO routes
                (source_airport_id, destination_airport_id,
                 distance_km, capacity, is_blocked)
            VALUES (%s, %s, %s, %s, FALSE)
            ON DUPLICATE KEY UPDATE
                distance_km = VALUES(distance_km),
                capacity = VALUES(capacity)
            """,
            (
                source_id,
                destination_id,
                route["distance"],
                route["capacity"],
            ),
        )

    connection.commit()
    print(f"Success: {len(AIRPORTS)} airports processed.")
    print(f"Success: {len(ROUTES)} routes processed.")

except Exception:
    if connection is not None:
        connection.rollback()
    raise

finally:
    if cursor is not None:
        cursor.close()
    if connection is not None and connection.is_connected():
        connection.close()
