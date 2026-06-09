from pathlib import Path
import random
import numpy as np
from PIL import Image

def generate_cellular_automata(width=80, height=80, init_wall_chance=0.45, iterations=5):
    """
    Generates a 2D cave-like layout using Cellular Automata.
    
    1 = Wall (Black)
    0 = Floor (White)
    """
    # Step 1: Randomly initialize the grid with walls and floors
    grid = np.zeros((height, width), dtype=np.uint8)
    for y in range(height):
        for x in range(width):
            # Keep edges as permanent walls
            if x == 0 or x == width - 1 or y == 0 or y == height - 1:
                grid[y, x] = 1
            else:
                grid[y, x] = 1 if random.random() < init_wall_chance else 0

    # Step 2: Run the simulation iterations
    for _ in range(iterations):
        next_grid = np.copy(grid)
        
        for y in range(1, height - 1):
            for x in range(1, width - 1):
                # Count walls in the 3x3 neighborhood around the cell (including itself)
                neighborhood = grid[y-1:y+2, x-1:x+2]
                wall_count = np.sum(neighborhood)
                
                # Rule: If 5 or more neighbors are walls, become a wall. Otherwise, floor.
                if wall_count >= 5:
                    next_grid[y, x] = 1
                else:
                    next_grid[y, x] = 0
                    
        grid = next_grid

    return grid

def save_layout_as_png(grid, filename="cellular_automata_layout.png", scale=8):
    """Converts the 0/1 grid into a high-contrast crisp PNG."""
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
    
    
    print(f"Cave layout successfully saved to '{filename}' ({new_size[0]}x{new_size[1]} px)")

if __name__ == "__main__":
    # Generate an 80x80 cave system
    # 45% initial walls usually provides a well-balanced cave system
    init_wall_chance = 0.50
    iterations = 5
    width = 80
    height = 80
    cave_grid = generate_cellular_automata(width, height, init_wall_chance, iterations)
    
    save_layout_as_png(cave_grid, "cellular_automata_layout" + "_" + str(init_wall_chance) + "_" + str(iterations) +  ".png", scale=8)
    
    
    #init_wall_chance (0.40 - 0.48): The starting density.
        #Lowering this below 0.40 results in massive wide-open arenas.
        #Raising it above 0.48 can choke the map, leaving small, isolated pockets of floor entirely trapped by walls.
    #iterations (3 - 6): How many times the rules are applied.
        #3 iterations leaves jagged, rough edges.
        #5 or 6 smooths the edges out into clean, flowing cavern walls.
        #Going beyond 7 usually stagnates the map into predictable geometric globs.
    