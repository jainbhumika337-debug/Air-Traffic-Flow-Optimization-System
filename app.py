import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import requests

API_URL = "http://127.0.0.1:5000"


def fetch_backend_routes():
    """Fetch the latest route status from the Flask/MySQL backend."""
    try:
        response = requests.get(f"{API_URL}/api/routes", timeout=10)
        response.raise_for_status()
        payload = response.json()
        return payload.get("routes", [])
    except (requests.exceptions.RequestException, ValueError):
        return None


def optimize_route_api(source, destination):
    try:
        response = requests.post(
            f"{API_URL}/api/optimize",
            json={
                "source": source,
                "destination": destination
            },
            timeout=10
        )

        try:
            result = response.json()
        except ValueError:
            return {
                "status": "error",
                "message": "Backend returned an invalid response."
            }

        if response.status_code == 200:
            return result

        return {
            "status": "error",
            "message": result.get(
                "message",
                "Route optimization failed"
            )
        }

    except requests.exceptions.RequestException:
        return {
            "status": "error",
            "message": "Backend is not running. Please start Flask first."
        }

    
def update_route_api(route_id, is_blocked):
    try:
        response = requests.patch(
            f"{API_URL}/api/routes/{route_id}/block",
            json={"is_blocked": is_blocked},
            timeout=10
        )

        result = response.json()

        if response.ok:
            return result

        return {
            "status": "error",
            "message": result.get(
                "message",
                "Could not update route"
            )
        }

    except (requests.exceptions.RequestException, ValueError):
        return {
            "status": "error",
            "message": "Could not connect to the Flask backend"
        }


from airports import AIRPORTS, ROUTES
from algorithms import (
    build_graph,
    dijkstra_route,
    compare_algorithms,
    prim_mst,
)

# --------------------------------------------------
# PAGE CONFIGURATION
# --------------------------------------------------

st.set_page_config(
    page_title="Air Traffic Flow Optimization",
    page_icon="✈️",
    layout="wide",
)

# --------------------------------------------------
# PROFESSIONAL BLUE-WHITE DASHBOARD THEME
# --------------------------------------------------

st.markdown("""
<style>
    :root {
        color-scheme: light !important;
    }

    html, body, [data-testid="stAppViewContainer"], .stApp,
    [data-testid="stMain"], [data-testid="stMainBlockContainer"] {
        background: #f3f7fd !important;
        color: #243b53 !important;
    }

    [data-testid="stAppViewContainer"] {
        background: linear-gradient(135deg, #f7faff 0%, #eaf2fc 100%) !important;
    }

    [data-testid="stHeader"] {
        background: rgba(247, 250, 255, 0.96) !important;
    }

    [data-testid="stToolbar"], [data-testid="stDecoration"],
    #MainMenu, footer {
        visibility: hidden !important;
        height: 0 !important;
    }

    [data-testid="stMainBlockContainer"] {
        padding-top: 1.8rem !important;
    }

    h1, h2, h3, h4 {
        color: #12345a !important;
        font-weight: 750 !important;
    }

    p, label, [data-testid="stMarkdownContainer"] {
        color: #243b53;
    }

    [data-testid="stCaptionContainer"] {
        color: #607995 !important;
    }

    [data-testid="stSidebar"], [data-testid="stSidebar"] > div {
        background: #e7f0fc !important;
        border-right: 1px solid #d3e2f4;
    }

    [data-testid="stSidebar"] h1,
    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3,
    [data-testid="stSidebar"] p,
    [data-testid="stSidebar"] label {
        color: #173e67 !important;
    }

    [data-testid="stMetric"] {
        background: #ffffff;
        border: 1px solid #d9e6f5;
        border-radius: 14px;
        padding: 18px 20px;
        box-shadow: 0 4px 14px rgba(30, 75, 125, 0.07);
    }

    [data-testid="stMetricLabel"] {
        color: #526b86 !important;
        font-weight: 600;
    }

    [data-testid="stMetricValue"] {
        color: #1264b4 !important;
        font-weight: 800;
    }

    div.stButton > button {
        background: linear-gradient(90deg, #1264b4, #2387e8);
        color: #ffffff !important;
        border: 1px solid #1264b4;
        border-radius: 9px;
        font-weight: 650;
        transition: all 0.2s ease;
    }

    div.stButton > button p {
        color: #ffffff !important;
        font-weight: 650;
    }

    div.stButton > button:hover {
        background: linear-gradient(90deg, #0b4e91, #1264b4);
        border-color: #0b4e91;
        color: #ffffff !important;
        box-shadow: 0 4px 12px rgba(18, 100, 180, 0.2);
    }

    [data-baseweb="select"] > div {
        background: #ffffff !important;
        border-color: #cbdced !important;
        color: #243b53 !important;
        border-radius: 8px;
    }

    [data-baseweb="input"] > div, [data-baseweb="textarea"] > div {
        background: #ffffff !important;
        border-color: #cbdced !important;
    }

    [data-testid="stAlert"] {
        border-radius: 12px !important;
    }

    [data-testid="stPlotlyChart"] {
        background: #ffffff !important;
        border: 1px solid #d9e6f5;
        border-radius: 12px;
        padding: 6px;
    }

    [data-testid="stDataFrame"] {
        border: 1px solid #d9e6f5;
        border-radius: 11px;
        overflow: hidden;
        background: #ffffff;
    }

    hr {
        border-color: #d5e3f3;
    }
</style>
""", unsafe_allow_html=True)

