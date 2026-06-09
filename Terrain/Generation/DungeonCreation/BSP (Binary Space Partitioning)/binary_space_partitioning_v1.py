from pathlib import Path
import random
import numpy as np
from PIL import Image

class Leaf:
    def __init__(self, x, y, width, height, min_size):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.min_size = min_size  # Minimum size of a leaf
        
        self.child_1 = None
        self.child_2 = None
        self.room = None
        self.corridors = []

    def split(self):
        # If already split, do nothing
        if self.child_1 or self.child_2:
            return False

        # Determine direction of split
        # If width is much greater than height, split vertically
        # If height is much greater than width, split horizontally
        # Otherwise, choose randomly
        if self.width / self.height >= 1.25:
            split_h = False
        elif self.height / self.width >= 1.25:
            split_h = True
        else:
            split_h = random.choice([True, False])

        max_size = (self.height if split_h else self.width) - self.min_size
        if max_size <= self.min_size:
            return False  # Too small to split

        split_pos = random.randint(self.min_size, max_size)

        if split_h:
            self.child_1 = Leaf(self.x, self.y, self.width, split_pos, self.min_size)
            self.child_2 = Leaf(self.x, self.y + split_pos, self.width, self.height - split_pos, self.min_size)
        else:
            self.child_1 = Leaf(self.x, self.y, split_pos, self.height, self.min_size)
            self.child_2 = Leaf(self.x + split_pos, self.y, self.width - split_pos, self.height, self.min_size)
            
        return True

    def create_rooms(self):
        """Recursively generate rooms in the leaf nodes."""
        if self.child_1 or self.child_2:
            if self.child_1:
                self.child_1.create_rooms()
            if self.child_2:
                self.child_2.create_rooms()
            
            # Connect children rooms with a corridor
            if self.child_1 and self.child_2:
                self.create_corridor(self.child_1.get_room(), self.child_2.get_room())
        else:
            # Create a room inside this leaf
            # Leave at least a 1-tile border inside the partition
            room_w = random.randint(self.min_size // 2, self.width - 2)
            room_h = random.randint(self.min_size // 2, self.height - 2)
            
            room_x = random.randint(1, self.width - room_w - 1)
            room_y = random.randint(1, self.height - room_h - 1)
            
            self.room = (self.x + room_x, self.y + room_y, room_w, room_h)

    def get_room(self):
        """Iterate down the tree to find a valid room instance."""
        if self.room:
            return self.room
        
        # If this is an intermediate partition, grab a room from a child node
        r1 = self.child_1.get_room() if self.child_1 else None
        r2 = self.child_2.get_room() if self.child_2 else None
        
        if r1 and r2:
            return random.choice([r1, r2])
        return r1 if r1 else r2

    def create_corridor(self, room1, room2):
        """Draws a simple L-shaped corridor connecting the centers of two rooms."""
        if not room1 or not room2:
            return

        # Get centers of both rooms
        cx1, cy1 = room1[0] + room1[2] // 2, room1[1] + room1[3] // 2
        cx2, cy2 = room2[0] + room2[2] // 2, room2[1] + room2[3] // 2

        # Randomly choose whether to go horizontal-then-vertical or vice-versa
        if random.choice([True, False]):
            self.corridors.append((cx1, cy1, cx2, cy1)) # Horiz
            self.corridors.append((cx2, cy1, cx2, cy2)) # Vert
        else:
            self.corridors.append((cx1, cy1, cx1, cy2)) # Vert
            self.corridors.append((cx1, cy2, cx2, cy2)) # Horiz


def generate_bsp_dungeon(width=80, height=80, max_leaf_size=20, min_size=10):
    """
    Manages the overall BSP process, flattening the tree down into a 2D grid matrix.
    
    1 = Wall (Black)
    0 = Floor (White)
    """
    grid = np.ones((height, width), dtype=np.uint8)
    
    # Initialize the root node
    root = Leaf(0, 0, width, height, min_size)
    leafs = [root]
    
    # Split the partitions iteratively
    did_split = True
    while did_split:
        did_split = False
        for l in list(leafs):
            if l.child_1 is None and l.child_2 is None:
                # If this leaf is too large, split it
                if l.width > max_leaf_size or l.height > max_leaf_size or random.random() > 0.25:
                    if l.split():
                        leafs.append(l.child_1)
                        leafs.append(l.child_2)
                        did_split = True
                        
    # Carve rooms and corridors on the tree structure
    root.create_rooms()
    
    # Flatten the tree structure onto our 2D grid array
    def carve_leaf(node):
        if node.room:
            rx, ry, rw, rh = node.room
            grid[ry:ry+rh, rx:rx+rw] = 0
            
        for corr in node.corridors:
            x1, y1, x2, y2 = corr
            # Sort coordinates so slice ranges function correctly
            start_x, end_x = min(x1, x2), max(x1, x2)
            start_y, end_y = min(y1, y2), max(y1, y2)
            grid[start_y:end_y+1, start_x:end_x+1] = 0
            
        if node.child_1: carve_leaf(node.child_1)
        if node.child_2: carve_leaf(node.child_2)

    carve_leaf(root)
    return grid

def save_layout_as_png(grid, filename="bsp_layout.png", scale=8):
    """Converts the 0/1 grid into a high-contrast crisp PNG."""
    img_data = np.where(grid == 0, 255, 0).astype(np.uint8)
    img = Image.fromarray(img_data, mode='L')
    
    new_size = (img.width * scale, img.height * scale)
    img = img.resize(new_size, resample=Image.Resampling.NEAREST)
    
    #img.save(filename)
    
    # Find the next available filename
    path = Path(filename)
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
    
    
    print(f"BSP layout successfully saved to '{filename}' ({new_size[0]}x{new_size[1]} px)")

if __name__ == "__main__":
    # Generate an 80x80 architectural dungeon layout
    width = 80
    height = 80
    max_leaf_size = 50
    min_size = 15
    dungeon_grid = generate_bsp_dungeon(width, height, max_leaf_size, min_size)
    
    save_layout_as_png(dungeon_grid, f"bsp_layout_{max_leaf_size}_{min_size}.png", scale=8)
    
    #self.min_size (Inside __init__): Dictates the absolute smallest boundaries a partition box can have.
        #Lowering this allows tiny closet-sized rooms; raising it forces large, spacious layouts.
    #max_leaf_size: Controls the splitting threshold.
        #If a room partition is larger than this setting, the code forces another split.
        #Keeping this value low produces highly dense, many-room complexes.