import json
import numpy as np
from PIL import Image

def generate_layout_from_json(json_filename="dungeon_data.txt", output_filename="dungeon_layout_control.png", width=120, height=120, scale=6):
    """
    Reads the topological/geometric room and path data from a JSON txt file
    and reconstructs the layout map into a high-contrast PNG.
    """
    # 1. Read and parse the JSON file
    try:
        with open(json_filename, "r") as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"Error: The file '{json_filename}' was not found. Please ensure it is in the same directory.")
        return
    except json.JSONDecodeError:
        print(f"Error: Could not parse '{json_filename}'. Ensure it is valid JSON.")
        return

    # 2. Initialize a blank grid of solid walls (1 = Wall/Black)
    grid = np.ones((height, width), dtype=np.uint8)

    # Dictionary to quickly look up room properties by their ID when carving paths
    rooms_by_id = {}

    # 3. Carve out all the rooms (0 = Floor/White)
    for room in data.get("rooms", []):
        room_id = room["id"]
        rx = room["position"]["x"]
        ry = room["position"]["y"]
        rw = room["size"]["width"]
        rh = room["size"]["height"]
        
        rooms_by_id[room_id] = room
        
        # Carve the rectangle into the grid array safely bounded within map limits
        grid[max(0, ry):min(height, ry+rh), max(0, rx):min(width, rx+rw)] = 0

    # 4. Carve out all the paths (corridors)
    for path in data.get("paths", []):
        room_a_id, room_b_id = path["connects"]
        
        # Pull the exact centers of the connected rooms
        cx1 = rooms_by_id[room_a_id]["center"]["x"]
        cy1 = rooms_by_id[room_a_id]["center"]["y"]
        cx2 = rooms_by_id[room_b_id]["center"]["x"]
        cy2 = rooms_by_id[room_b_id]["center"]["y"]

        # Carve standard architectural L-shaped corridors connecting the centers
        # We can reconstruct it consistently or give it a predictable logic. 
        # Here we'll draw Horizontal then Vertical segments.
        start_x, end_x = min(cx1, cx2), max(cx1, cx2)
        start_y, end_y = min(cy1, cy2), max(cy1, cy2)
        
        # Horizontal segment at cy1 from cx1 to cx2
        grid[cy1, start_x:end_x + 1] = 0
        # Vertical segment at cx2 from cy1 to cy2
        grid[start_y:end_y + 1, cx2] = 0

    # 5. Convert binary matrix and save as pixel-perfect PNG
    # Map 0 (floors) to 255 (white) and 1 (walls) to 0 (black)
    img_data = np.where(grid == 0, 255, 0).astype(np.uint8)
    img = Image.fromarray(img_data, mode='L')
    
    # Scale up using NEAREST resample to maintain sharp pixel-art edges
    new_size = (img.width * scale, img.height * scale)
    img = img.resize(new_size, resample=Image.Resampling.NEAREST)
    
    img.save(output_filename)
    print(f"Success: Reconstructed layout saved to '{output_filename}' ({new_size[0]}x{new_size[1]} px)")

if __name__ == "__main__":
    # Parameters matching the original generator configuration
    generate_layout_from_json(
        json_filename="dungeon_data.txt", 
        output_filename="dungeon_layout_control.png",
        width=80, 
        height=80, 
        scale=6
    )