
# ✈️ Air Traffic Flow Optimization System

A graph-based route optimization system developed as an MCA-level Design and Analysis of Algorithms (DAA) project.

## 📌 Project Overview

The Air Traffic Flow Optimization System helps find efficient routes between airports using graph algorithms. It models airports as vertices and flight routes as weighted edges, where weights represent route distances.

The system demonstrates how algorithmic techniques can help identify shortest paths and alternative routes when a route is blocked.

## 🎯 Objectives

- Represent airports and routes using graph data structures.
- Find shortest routes between airports.
- Compare Dijkstra's algorithm and A* search.
- Generate a Minimum Spanning Tree using Prim's algorithm.
- Handle blocked routes and find alternative paths.
- Store airport and route information in a MySQL database.
- Visualize and analyze route optimization through an interactive dashboard.

## 🚀 Features

- Interactive Streamlit dashboard.
- Airport and route visualization.
- Shortest-path calculation.
- Dijkstra's algorithm and A* search comparison.
- Minimum Spanning Tree using Prim's algorithm.
- Route blocking and alternative-route testing.
- Flask REST API for route optimization.
- MySQL database integration.
- Algorithm complexity analysis.

## 🧠 Algorithms Used

### 1. Dijkstra's Algorithm
Finds a shortest path between a source airport and a destination airport using non-negative edge weights.

### 2. A* Search Algorithm
Uses path cost and a heuristic estimate to guide the search toward the destination.

### 3. Prim's Minimum Spanning Tree
Constructs a minimum spanning tree for a connected, undirected weighted graph.

## 🛠️ Technologies Used

- Python
- Streamlit
- Flask
- MySQL
- NetworkX
- Pandas
- Plotly
- REST API

## 📂 Project Structure

```text
AirTrafficOptimization/
├── app.py
├── airports.py
├── algorithms.py
├── requirements.txt
├── .gitignore
├── README.md
└── backend/
    ├── app.py
    ├── database.py
    ├── seed_database.py
    └── test_connection.py
```

## ⚙️ Installation and Setup

### Prerequisites

- Python 3
- MySQL Server
- Git

### 1. Clone the repository

```bash
git clone https://github.com/jainbhumika337-debug/Air-Traffic-Flow-Optimization-System.git
cd Air-Traffic-Flow-Optimization-System
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure the database

Configure your MySQL database credentials using the environment variables expected by the backend. Keep passwords and other secrets out of source control.

Create and initialize the required database and tables according to the project's database setup.

### 4. Start the Flask backend

Open a terminal in the project root and run:

```powershell
python backend/app.py
```

### 5. Start the Streamlit dashboard

Open another terminal in the project root and run:

```powershell
python -m streamlit run app.py
```

Open the local URL displayed by Streamlit in your browser.

## 📊 DAA Concepts Demonstrated

- Graph representation
- Weighted graphs
- Shortest-path algorithms
- Heuristic search
- Minimum Spanning Tree
- Time and space complexity analysis
- Algorithm comparison

## 🎓 Project Scope

This project is an educational prototype for demonstrating graph algorithms and route optimization. It does not connect to live air traffic control systems or provide operational flight guidance.

## 👩‍💻 Author

**Bhumika**

MCA — Design and Analysis of Algorithms Project
