# 🏫 Campus Navigator - Shortest Path Finder

A beginner-friendly web application built with **Python, Flask, HTML, CSS, JavaScript, Graph Data Structures, and Breadth-First Search (BFS)**.

---

## 📌 Project Overview
Campus Navigator helps college students find the shortest walking route between 14 campus locations. It represents campus paths as an **undirected graph** (using an Adjacency List) and applies **Breadth-First Search (BFS)** using Python's `collections.deque` to find the path with the minimum number of connections (hops).

---

## 📂 Project Directory Structure

```text
DSA Campus/
├── CampusNavigator/
│   ├── static/
│   │   ├── style.css          # Modern dark-theme styling & responsive UI
│   │   └── script.js          # Interactive SVG map, AJAX requests, route highlight
│   ├── templates/
│   │   └── index.html         # HTML layout, SVG campus schematic map, timeline
│   ├── __init__.py            # Package initializer
│   ├── app.py                 # Flask app & API endpoints (/api/route, /api/graph)
│   ├── campus_graph.py        # Graph adjacency list & BFS algorithm
│   ├── test_navigator.py      # Automated unit tests for Graph & BFS
│   └── requirements.txt       # Dependencies (Flask)
│
├── static/                    # Root static assets mirror
│   ├── style.css
│   └── script.js
├── templates/                 # Root templates mirror
│   └── index.html
├── app.py                     # Root launcher (runs from project folder directly)
├── campus_graph.py            # Root graph module
├── test_campus_navigator.py   # Full automated test suite
├── requirements.txt           # Project dependencies
└── README.md                  # Complete documentation and viva guide
```

---

## 🚀 How to Run the Application Locally

### 1. Prerequisites Check
Make sure Python is installed. To verify in your terminal / PowerShell:
```powershell
python --version
```
*(Python 3.13.3 is already installed on your system!)*

### 2. Install Flask
If Flask is not yet installed in your Python environment, install it by running:
```powershell
pip install flask
```
*(or `pip install -r requirements.txt`)*

### 3. Start the Web Server
You can start the app directly from your project directory:
```powershell
python app.py
```
Or from inside the `CampusNavigator` folder:
```powershell
cd CampusNavigator
python app.py
```

### 4. Open the Website in Your Browser
Once running, open your web browser and navigate to:
```
http://127.0.0.1:5000
```

---

## 🧪 Running the Automated Tests
We have built an automated test suite verifying all project criteria:
```powershell
python test_campus_navigator.py
```
This tests:
1. **Library &rarr; CUS**: Verifies the shortest route `Library → Botany Tank → Principal's Residence → MRF → Bell Tower → CUS` with exactly **5 connections**.
2. **Same Start & Destination**: Verifies 0 connections when start equals destination.
3. **Invalid Locations**: Verifies error handling and graceful feedback.
4. **Graph Symmetry**: Verifies all 15 walkways are bidirectional.
5. **Connectivity**: Verifies all 14 campus locations are reachable.

---

## 💡 How the Data Structures & Algorithm Work

### 1. Graph (Adjacency List)
The campus is represented as an undirected graph using a Python dictionary:
- **Vertices (Nodes)**: 14 campus landmarks and buildings.
- **Edges**: Walkways connecting them.
- **Adjacency List**: Each location maps to a list of neighboring locations directly accessible on foot.

### 2. Breadth-First Search (BFS)
- Uses a **FIFO Queue** (`collections.deque`) which allows $O(1)$ pop operations from the front.
- BFS traverses level-by-level (all 1-hop neighbors, then 2-hop neighbors, etc.).
- The first time the target location is dequeued/reached, the path is **mathematically guaranteed to be the shortest path in terms of connections (edges)**.
- A `visited` set tracks visited locations to prevent infinite loops and cyclic walking.
- **Time Complexity**: $O(V + E)$ where $V = 14$ locations and $E = 15$ walkways.
