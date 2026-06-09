import json
import random
import numpy as np
from scipy.spatial import Delaunay

class Room:
    def __init__(self, room_id, x, y, w, h):
        self.room_id = f"room_{room_id}"
        self.x = int(x)
        self.y = int(y)
        self.w = int(w)
        self.h = int(h)

    @property
    def center(self):
        return (self.x + self.w // 2, self.y + self.h // 2)

    def intersects(self, other, padding=2):
        return not (self.x + self.w + padding < other.x or
                    self.x > other.x + other.w + padding or
                    self.y + self.h + padding < other.y or
                    self.y > other.y + other.h + padding)

    def to_dict(self):
        return {
            "id": self.room_id,
            "position": {"x": self.x, "y": self.y},
            "size": {"width": self.w, "height": self.h},
            "center": {"x": self.center[0], "y": self.center[1]},
            "connected_paths": []  # Will be populated during graph generation
        }

def kruskal_mst(num_nodes, edges):
    parent = list(range(num_nodes))
    def find(i):
        if parent[i] == i: return i
        parent[i] = find(parent[i])
        return parent[i]
    def union(i, j):
        root_i, root_j = find(i), find(j)
        if root_i != root_j:
            parent[root_i] = root_j
            return True
        return False

    sorted_edges = sorted(edges, key=lambda e: e[2])
    mst_edges = []
    discarded_edges = []
    for u, v, w in sorted_edges:
        if union(u, v): mst_edges.append((u, v))
        else: discarded_edges.append((u, v, w))
    return mst_edges, discarded_edges

def generate_layout_json(width=100, height=100, num_rooms=15, loop_back_chance=0.20):
    # 1. Spawn overlapping rooms
    rooms = []
    for i in range(num_rooms):
        w = random.randint(6, 12)
        h = random.randint(6, 12)
        r = 12
        theta = random.random() * 2 * np.pi
        x = (width // 2) + r * np.cos(theta) - w // 2
        y = (height // 2) + r * np.sin(theta) - h // 2
        rooms.append(Room(i, x, y, w, h))

    # 2. Separate rooms via physics forces
    for _ in range(120):
        for i, r1 in enumerate(rooms):
            for j, r2 in enumerate(rooms):
                if i == j: continue
                if r1.intersects(r2):
                    cx1, cy1 = r1.center
                    cx2, cy2 = r2.center
                    dx, dy = cx1 - cx2, cy1 - cy2
                    dist = np.hypot(dx, dy) or 0.1
                    r1.x += (dx / dist) * 0.5
                    r1.y += (dy / dist) * 0.5
                    r2.x -= (dx / dist) * 0.5
                    r2.y -= (dy / dist) * 0.5

    # Snap to integer grid space
    for r in rooms:
        r.x = max(2, min(width - r.w - 2, int(r.x)))
        r.y = max(2, min(height - r.h - 2, int(r.y)))

    # 3. Delaunay Triangulation
    centers = np.array([r.center for r in rooms])
    tri = Delaunay(centers)
    edges_dict = {}
    for simplex in tri.simplices:
        for i in range(3):
            u, v = simplex[i], simplex[(i + 1) % 3]
            if u > v: u, v = v, u
            dist = np.hypot(centers[u][0] - centers[v][0], centers[u][1] - centers[v][1])
            edges_dict[(u, v)] = dist

    all_edges = [(u, v, w) for (u, v), w in edges_dict.items()]

    # 4. Filter with MST + Loops
    mst_edges, discarded = kruskal_mst(len(rooms), all_edges)
    final_edges = set(mst_edges)
    for u, v, w in discarded:
        if random.random() < loop_back_chance:
            final_edges.add((u, v))

    # 5. Build structured JSON response
    rooms_map = {r.room_id: r.to_dict() for r in rooms}
    paths_list = []

    for path_index, (u, v) in enumerate(final_edges):
        path_id = f"path_{path_index}"
        room_a = rooms[u]
        room_b = rooms[v]

        # Define path structure
        path_data = {
            "id": path_id,
            "connects": [room_a.room_id, room_b.room_id],
            "points": [
                {"x": room_a.center[0], "y": room_a.center[1]},
                {"x": room_b.center[0], "y": room_b.center[1]}
            ]
        }
        paths_list.append(path_data)

        # Cross-reference the path back into the respective rooms
        rooms_map[room_a.room_id]["connected_paths"].append(path_id)
        rooms_map[room_b.room_id]["connected_paths"].append(path_id)

    output_data = {
        "rooms": list(rooms_map.values()),
        "paths": paths_list
    }

    return json.dumps(output_data, indent=4)

if __name__ == "__main__":
    # Generate abstract topological map data
    dungeon_json = generate_layout_json(num_rooms=6, loop_back_chance=0.20)
    print(dungeon_json)