st.title("✈️ Air Traffic Flow Optimization System")

# Approximate coordinates: longitude, latitude
positions = {
    "Delhi": (77.1, 28.6),
    "Mumbai": (72.9, 19.1),
    "Jaipur": (75.8, 26.9),
    "Chennai": (80.3, 13.1),
    "Bengaluru": (77.6, 13.0),
    "Hyderabad": (78.5, 17.4),
    "Kolkata": (88.4, 22.6),
    "Ahmedabad": (72.6, 23.0),
}

# --------------------------------------------------
# SESSION STATE
# --------------------------------------------------

if "congestion" not in st.session_state:
    st.session_state.congestion = {}

if "blocked_routes" not in st.session_state:
    st.session_state.blocked_routes = set()


# Load current database route statuses before building the graph.
backend_routes_data = fetch_backend_routes()
database_blocked_routes = set()

if backend_routes_data is not None:
    for db_route in backend_routes_data:
        if db_route.get("is_blocked", False):
            database_blocked_routes.add(
                tuple(sorted((db_route["source"], db_route["destination"])))
            )

effective_blocked_routes = (
    set(st.session_state.blocked_routes) | database_blocked_routes
)

# --------------------------------------------------
# SIDEBAR: FLIGHT ROUTE PLANNER
# --------------------------------------------------

st.sidebar.header("✈️ Flight Route Planner")

airport_names = list(AIRPORTS.keys())

source = st.sidebar.selectbox(
    "Source Airport",
    airport_names,
    index=0,
    key="source_airport",
)

destination_options = [
    airport for airport in airport_names if airport != source
]

preferred_destination = (
    "Chennai" if "Chennai" in destination_options
    else destination_options[0]
)

destination = st.sidebar.selectbox(
    "Destination Airport",
    destination_options,
    index=destination_options.index(preferred_destination),
    key="destination_airport",
)

st.sidebar.subheader("Traffic Simulation")

if st.sidebar.button("Simulate Congestion", width="stretch"):
    for route in ROUTES:
        key = tuple(sorted((route["source"], route["destination"])))
        st.session_state.congestion[key] = route["capacity"]
    st.rerun()

if st.sidebar.button("Reset Traffic", width="stretch"):
    st.session_state.congestion = {}
    st.rerun()

# --------------------------------------------------
# BUILD GRAPH AND FIND ROUTE
# --------------------------------------------------

graph = build_graph(
    AIRPORTS,
    ROUTES,
    blocked_routes=effective_blocked_routes,
    congestion=st.session_state.congestion,
)

path, route_cost = dijkstra_route(graph, source, destination)

