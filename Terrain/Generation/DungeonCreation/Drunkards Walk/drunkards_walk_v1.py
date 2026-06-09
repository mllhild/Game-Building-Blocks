from pathlib import Path
import random
import numpy as np
from PIL import Image

def generate_drunkards_walk(width=100, height=100, coverage_target=0.35, room_chance=0.05):
    """
    Generates a 2D dungeon layout using the Drunkard's Walk algorithm.
    
    1 = Wall (Black)
    0 = Floor (White)
    """
    # Start with a solid grid of walls (1)
    grid = np.ones((height, width), dtype=np.uint8)
    
    # Calculate how many floor tiles we want to carve out
    total_tiles = width * height
    target_floor_tiles = int(total_tiles * coverage_target)
    
    # Start the drunkard exactly in the middle
    x, y = width // 2, height // 2
    grid[y, x] = 0
    floor_count = 1
    
    # Movement vectors: North, South, East, West
    directions = [(0, -1), (0, 1), (1, 0), (-1, 0)]
    
    while floor_count < target_floor_tiles:
        # Pick a random direction
        dx, dy = random.choice(directions)
        
        # Calculate new position
        new_x = x + dx
        new_y = y + dy
        
        # Ensure the drunkard stays inside the map boundaries 
        # (leaving a 1-tile border of permanent wall)
        if 0 < new_x < width - 1 and 0 < new_y < height - 1:
            x, y = new_x, new_y
            
            # If it's a wall, carve it into a floor
            if grid[y, x] == 1:
                grid[y, x] = 0
                floor_count += 1
                
                # OPTIONAL: Occasionally spawn a small room to break up narrow tunnels
                if random.random() < room_chance:
                    room_w = random.randint(3, 6)
                    room_h = random.randint(3, 6)
                    
                    # Carve out the room centered on the current position
                    for ry in range(y - room_h//2, y + room_h//2):
                        for rx in range(x - room_w//2, x + room_w//2):
                            if 0 < rx < width - 1 and 0 < ry < height - 1:
                                if grid[ry, rx] == 1:
                                    grid[ry, rx] = 0
                                    floor_count += 1

    return grid

def save_layout_as_png(grid, filename="dungeon_layout.png", scale=8):
    """
    Converts the 0/1 grid into a high-contrast PNG.
    0 (Floor) -> White (255)
    1 (Wall)  -> Black (0)
    """
    # Map 0 to 255 (white) and 1 to 0 (black)
    img_data = np.where(grid == 0, 255, 0).astype(np.uint8)
    
    img = Image.fromarray(img_data, mode='L')
    
    # Scale up the image so it's easily viewable (1 tile = scale x scale pixels)
    new_size = (img.width * scale, img.height * scale)
    img = img.resize(new_size, resample=Image.Resampling.NEAREST)
    
    #img.save(filename)
    #print(file=None)
    
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
    
    print(f"Dungeon layout successfully saved to '{filename}' ({new_size[0]}x{new_size[1]} px)")

if __name__ == "__main__":
    # Generate a 80x80 grid, aiming to clear out 30% of it as floors
    width = 80
    height = 80
    coverage_target = 0.1
    room_chance = 0.00
    dungeon_grid = generate_drunkards_walk(width, height, coverage_target, room_chance)
    
    # Save it! Scale=8 means the output PNG will be 640x640 pixels
    save_layout_as_png(dungeon_grid, f"drunkards_walk_layout_{coverage_target}_{room_chance}.png", scale=8)
    
    
    #coverage_target (0.30 - 0.45): Controls how much of the map gets hollowed out.
        #A lower number means a shorter, more linear path.
        #A higher number will make the drunkard loop back over old paths, creating larger cavernous spaces.
    #room_chance (0.00 - 0.10):
        #Set this to 0 if you want only winding, 1-tile-wide corridors.
        #Setting it to 0.04 (4% chance per step) inserts nice square clearings dynamically.
    #scale: Because a $80 \times 80$ grid results in a tiny $80 \times 80$ pixel image, the scale factor blows it up (using nearest-neighbor interpolation) so it stays perfectly crisp and pixelated instead of blurry.
    
    
    