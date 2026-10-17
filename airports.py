
# Airport information
AIRPORTS = {
    "Delhi": {"code": "DEL"},
    "Mumbai": {"code": "BOM"},
    "Jaipur": {"code": "JAI"},
    "Chennai": {"code": "MAA"},
    "Bengaluru": {"code": "BLR"},
    "Hyderabad": {"code": "HYD"},
    "Kolkata": {"code": "CCU"},
    "Ahmedabad": {"code": "AMD"},
}

# Available flight routes
# Each route contains distance in km and simulated capacity
ROUTES = [
    {"source": "Delhi", "destination": "Jaipur", "distance": 280, "capacity": 5},
    {"source": "Delhi", "destination": "Mumbai", "distance": 1150, "capacity": 8},
    {"source": "Delhi", "destination": "Ahmedabad", "distance": 775, "capacity": 6},
    {"source": "Delhi", "destination": "Kolkata", "distance": 1300, "capacity": 7},
    {"source": "Jaipur", "destination": "Mumbai", "distance": 920, "capacity": 4},
    {"source": "Jaipur", "destination": "Ahmedabad", "distance": 540, "capacity": 5},
    {"source": "Mumbai", "destination": "Hyderabad", "distance": 620, "capacity": 6},
    {"source": "Mumbai", "destination": "Bengaluru", "distance": 840, "capacity": 7},
    {"source": "Ahmedabad", "destination": "Hyderabad", "distance": 880, "capacity": 5},
    {"source": "Hyderabad", "destination": "Chennai", "distance": 520, "capacity": 5},
    {"source": "Hyderabad", "destination": "Bengaluru", "distance": 570, "capacity": 6},
    {"source": "Bengaluru", "destination": "Chennai", "distance": 350, "capacity": 6},
    {"source": "Kolkata", "destination": "Chennai", "distance": 1670, "capacity": 5},
    {"source": "Kolkata", "destination": "Hyderabad", "distance": 1180, "capacity": 4},
]