congested_count = sum(
    1
    for route in ROUTES
    if tuple(sorted((route["source"], route["destination"])))
    not in effective_blocked_routes
    and st.session_state.congestion.get(
        tuple(sorted((route["source"], route["destination"]))), 0
    ) >= route["capacity"]
)

# --------------------------------------------------
# SUMMARY METRICS
# --------------------------------------------------

col1, col2, col3 = st.columns(3)

col1.metric("Total Airports", len(AIRPORTS))
col2.metric("Available Routes", graph.number_of_edges())
col3.metric("Congested Routes", congested_count)

st.divider()

# --------------------------------------------------
# AIRPORT NETWORK MAP
# --------------------------------------------------

left, right = st.columns([2, 1])

with left:
    st.subheader("🌐 Airport Network")

    # Calculate MST for visualization
    mst_edges, mst_distance = prim_mst(graph)
    mst_available = (
        len(AIRPORTS) <= 1
        or len(mst_edges) == len(AIRPORTS) - 1
    )

    show_mst = st.checkbox(
        "Show Prim's Minimum Spanning Tree on Map",
        value=False,
    )

    fig = go.Figure()

    # Draw available routes
    for route in ROUTES:
        a = route["source"]
        b = route["destination"]
        key = tuple(sorted((a, b)))

        x1, y1 = positions[a]
        x2, y2 = positions[b]

        traffic = st.session_state.congestion.get(key, 0)
        is_blocked = key in effective_blocked_routes
        is_congested = traffic >= route["capacity"] and not is_blocked

        if is_blocked:
            route_color = "#dc2626"
            route_width = 2.5
            route_dash = "dash"
            route_status = "BLOCKED"
        elif is_congested:
            route_color = "#f97316"
            route_width = 3
            route_dash = "solid"
            route_status = "CONGESTED"
        else:
            route_color = "#9bb2cc"
            route_width = 1.3
            route_dash = "solid"
            route_status = "AVAILABLE"

        fig.add_trace(go.Scatter(
            x=[x1, x2],
            y=[y1, y2],
            mode="lines",
            line=dict(color=route_color, width=route_width, dash=route_dash),
            hovertemplate=(
                f"{a} ↔ {b}<br>"
                f"Distance: {route['distance']} km<br>"
                f"Capacity: {route['capacity']}<br>"
                f"Status: {route_status}<extra></extra>"
            ),
            showlegend=False,
        ))

    # Highlight Prim's MST in orange
    if show_mst:
        if mst_available:
            for a, b, distance in mst_edges:
                x1, y1 = positions[a]
                x2, y2 = positions[b]

                fig.add_trace(go.Scatter(
                    x=[x1, x2],
                    y=[y1, y2],
                    mode="lines",
                    line=dict(color="#8b5cf6", width=5),
                    hovertemplate=(
                        f"MST: {a} ↔ {b}<br>"
                        f"Distance: {distance} km<extra></extra>"
                    ),
                    showlegend=False,
                ))
        else:
            st.warning(
                "The network is disconnected. Reopen blocked routes "
                "to connect all airports before displaying the MST."
            )

    # Highlight Dijkstra's recommended route in green
    if path:
        for a, b in zip(path, path[1:]):
            x1, y1 = positions[a]
            x2, y2 = positions[b]

            fig.add_trace(go.Scatter(
                x=[x1, x2],
                y=[y1, y2],
                mode="lines",
                line=dict(color="#00cc96", width=5),
                hoverinfo="skip",
                showlegend=False,
            ))

    # Draw airport markers
    fig.add_trace(go.Scatter(
        x=[positions[a][0] for a in airport_names],
        y=[positions[a][1] for a in airport_names],
        mode="markers+text",
        text=airport_names,
        textposition="top center",
        marker=dict(size=12, color="#4c78a8"),
        hovertemplate="%{text}<extra>Airport</extra>",
        showlegend=False,
    ))

    fig.update_layout(
        height=520,
        margin=dict(l=10, r=10, t=20, b=10),
        xaxis_title="Longitude (schematic)",
        yaxis_title="Latitude (schematic)",
        template="plotly_white",
        paper_bgcolor="#ffffff",
        plot_bgcolor="#f7faff",
        font=dict(color="#173e67", size=12),
        xaxis=dict(gridcolor="#dce6f2", zerolinecolor="#dce6f2"),
        yaxis=dict(gridcolor="#dce6f2", zerolinecolor="#dce6f2"),
        legend=dict(bgcolor="rgba(255,255,255,0.85)"),
    )

    st.plotly_chart(fig, width="stretch")
    st.caption("Map legend: green = recommended route · orange = congested · red dashed = blocked · purple = Prim's MST.")

    if show_mst and mst_available:
        st.success("MST connections are highlighted in purple.")
        st.metric("Total MST Distance", f"{mst_distance:,} km")

