from pathlib import Path
import random
import numpy as np
from scipy.spatial import Delaunay
from PIL import Image

class Room:
    def __init__(self, x, y, w, h):
        self.x = float(x)
        self.y = float(y)
        self.w = w
        self.h = h

    @property
    def center(self):
        return (self.x + self.w / 2, self.y + self.h / 2)

    def intersects(self, other, padding=2):
        return not (self.x + self.w + padding < other.x or
                    self.x > other.x + other.w + padding or
                    self.y + self.h + padding < other.y or
                    self.y > other.y + other.h + padding)

def kruskal_mst(num_nodes, edges):
    """Computes the Minimum Spanning Tree using Kruskal's Algorithm."""
    parent = list(range(num_nodes))
    
    def find(i):
        if parent[i] == i:
            return i
        parent[i] = find(parent[i])
        return parent[i]

    def union(i, j):
        root_i = find(i)
        root_j = find(j)
        if root_i != root_j:
            parent[root_i] = root_j
            return True
        return False

    # Sort edges by distance
    sorted_edges = sorted(edges, key=lambda e: e[2])
    mst_edges = []
    discarded_edges = []

    for u, v, w in sorted_edges:
        if union(u, v):
            mst_edges.append((u, v))
        else:
            discarded_edges.append((u, v, w))
            
    return mst_edges, discarded_edges

def generate_delaunay_mst_dungeon(width=100, height=100, num_rooms=30, loop_back_chance=0.15):
    # 1. Spawn overlapping rooms in a tight circle at the center
    rooms = []
    for _ in range(num_rooms):
        w = random.randint(6, 12)
        h = random.randint(6, 12)
        # Radius of placement circle
        r = 10
        theta = random.random() * 2 * np.pi
        x = (width // 2) + r * np.cos(theta) - w // 2
        y = (height // 2) + r * np.sin(theta) - h // 2
        rooms.append(Room(x, y, w, h))

    # 2. Separate rooms using basic steering/push forces
    for _ in range(150): # Iterations to resolve overlap
        for i, r1 in enumerate(rooms):
            for j, r2 in enumerate(rooms):
                if i == j: continue
                if r1.intersects(r2):
                    cx1, cy1 = r1.center
                    cx2, cy2 = r2.center
                    dx, dy = cx1 - cx2, cy1 - cy2
                    dist = np.hypot(dx, dy) or 0.1
                    # Push away
                    r1.x += (dx / dist) * 0.5
                    r1.y += (dy / dist) * 0.5
                    r2.x -= (dx / dist) * 0.5
                    r2.y -= (dy / dist) * 0.5

    # Round room positions to integer grid coordinates & snap within bounds
    for r in rooms:
        r.x = max(2, min(width - r.w - 2, int(r.x)))
        r.y = max(2, min(height - r.h - 2, int(r.y)))

    # 3. Create Delaunay Triangulation from room centers
    centers = np.array([r.center for r in rooms])
    tri = Delaunay(centers)
    
    # Extract unique edges from triangulation
    edges_dict = {}
    for simplex in tri.simplices:
        for i in range(3):
            u, v = simplex[i], simplex[(i + 1) % 3]
            if u > v: u, v = v, u  # Normalize direction
            dist = np.hypot(centers[u][0] - centers[v][0], centers[u][1] - centers[v][1])
            edges_dict[(u, v)] = dist

    all_edges = [(u, v, w) for (u, v), w in edges_dict.items()]

    # 4. Generate MST and add back a few loops
    mst_edges, discarded = kruskal_mst(len(rooms), all_edges)
    
    final_edges = set(mst_edges)
    for u, v, w in discarded:
        if random.random() < loop_back_chance:
            final_edges.add((u, v))

    # 5. Burn everything down into a 2D binary grid
    grid = np.ones((height, width), dtype=np.uint8)

    # Carve rooms
    for r in rooms:
        grid[int(r.y):int(r.y+r.h), int(r.x):int(r.x+r.w)] = 0

    # Carve L-shaped corridors along final graph edges
    for u, v in final_edges:
        cx1, cy1 = map(int, rooms[u].center)
        cx2, cy2 = map(int, rooms[v].center)
        
        # Horizontal then Vertical
        if random.choice([True, False]):
            grid[cy1, min(cx1, cx2):max(cx1, cx2)+1] = 0
            grid[min(cy1, cy2):max(cy1, cy2)+1, cx2] = 0
        # Vertical then Horizontal
        else:
            grid[min(cy1, cy2):max(cy1, cy2)+1, cx1] = 0
            grid[cy2, min(cx1, cx2):max(cx1, cx2)+1] = 0

    return grid

def save_layout_as_png(grid, filename="delaunay_mst_layout.png", scale=8):
    img_data = np.where(grid == 0, 255, 0).astype(np.uint8)
    img = Image.fromarray(img_data, mode='L')
    new_size = (img.width * scale, img.height * scale)
    img = img.resize(new_size, resample=Image.Resampling.NEAREST)
    #img.save(filename)
    path = Path(filename)

    # Find the next available filename
    if path.exists():
        stem = path.stem
        suffix = path.suffix
        counter = 1

        while True:
            new_path = path.with_name(f"{stem}_{counter}{suffix}")
            if not new_path.exists():
                path = new_path
                break
            counter += 1

    img.save(path)
    print(f"Graph-based layout successfully saved to '{filename}' ({new_size[0]}x{new_size[1]} px)")

if __name__ == "__main__":
    # Generate a layout from 22 physics-separated structural rooms
    width = 120
    height = 120
    num_rooms = 22
    loop_back_chance = 0.05
    dungeon_grid = generate_delaunay_mst_dungeon(width, height, num_rooms, loop_back_chance)
    save_layout_as_png(dungeon_grid, f"delaunay_mst_layout_{num_rooms}_{loop_back_chance}.png", scale=6)
    
    
    
    #loop_back_chance (0.05 - 0.25): Controls the cyclic density.
        #At 0.00, the dungeon is a strict tree with zero loops (dead ends everywhere).
        #At 0.20, one-fifth of alternative paths are re-opened, building cycling loops, flanking paths, and shortcut corridors.
    #num_rooms: How many initial rooms are spawned into the cluster before physics pushes them apart.
        #Too many rooms relative to the width/height boundaries will cause the physics step to mash rooms right up against the borders.