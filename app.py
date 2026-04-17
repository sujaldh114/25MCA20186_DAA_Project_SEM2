from flask import Flask, render_template, request, jsonify
import heapq
from collections import deque

app = Flask(__name__)

# HEURISTIC (Manhattan Distance)
def heuristic(a, b):
    return abs(a[0] - b[0]) + abs(a[1] - b[1])

# A* ALGORITHM
def astar(grid, start, goal):
    open_set = []
    heapq.heappush(open_set, (0, start))

    came_from = {}
    g_score = {start: 0}
    closed = set()

    while open_set:
        _, current = heapq.heappop(open_set)

        if current in closed:
            continue
        closed.add(current)

        if current == goal:
            path = []
            while current in came_from:
                path.append(current)
                current = came_from[current]
            path.append(start)
            return path[::-1], g_score[goal]

        for dx, dy in [(1,0),(-1,0),(0,1),(0,-1)]:
            nx, ny = current[0] + dx, current[1] + dy

            if 0 <= nx < len(grid) and 0 <= ny < len(grid[0]):
                if grid[nx][ny] == -1:
                    continue

                cost = grid[nx][ny]
                temp_g = g_score[current] + cost

                if (nx, ny) not in g_score or temp_g < g_score[(nx, ny)]:
                    g_score[(nx, ny)] = temp_g
                    f = temp_g + heuristic((nx, ny), goal)
                    heapq.heappush(open_set, (f, (nx, ny)))
                    came_from[(nx, ny)] = current

    return [], 0

# DIJKSTRA
def dijkstra(grid, start, goal):
    pq = [(0, start)]
    dist = {start: 0}
    parent = {}

    while pq:
        cost, node = heapq.heappop(pq)

        if node == goal:
            path = []
            while node in parent:
                path.append(node)
                node = parent[node]
            path.append(start)
            return path[::-1], cost

        for dx, dy in [(1,0),(-1,0),(0,1),(0,-1)]:
            nx, ny = node[0] + dx, node[1] + dy

            if 0 <= nx < len(grid) and 0 <= ny < len(grid[0]):
                if grid[nx][ny] == -1:
                    continue

                new_cost = cost + grid[nx][ny]

                if (nx, ny) not in dist or new_cost < dist[(nx, ny)]:
                    dist[(nx, ny)] = new_cost
                    parent[(nx, ny)] = node
                    heapq.heappush(pq, (new_cost, (nx, ny)))

    return [], 0

# BFS
def bfs(grid, start, goal):
    q = deque([start])
    parent = {}
    visited = set([start])

    while q:
        node = q.popleft()

        if node == goal:
            path = []
            while node in parent:
                path.append(node)
                node = parent[node]
            path.append(start)
            return path[::-1], len(path) - 1

        for dx, dy in [(1,0),(-1,0),(0,1),(0,-1)]:
            nx, ny = node[0] + dx, node[1] + dy

            if 0 <= nx < len(grid) and 0 <= ny < len(grid[0]):
                if grid[nx][ny] == -1:
                    continue

                if (nx, ny) not in visited:
                    visited.add((nx, ny))
                    parent[(nx, ny)] = node
                    q.append((nx, ny))

    return [], 0

# DFS
def dfs(grid, start, goal):
    stack = [start]
    parent = {}
    visited = set([start])

    while stack:
        node = stack.pop()

        if node == goal:
            path = []
            while node in parent:
                path.append(node)
                node = parent[node]
            path.append(start)
            return path[::-1], len(path) - 1

        for dx, dy in [(1,0),(-1,0),(0,1),(0,-1)]:
            nx, ny = node[0] + dx, node[1] + dy

            if 0 <= nx < len(grid) and 0 <= ny < len(grid[0]):
                if grid[nx][ny] == -1:
                    continue

                if (nx, ny) not in visited:
                    visited.add((nx, ny))
                    parent[(nx, ny)] = node
                    stack.append((nx, ny))

    return [], 0

# BEST FIRST SEARCH
def best_first(grid, start, goal):
    pq = []
    heapq.heappush(pq, (heuristic(start, goal), start))

    parent = {}
    visited = set([start])

    while pq:
        _, node = heapq.heappop(pq)

        if node == goal:
            path = []
            while node in parent:
                path.append(node)
                node = parent[node]
            path.append(start)
            return path[::-1], len(path) - 1

        for dx, dy in [(1,0),(-1,0),(0,1),(0,-1)]:
            nx, ny = node[0] + dx, node[1] + dy

            if 0 <= nx < len(grid) and 0 <= ny < len(grid[0]):
                if grid[nx][ny] == -1:
                    continue

                if (nx, ny) not in visited:
                    visited.add((nx, ny))
                    parent[(nx, ny)] = node
                    heapq.heappush(pq, (heuristic((nx, ny), goal), (nx, ny)))

    return [], 0

# HILL CLIMBING
def hill_climbing(grid, start, goal):
    current = start
    path = [current]

    while current != goal:
        neighbors = []

        for dx, dy in [(1,0),(-1,0),(0,1),(0,-1)]:
            nx, ny = current[0] + dx, current[1] + dy

            if 0 <= nx < len(grid) and 0 <= ny < len(grid[0]):
                if grid[nx][ny] != -1:
                    neighbors.append((nx, ny))

        if not neighbors:
            return [], 0

        next_node = min(neighbors, key=lambda x: heuristic(x, goal))

        if heuristic(next_node, goal) >= heuristic(current, goal):
            return path, len(path) - 1  # stuck (local maxima)

        current = next_node
        path.append(current)

    return path, len(path) - 1

# ROUTE API
@app.route("/route", methods=["POST"])
def route():
    data = request.json

    grid = data["grid"]
    start = tuple(data["start"])
    goals = [tuple(g) for g in data["goals"]]
    algo = data.get("algo", "astar")

    full_path = []
    total_cost = 0
    current = start
    remaining = goals[:]

    while remaining:
        nearest = min(remaining, key=lambda g: heuristic(current, g))

        if algo == "astar":
            path, cost = astar(grid, current, nearest)
        elif algo == "dijkstra":
            path, cost = dijkstra(grid, current, nearest)
        elif algo == "bfs":
            path, cost = bfs(grid, current, nearest)
        elif algo == "dfs":
            path, cost = dfs(grid, current, nearest)
        elif algo == "best_first":
            path, cost = best_first(grid, current, nearest)
        elif algo == "hill_climbing":
            path, cost = hill_climbing(grid, current, nearest)
        else:
            return jsonify({"error": "Invalid algorithm"}), 400

        if path:
            if full_path:
                full_path += path[1:]
            else:
                full_path += path

            total_cost += cost
            current = nearest

        remaining.remove(nearest)

    return jsonify({
        "path": full_path,
        "cost": total_cost
    })

# HOME PAGE
@app.route("/")
def home():
    return render_template("index.html")

# RUN SERVER
if __name__ == "__main__":
    app.run(debug=True)