with right:
    st.subheader("🧭 Route Recommendation")

    if path:
        st.success("Available route found!")
        st.markdown(" → ".join(path))

        total_distance = sum(
            graph[a][b]["distance"]
            for a, b in zip(path, path[1:])
        )

        st.metric("Route Distance", f"{total_distance:,} km")
        st.metric("Weighted Route Cost", f"{route_cost:,.1f}")

        st.caption(
            "Weighted cost includes a simulated congestion penalty. "
            "It does not represent actual flight time."
        )
    else:
        st.error(
            "No available route. Try another destination "
            "or reopen a blocked route."
        )

# --------------------------------------------------
# FLASK + MYSQL BACKEND ROUTE OPTIMIZATION
# --------------------------------------------------

st.divider()
st.subheader("🗄️ Backend Route Optimization (Flask + MySQL)")
st.write(
    "Calculate the shortest route using the airports and routes stored "
    "in the MySQL database. This result is separate from the local "
    "traffic simulation above."
)

if st.button("Optimize Using Backend Database", type="primary"):
    with st.spinner("Requesting route from Flask backend..."):
        backend_result = optimize_route_api(source, destination)

    if backend_result.get("status") == "success":
        backend_path = backend_result.get("route", [])
        backend_distance = backend_result.get("total_distance_km")

        st.success("Backend route optimization successful!")
        st.markdown("**Database Route:** " + " → ".join(backend_path))

        backend_col1, backend_col2 = st.columns(2)
        backend_col1.metric(
            "Database Route Distance",
            f"{backend_distance:,.1f} km"
            if isinstance(backend_distance, (int, float))
            else "Not provided"
        )
        backend_col2.metric(
            "Backend Algorithm",
            backend_result.get("algorithm", "Dijkstra")
        )
    else:
        st.error(
            backend_result.get(
                "message",
                "Backend route optimization failed."
            )
        )

# --------------------------------------------------
# DIJKSTRA VS A* COMPARISON
# --------------------------------------------------

st.divider()
st.subheader("📊 DAA Algorithm Performance Comparison")

st.write(
    "Compare Dijkstra and A* using the same airport network "
    "and route-cost model."
)

if st.button("Compare Dijkstra vs A*", type="primary"):
    comparison = compare_algorithms(graph, source, destination, positions)
    comparison_rows = []

    for algorithm, result in comparison.items():
        comparison_rows.append({
            "Algorithm": algorithm,
            "Route": " → ".join(result["path"]) if result.get("path") else "No route",
            "Weighted Cost": round(result["cost"], 2) if result.get("path") else None,
            "Execution Time (ms)": round(float(result.get("time_ms", 0)), 4),
        })

    comparison_df = pd.DataFrame(comparison_rows)
    if comparison_df.empty:
        st.warning("No comparison results were returned for this route.")
    else:
        st.dataframe(
            comparison_df,
            width="stretch",
            hide_index=True,
            key="algorithm_comparison_table",
        )
        st.bar_chart(
            comparison_df.set_index("Algorithm")["Execution Time (ms)"]
        )
        st.caption(
            "Execution time depends on the computer and system load. "
            "Repeat tests and compare averages for better results."
        )

# --------------------------------------------------
# ROUTE CAPACITY MANAGEMENT
# --------------------------------------------------

st.divider()
st.subheader("🚦 Route Capacity Management")

st.caption(
    "Select a route to block or reopen it in the MySQL database."
)

if backend_routes_data is None:
    st.error("Could not load routes from the Flask backend. Check that Flask is running.")

if backend_routes_data:
    route_options = {
        (
            f"{route['source']} ↔ {route['destination']} "
            f"(ID: {route['route_id']})"
        ): route
        for route in backend_routes_data
    }

    selected_label = st.selectbox(
        "Select database route",
        list(route_options.keys()),
        key="database_route_selection"
    )

    selected_route = route_options[selected_label]

    is_blocked = selected_route["is_blocked"]

    if is_blocked:
        st.warning("This database route is currently blocked.")
    else:
        st.success("This database route is currently available.")

    col_a, col_b = st.columns(2)

    with col_a:
        if st.button(
            "Block Selected Route",
            disabled=is_blocked,
            use_container_width=True
        ):
            result = update_route_api(
                selected_route["route_id"],
                True
            )

            if result.get("status") == "success":
                st.success("Route blocked in the database.")
                st.rerun()
            else:
                st.error(result.get("message", "Unable to block route."))

    with col_b:
        if st.button(
            "Reopen Selected Route",
            disabled=not is_blocked,
            use_container_width=True
        ):
            result = update_route_api(
                selected_route["route_id"],
                False
            )

            if result.get("status") == "success":
                st.success("Route reopened in the database.")
                st.rerun()
            else:
                st.error(result.get("message", "Unable to reopen route."))

else:
    st.info("No database routes are available to manage.")


# --------------------------------------------------
# PRIM'S ALGORITHM: MST RESULTS
# --------------------------------------------------

st.divider()
st.subheader("🌳 Minimum Spanning Tree — Prim's Algorithm")

st.write(
    "Prim's algorithm finds a minimum-distance set of connections "
    "that connects all airports in the available network."
)

if st.button("Generate Minimum Spanning Tree", type="primary"):
    mst_edges, total_mst_distance = prim_mst(graph)

    if len(AIRPORTS) > 1 and len(mst_edges) != len(AIRPORTS) - 1:
        st.error(
            "The network is disconnected. Reopen some routes "
            "to connect all airports before generating the MST."
        )
    else:
        st.success("Minimum Spanning Tree generated successfully!")

        st.metric(
            "Total MST Distance",
            f"{total_mst_distance:,} km",
        )
        st.metric("Connections in MST", len(mst_edges))

        mst_rows = [
            {
                "Airport 1": a,
                "Airport 2": b,
                "Distance (km)": distance,
            }
            for a, b, distance in mst_edges
        ]

        mst_df = pd.DataFrame(mst_rows)
        mst_df_styled = mst_df.style.set_properties(
            **{"background-color": "#ffffff", "color": "#243b53", "border-color": "#d9e6f5"}
        ).set_table_styles([
            {"selector": "th", "props": [
                ("background-color", "#e7f0fc"),
                ("color", "#173e67"),
                ("font-weight", "600"),
                ("border-color", "#d9e6f5"),
            ]},
        ])
        st.dataframe(
            mst_df_styled,
            width="stretch",
            hide_index=True,
            key="mst_results_table",
        )

st.caption(
    "Educational simulation only. Airport positions, route distances, "
    "capacities and traffic are illustrative. This system does not "
    "connect to or control real aircraft."
)


# --------------------------------------------------
# ALGORITHM COMPLEXITY ANALYSIS
# --------------------------------------------------

st.divider()
st.subheader("📚 Algorithm Complexity Analysis")

complexity_data = [
    {
        "Algorithm": "Dijkstra's Algorithm",
        "Purpose": "Shortest path",
        "Time Complexity": "O((V + E) log V)",
        "Space Complexity": "O(V + E)",
    },
    {
        "Algorithm": "A* Search",
        "Purpose": "Heuristic-guided pathfinding",
        "Time Complexity": "Depends on heuristic; worst case can be exponential",
        "Space Complexity": "Can be exponential",
    },
    {
        "Algorithm": "Prim's Algorithm",
        "Purpose": "Minimum Spanning Tree",
        "Time Complexity": "O(E log V)",
        "Space Complexity": "O(V + E)",
    },
]

complexity_df = pd.DataFrame(complexity_data)
complexity_df_styled = complexity_df.style.set_properties(
    **{"background-color": "#ffffff", "color": "#243b53", "border-color": "#d9e6f5"}
).set_table_styles([
    {"selector": "th", "props": [
        ("background-color", "#e7f0fc"),
        ("color", "#173e67"),
        ("font-weight", "600"),
        ("border-color", "#d9e6f5"),
    ]},
])
st.dataframe(
    complexity_df_styled,
    width="stretch",
    hide_index=True,
    key="complexity_table",
)

st.caption(
    "V = number of airports (vertices), E = number of routes (edges). "
    "Complexities depend on the implementation and data structures used."
)


# --------------------------------------------------
# ROUTE DETAILS AND CONGESTION ANALYSIS
# --------------------------------------------------

st.divider()
st.subheader("📋 Route Details & Congestion Analysis")

route_details = []

for route in ROUTES:
    source_airport = route["source"]
    destination_airport = route["destination"]
    route_key = tuple(sorted((source_airport, destination_airport)))

    traffic = st.session_state.congestion.get(route_key, 0)
    capacity = route["capacity"]

    is_blocked = route_key in effective_blocked_routes

    if is_blocked:
        status = "Blocked"
    elif traffic >= capacity:
        status = "Congested"
    else:
        status = "Available"

    route_details.append({
        "Source": source_airport,
        "Destination": destination_airport,
        "Distance (km)": route["distance"],
        "Capacity": capacity,
        "Traffic": traffic,
        "Traffic Usage (%)": round((traffic / capacity) * 100, 1),
        "Status": status,
    })

route_df = pd.DataFrame(route_details)

status_filter = st.selectbox(
    "Filter routes by status",
    ["All", "Available", "Congested", "Blocked"],
    key="route_status_filter",
)

if status_filter != "All":
    route_df = route_df[route_df["Status"] == status_filter]

route_df_styled = route_df.style.set_properties(
    **{"background-color": "#ffffff", "color": "#243b53", "border-color": "#d9e6f5"}
).set_table_styles([
    {"selector": "th", "props": [
        ("background-color", "#e7f0fc"),
        ("color", "#173e67"),
        ("font-weight", "600"),
        ("border-color", "#d9e6f5"),
    ]},
    {"selector": "td", "props": [("border-color", "#d9e6f5")]},
])

st.dataframe(
    route_df_styled,
    width="stretch",
    hide_index=True,
    key="route_details_table",
)

st.caption(
    "Traffic values are simulated for this educational project. "
    "They are not live aircraft traffic data."
)

# --------------------------------------------------
# PROFESSIONAL FOOTER
# --------------------------------------------------

st.markdown("""
<div class="project-footer">
    <div class="footer-plane">✈️</div>
    <div class="footer-title">Air Traffic Flow Optimization System</div>
    <div class="footer-tagline">Intelligent Flight Route Planning &amp; Optimization</div>
    <div class="footer-divider"></div>
    <div class="footer-author">Developed by: <strong>Bhumika</strong></div>
    <div class="footer-meta">Academic Project · 2026</div>
</div>
<style>
.project-footer {
    margin-top: 3rem;
    padding: 2rem 1rem 1.5rem;
    text-align: center;
    border-top: 1px solid #d5e3f3;
    color: #173e67;
}
.footer-plane { font-size: 1.8rem; margin-bottom: .35rem; }
.footer-title { font-size: 1.15rem; font-weight: 750; }
.footer-tagline { color: #6c829b; font-size: .92rem; margin-top: .35rem; }
.footer-divider { width: 72px; height: 3px; background: #2878c8; border-radius: 4px; margin: 1rem auto; }
.footer-author { font-size: .95rem; }
.footer-meta { color: #8093a8; font-size: .78rem; margin-top: .45rem; }
</style>
""", unsafe_allow_html=True)

