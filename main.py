from mcpylib import MCPyLib
from PIL import Image
import sys
import os
import numpy as np
from sklearn.cluster import KMeans


class MinecraftImageDrawer:
    """Draw images in Minecraft using modern map art algorithms"""

    # OFFICIAL Minecraft Map Colors ONLY (61 colors total)
    # Based on the exact Minecraft map color table - NO duplicates
    COLOR_MAP = {
        (127, 178, 56): "grass_block",           # ID 1 - GRASS
        (247, 233, 163): "sandstone",            # ID 2 - SAND
        (199, 199, 199): "white_wool",           # ID 3 - WOOL
        (255, 0, 0): "red_concrete",             # ID 4 - FIRE
        (160, 160, 255): "packed_ice",           # ID 5 - ICE
        (167, 167, 167): "iron_block",           # ID 6 - METAL
        (0, 124, 0): "oak_leaves",               # ID 7 - PLANT
        (255, 255, 255): "white_concrete",       # ID 8 - SNOW
        (164, 168, 184): "clay",                 # ID 9 - CLAY
        (151, 109, 77): "dirt",                  # ID 10 - DIRT
        (112, 112, 112): "stone",                # ID 11 - STONE
        (64, 64, 255): "blue_concrete",          # ID 12 - WATER
        (143, 119, 72): "oak_planks",            # ID 13 - WOOD
        (255, 252, 245): "quartz_block",         # ID 14 - QUARTZ
        (216, 127, 51): "orange_concrete",       # ID 15 - ORANGE
        (178, 76, 216): "magenta_concrete",      # ID 16 - MAGENTA
        (102, 153, 216): "light_blue_concrete",  # ID 17 - LIGHT_BLUE
        (229, 229, 51): "yellow_concrete",       # ID 18 - YELLOW
        (127, 204, 25): "lime_concrete",         # ID 19 - LIME
        (242, 127, 165): "pink_concrete",        # ID 20 - PINK
        (76, 76, 76): "gray_concrete",           # ID 21 - GRAY
        (153, 153, 153): "light_gray_concrete",  # ID 22 - LIGHT_GRAY
        (76, 127, 153): "cyan_concrete",         # ID 23 - CYAN
        (127, 63, 178): "purple_concrete",       # ID 24 - PURPLE
        (51, 76, 178): "blue_concrete",          # ID 25 - BLUE
        (102, 76, 51): "brown_concrete",         # ID 26 - BROWN
        (102, 127, 51): "green_concrete",        # ID 27 - GREEN
        (153, 51, 51): "red_concrete",           # ID 28 - RED
        (25, 25, 25): "black_concrete",          # ID 29 - BLACK
        (250, 238, 77): "gold_block",            # ID 30 - GOLD
        (92, 219, 213): "diamond_block",         # ID 31 - DIAMOND
        (74, 128, 255): "lapis_block",           # ID 32 - LAPIS
        (0, 217, 58): "emerald_block",           # ID 33 - EMERALD
        (129, 86, 49): "podzol",                 # ID 34 - PODZOL
        (112, 2, 0): "netherrack",               # ID 35 - NETHER
        (209, 177, 161): "white_terracotta",     # ID 36 - TERRACOTTA_WHITE
        (159, 82, 36): "orange_terracotta",      # ID 37 - TERRACOTTA_ORANGE
        (149, 87, 108): "magenta_terracotta",    # ID 38 - TERRACOTTA_MAGENTA
        # ID 39 - TERRACOTTA_LIGHT_BLUE
        (112, 108, 138): "light_blue_terracotta",
        (186, 133, 36): "yellow_terracotta",     # ID 40 - TERRACOTTA_YELLOW
        (103, 117, 53): "lime_terracotta",       # ID 41 - TERRACOTTA_LIME
        (160, 77, 78): "pink_terracotta",        # ID 42 - TERRACOTTA_PINK
        (57, 41, 35): "gray_terracotta",         # ID 43 - TERRACOTTA_GRAY
        # ID 44 - TERRACOTTA_LIGHT_GRAY
        (135, 107, 98): "light_gray_terracotta",
        (87, 92, 92): "cyan_terracotta",         # ID 45 - TERRACOTTA_CYAN
        (122, 73, 88): "purple_terracotta",      # ID 46 - TERRACOTTA_PURPLE
        (76, 62, 92): "blue_terracotta",         # ID 47 - TERRACOTTA_BLUE
        (76, 50, 35): "brown_terracotta",        # ID 48 - TERRACOTTA_BROWN
        (76, 82, 42): "green_terracotta",        # ID 49 - TERRACOTTA_GREEN
        (142, 60, 46): "red_terracotta",         # ID 50 - TERRACOTTA_RED
        (37, 22, 16): "black_terracotta",        # ID 51 - TERRACOTTA_BLACK
        (189, 48, 49): "crimson_nylium",         # ID 52 - CRIMSON_NYLIUM
        (148, 63, 97): "crimson_planks",         # ID 53 - CRIMSON_STEM
        (92, 25, 29): "crimson_hyphae",          # ID 54 - CRIMSON_HYPHAE
        (22, 126, 134): "warped_nylium",         # ID 55 - WARPED_NYLIUM
        (58, 142, 140): "warped_planks",         # ID 56 - WARPED_STEM
        (86, 44, 62): "warped_hyphae",           # ID 57 - WARPED_HYPHAE
        (20, 180, 133): "warped_wart_block",     # ID 58 - WARPED_WART_BLOCK
        (100, 100, 100): "deepslate",            # ID 59 - DEEPSLATE
        (216, 175, 147): "raw_iron_block",       # ID 60 - RAW_IRON
        (127, 167, 150): "glow_lichen",          # ID 61 - GLOW_LICHEN
    }

    def __init__(self, ip="127.0.0.1", port=65535, token="", timeout=10.0):
        """Initialize the Minecraft connection"""
        try:
            self.mc = MCPyLib(ip=ip, port=port, token=token, timeout=timeout)
            print(f"Connected to Minecraft server at {ip}:{port}")
        except Exception as e:
            print(f"Failed to connect to Minecraft server: {e}")
            sys.exit(1)

    def get_closest_block(self, rgb):
        """Find closest Minecraft block using simple Euclidean distance"""
        # Ensure RGB values are in valid range [0, 255] to prevent overflow
        r = int(np.clip(rgb[0], 0, 255))
        g = int(np.clip(rgb[1], 0, 255))
        b = int(np.clip(rgb[2], 0, 255))

        min_distance = float('inf')
        closest_block = "white_concrete"
        closest_color = (255, 255, 255)

        for color, block in self.COLOR_MAP.items():
            cr, cg, cb = color
            # Calculate squared distance (no need for sqrt, just comparing)
            dr = r - cr
            dg = g - cg
            db = b - cb
            distance = dr * dr + dg * dg + db * db

            if distance < min_distance:
                min_distance = distance
                closest_block = block
                closest_color = color

        return closest_block, closest_color

    def calculate_brightness(self, rgb):
        """Calculate perceived brightness of an RGB color

        Uses luminance formula: 0.299*R + 0.587*G + 0.114*B
        Returns value between 0.0 and 1.0
        """
        r, g, b = rgb[0], rgb[1], rgb[2]
        brightness = (0.299 * r + 0.587 * g + 0.114 * b) / 255.0
        return brightness

    def get_map_tone(self, brightness):
        """Determine map tone based on brightness for staircase algorithm

        Minecraft maps have 4 tones per color, controlled by height differences:
        - dark: block is 1 level LOWER than previous
        - normal: block is at SAME level as previous
        - light: block is 1 level HIGHER than previous

        Args:
            brightness: Float between 0.0 and 1.0

        Returns:
            String: "dark", "normal", or "light"
        """
        if brightness < 0.33:
            return "dark"
        elif brightness < 0.67:
            return "normal"
        else:
            return "light"

    def get_height_change(self, brightness, tone):
        """Calculate height change with aggressive reset strategy

        Uses brightness to determine height change.
        Returns special value -999 to indicate reset to Y=-60.

        Args:
            brightness: Float between 0.0 and 1.0
            tone: "dark", "normal", or "light"

        Returns:
            Integer: height change amount, or -999 to reset to Y=-60
        """
        if tone == "light":
            return 1  # Ascend 1 level
        elif tone == "normal":
            return 0  # Stay same
        else:  # dark
            # Aggressive reset to Y=-60 for darker colors
            # More frequent triggers for better height control
            if brightness < 0.25:  # 25% threshold - more frequent
                return -999  # Special value: reset to Y=-60
            else:
                return -1  # Normal descent 1 level

    def quantize_with_kmeans(self, img_array, num_colors=35):
        """Modern Minecraft map art algorithm: k-means color quantization

        How professional Minecraft map artists work:
        1. Find the N most important colors in the image using k-means
        2. Map those to closest Minecraft blocks
        3. Replace all pixels with their cluster's Minecraft color
        4. NO dithering - clean coherent regions

        Args:
            img_array: Image as numpy array
            num_colors: Number of colors to use (fewer = cleaner, more = detailed)

        Returns:
            Quantized image array
        """
        print(f"\n=== K-Means Color Quantization (Modern Map Art Algorithm) ===")
        print(f"Reducing to {num_colors} most important colors...\n")

        height, width = img_array.shape[:2]
        pixels = img_array.reshape(-1, 3).astype(np.float32)

        # Step 1: K-means to find dominant colors
        print("[1/3] Finding dominant colors in image...")
        kmeans = KMeans(n_clusters=num_colors, random_state=42,
                        n_init=10, max_iter=300)
        labels = kmeans.fit_predict(pixels)

        # Step 2: Map each cluster to closest Minecraft color
        print("[2/3] Mapping to Minecraft palette...")
        minecraft_colors = []
        minecraft_blocks = []

        for i, center in enumerate(kmeans.cluster_centers_):
            rgb = tuple(np.clip(center.astype(int), 0, 255))
            block, mc_color = self.get_closest_block(rgb)
            minecraft_colors.append(mc_color)
            minecraft_blocks.append(block)

        # Step 3: Replace pixels
        print("[3/3] Applying quantization...")
        output = np.array([minecraft_colors[label] for label in labels])
        output = output.reshape(height, width, 3).astype(np.uint8)

        # Print statistics
        unique, counts = np.unique(labels, return_counts=True)
        print(f"\n=== Color Usage (Top 15) ===")
        for idx in sorted(unique, key=lambda x: counts[x], reverse=True)[:15]:
            block = minecraft_blocks[idx]
            color = minecraft_colors[idx]
            percentage = (counts[idx] / len(labels)) * 100
            print(f"  {block:28s}  RGB{color}  {percentage:5.1f}%")

        return output

    def clear_area(self, start_x, start_z, width, height, border=16, max_blocks_per_chunk=100000):
        """Clear the build area from Y=-60 to Y=319 with border, in chunks

        Due to server limitations, clears in chunks of max 100,000 blocks at a time.

        Args:
            start_x, start_z: Starting X and Z coordinates
            width: Width of the image area
            height: Height (depth) of the image area
            border: Additional border to clear (default 16 blocks)
            max_blocks_per_chunk: Maximum blocks to clear per operation (default 100,000)
        """
        print(f"\n=== Clearing Build Area ===")
        print(f"Main area: {width}x{height} blocks")
        print(f"Border: {border} blocks on each side")
        print(f"Y range: -60 to 319 (380 blocks height)")

        # Calculate extended area with border
        clear_x = start_x - border
        clear_y_min = -60
        clear_y_max = 319
        clear_z = start_z - border
        clear_width = width + 2 * border
        clear_height = height + 2 * border
        total_y_range = 380  # Y range: -60 to 319

        total_blocks = clear_width * total_y_range * clear_height
        print(f"Clearing from ({clear_x}, {clear_y_min}, {clear_z})")
        print(f"Size: {clear_width}x{total_y_range}x{clear_height} blocks")
        print(f"Total blocks to clear: {total_blocks:,}")

        try:
            # Calculate chunk size
            xz_area = clear_width * clear_height

            # Check if we need to split horizontally (XZ) as well
            if xz_area > max_blocks_per_chunk:
                # Even one Y level is too large, need to split XZ area
                print(f"XZ area ({xz_area:,} blocks) exceeds chunk limit!")
                print(f"Splitting horizontally into smaller regions...\n")

                # Calculate how many Z slices we need
                z_per_chunk = max(1, max_blocks_per_chunk // clear_width)
                num_z_chunks = (clear_height + z_per_chunk - 1) // z_per_chunk

                total_cleared = 0
                chunk_count = 0

                for y_start in range(clear_y_min, clear_y_max + 1):
                    for z_chunk_idx in range(num_z_chunks):
                        z_start = z_chunk_idx * z_per_chunk
                        z_count = min(z_per_chunk, clear_height - z_start)

                        blocks_this_chunk = clear_width * 1 * z_count
                        chunk_count += 1

                        if chunk_count % 100 == 1:  # Show progress every 100 chunks
                            print(f"Chunk {chunk_count}: Y={y_start}, Z={z_start} to {z_start + z_count - 1} ({blocks_this_chunk:,} blocks)")

                        # Create air blocks for this slice
                        air_blocks = []
                        for x in range(clear_width):
                            x_layer = [["air" for _ in range(z_count)]]
                            air_blocks.append(x_layer)

                        # Clear this chunk
                        count = self.mc.edit(clear_x, y_start, clear_z + z_start, air_blocks)
                        total_cleared += count

                print(f"\nTotal chunks: {chunk_count}")
                print(f"Total cleared: {total_cleared:,} blocks successfully!\n")
            else:
                # XZ area fits in chunk limit, split by Y levels
                y_levels_per_chunk = max(1, max_blocks_per_chunk // xz_area)
                num_chunks = (total_y_range + y_levels_per_chunk - 1) // y_levels_per_chunk

                print(f"Splitting into {num_chunks} chunks ({y_levels_per_chunk} Y-levels per chunk)")
                print(f"Max {max_blocks_per_chunk:,} blocks per chunk\n")

                total_cleared = 0
                current_y = clear_y_min

                for chunk_idx in range(num_chunks):
                    # Calculate Y range for this chunk
                    y_start = current_y
                    y_levels_this_chunk = min(y_levels_per_chunk, clear_y_max - current_y + 1)
                    y_end = y_start + y_levels_this_chunk - 1

                    blocks_this_chunk = clear_width * y_levels_this_chunk * clear_height

                    print(f"Chunk {chunk_idx + 1}/{num_chunks}: Y={y_start} to Y={y_end} ({blocks_this_chunk:,} blocks)")

                    # Create air blocks structure for this chunk
                    air_blocks = []
                    for x in range(clear_width):
                        x_layer = []
                        for y in range(y_levels_this_chunk):
                            z_layer = ["air"] * clear_height
                            x_layer.append(z_layer)
                        air_blocks.append(x_layer)

                    # Clear this chunk
                    count = self.mc.edit(clear_x, y_start, clear_z, air_blocks)
                    total_cleared += count
                    print(f"  Cleared {count:,} blocks")

                    current_y += y_levels_this_chunk

                print(f"\nTotal cleared: {total_cleared:,} blocks successfully!\n")
        except Exception as e:
            print(f"Error clearing area: {e}\n")

    def load_and_resize_image(self, image_path, max_size):
        """Load and resize image"""
        if not os.path.exists(image_path):
            print(f"Error: Image not found: {image_path}")
            sys.exit(1)

        try:
            img = Image.open(image_path)
            print(f"Loaded: {img.size[0]}x{img.size[1]} pixels")

            if img.mode != 'RGB':
                img = img.convert('RGB')

            img.thumbnail((max_size, max_size), Image.Resampling.LANCZOS)
            print(f"Resized: {img.size[0]}x{img.size[1]} pixels")

            return img
        except Exception as e:
            print(f"Error loading image: {e}")
            sys.exit(1)

    def draw_horizontal(self, image_path, size, start_x, start_y, start_z, num_colors=35, max_blocks_per_chunk=100000):
        """Draw horizontally with k-means quantization (flat 2D version)

        This method creates a flat 2D map art at a single Y level.
        - X axis: image width
        - Y axis: single level (flat)
        - Z axis: image height (depth)

        Places blocks in chunks of max 100,000 blocks to avoid server overload.
        """
        print(f"\n{'='*60}")
        print(f"Drawing FLAT HORIZONTAL MAP ART")
        print(f"Position: ({start_x}, {start_y}, {start_z})")
        print(f"{'='*60}")

        img = self.load_and_resize_image(image_path, size)
        width, height = img.size

        # Apply k-means quantization
        img_array = np.array(img)
        img_array = self.quantize_with_kmeans(img_array, num_colors=num_colors)

        # Convert to blocks (flat 2D)
        print(f"\nConverting to Minecraft blocks (flat)...")
        blocks = []
        for x in range(width):
            x_layer = []
            for y in range(1):  # Only one Y level
                z_layer = []
                for z in range(height):
                    pixel = tuple(img_array[z, x])
                    block, _ = self.get_closest_block(pixel)
                    z_layer.append(block)
                x_layer.append(z_layer)
            blocks.append(x_layer)

        # Place blocks in chunks
        try:
            total_blocks = width * height
            print(f"\nPlacing {width}x{height} blocks in Minecraft...")
            print(f"Splitting placement into chunks of max {max_blocks_per_chunk:,} blocks...\n")

            # Calculate how many X columns fit in one chunk
            x_per_chunk = max(1, max_blocks_per_chunk // height)
            num_chunks = (width + x_per_chunk - 1) // x_per_chunk

            print(f"Columns per chunk: {x_per_chunk}")
            print(f"Total chunks: {num_chunks}\n")

            total_placed = 0
            for chunk_idx in range(num_chunks):
                x_start = chunk_idx * x_per_chunk
                x_count = min(x_per_chunk, width - x_start)
                x_end = x_start + x_count - 1

                # Extract chunk
                chunk_blocks = blocks[x_start:x_start + x_count]
                blocks_in_chunk = x_count * height

                print(f"Chunk {chunk_idx + 1}/{num_chunks}: X={start_x + x_start} to {start_x + x_end} ({blocks_in_chunk:,} blocks)")

                # Place chunk
                count = self.mc.edit(start_x + x_start, start_y, start_z, chunk_blocks)
                total_placed += count
                print(f"  Placed {count:,} blocks")

            print(f"\n{'='*60}")
            print(f"SUCCESS! Placed {total_placed:,} blocks total")
            print(f"Location: ({start_x}, {start_y}, {start_z}) to ({start_x + width}, {start_y}, {start_z + height})")
            print(f"{'='*60}")
        except Exception as e:
            print(f"Error: {e}")

    def draw_horizontal_3d(self, image_path, size, start_x, start_z, num_colors=35, max_blocks_per_chunk=100000, staircase_mode="classic"):
        """Draw horizontally with staircase algorithm for Minecraft map art (3D version)

        This method creates 3D map art using the staircase algorithm:
        - Each pixel's height is relative to the previous pixel
        - Height changes based on brightness tone (dark/normal/light)
        - Creates natural staircase patterns

        Args:
            staircase_mode: "classic" (common base at Y=0) or "valley" (pull valleys down)
        """
        print(f"\n{'='*60}")
        print(f"Drawing 3D STAIRCASE MAP ART")
        print(f"Staircase mode: {staircase_mode}")
        print(f"Position: ({start_x}, variable Y, {start_z})")
        print(f"{'='*60}")

        img = self.load_and_resize_image(image_path, size)
        width, height = img.size

        # Clear the area first (including 16-block border)
        self.clear_area(start_x, start_z, width, height, border=16)

        # Apply k-means quantization
        img_array = np.array(img)
        img_array = self.quantize_with_kmeans(img_array, num_colors=num_colors)

        # Build physical structure using staircase algorithm
        print(f"\nBuilding staircase structure...")
        print(f"Using absolute brightness for tone calculation")

        # Store physical blocks for each column
        physical_columns = []
        tone_stats = {"dark": 0, "normal": 0, "light": 0}
        reset_count = 0  # Track how many times we reset to Y=-60

        # Minecraft world limits
        world_min_y = -60
        world_max_y = 319
        world_height_limit = world_max_y - world_min_y + 1  # 380 levels

        for x in range(width):
            if x % 50 == 0:
                print(f"  Progress: {x}/{width} columns...")

            column_blocks = []
            current_height = world_min_y  # Start at Y=-60 directly

            for z in range(height):
                pixel = tuple(img_array[z, x])
                block, _ = self.get_closest_block(pixel)

                # Determine tone based on absolute brightness
                brightness = self.calculate_brightness(pixel)
                tone = self.get_map_tone(brightness)

                # Get height change with aggressive reset strategy
                height_change = self.get_height_change(brightness, tone)

                # Check for reset signal
                if height_change == -999:
                    # Reset to bottom for dark colors
                    current_height = world_min_y
                    if x == 0:  # Count resets once
                        reset_count += 1
                else:
                    # Normal height change
                    current_height += height_change

                    # Apply wraparound if needed (during building, not after)
                    if current_height > world_max_y:
                        current_height = world_min_y + (current_height - world_max_y - 1)
                    elif current_height < world_min_y:
                        current_height = world_max_y + (current_height - world_min_y + 1)

                # Store block with its position
                column_blocks.append({
                    'x': x,
                    'y': current_height,
                    'z': z,
                    'block': block,
                    'tone': tone,
                    'brightness': brightness
                })

                if x == 0:  # Count statistics once
                    tone_stats[tone] += 1

            physical_columns.append(column_blocks)

        # Print tone statistics
        total_pixels = width * height
        print(f"\n=== Tone Distribution ===")
        print(f"  Dark:   {tone_stats['dark']:6d} pixels ({tone_stats['dark']/total_pixels*100:5.1f}%)")
        print(f"  Normal: {tone_stats['normal']:6d} pixels ({tone_stats['normal']/total_pixels*100:5.1f}%)")
        print(f"  Light:  {tone_stats['light']:6d} pixels ({tone_stats['light']/total_pixels*100:5.1f}%)")

        print(f"\n=== Height Control ===")
        print(f"  Resets to Y=-60: {reset_count} times ({reset_count/total_pixels*100:5.1f}%)")
        print(f"  This helps control maximum height and creates depth")

        # Find overall min/max Y (already adjusted per column)
        all_y_values = [block['y'] for column in physical_columns for block in column]
        min_y = min(all_y_values)
        max_y = max(all_y_values)
        y_range = max_y - min_y + 1

        print(f"\n  Final Y range: {min_y} to {max_y} ({y_range} levels)")
        print(f"  Each column individually adjusted to fit within world limits")

        # Convert to blocks array format
        print(f"\nConverting to block array...")
        blocks = []
        for x in range(width):
            x_layer = []
            for y_level in range(y_range):
                z_layer = ["air"] * height
                x_layer.append(z_layer)

            # Fill in actual blocks
            for block_info in physical_columns[x]:
                y_index = block_info['y'] - min_y
                z_index = block_info['z']
                x_layer[y_index][z_index] = block_info['block']

            blocks.append(x_layer)

        # Place blocks in chunks
        try:
            print(f"\nPlacing {width}x{y_range}x{height} blocks in Minecraft...")
            print(f"Splitting placement into chunks of max {max_blocks_per_chunk:,} blocks...\n")

            blocks_per_column = y_range * height
            x_per_chunk = max(1, max_blocks_per_chunk // blocks_per_column)
            num_chunks = (width + x_per_chunk - 1) // x_per_chunk

            print(f"Columns per chunk: {x_per_chunk}")
            print(f"Total chunks: {num_chunks}\n")

            total_placed = 0
            for chunk_idx in range(num_chunks):
                x_start = chunk_idx * x_per_chunk
                x_count = min(x_per_chunk, width - x_start)
                x_end = x_start + x_count - 1

                chunk_blocks = blocks[x_start:x_start + x_count]
                blocks_in_chunk = x_count * y_range * height

                print(f"Chunk {chunk_idx + 1}/{num_chunks}: X={start_x + x_start} to {start_x + x_end} ({blocks_in_chunk:,} blocks)")

                count = self.mc.edit(start_x + x_start, min_y, start_z, chunk_blocks)
                total_placed += count
                print(f"  Placed {count:,} blocks")

            print(f"\n{'='*60}")
            print(f"SUCCESS! Placed {total_placed:,} blocks total")
            print(f"Location: ({start_x}, {min_y}, {start_z}) to ({start_x + width}, {max_y}, {start_z + height})")
            print(f"{'='*60}")
        except Exception as e:
            print(f"Error: {e}")

    def draw_vertical(self, image_path, size, start_x, start_y, start_z, num_colors=35):
        """Draw vertically with k-means quantization"""
        print(f"\n{'='*60}")
        print(f"Drawing VERTICAL at ({start_x}, {start_y}, {start_z})")
        print(f"{'='*60}")

        img = self.load_and_resize_image(image_path, size)
        width, height = img.size

        # Apply k-means quantization
        img_array = np.array(img)
        img_array = self.quantize_with_kmeans(img_array, num_colors=num_colors)

        # Convert to blocks
        print(f"\nConverting to Minecraft blocks...")
        blocks = []
        for x in range(width):
            x_layer = []
            for y in range(height):
                pixel = tuple(img_array[height - 1 - y, x])
                block, _ = self.get_closest_block(pixel)
                x_layer.append([block])
            blocks.append(x_layer)

        # Place blocks
        try:
            print(f"\nPlacing {width}x{height} blocks in Minecraft...")
            count = self.mc.edit(start_x, start_y, start_z, blocks)
            print(f"\n{'='*60}")
            print(f"SUCCESS! Placed {count} blocks")
            print(
                f"Location: ({start_x}, {start_y}, {start_z}) to ({start_x + width}, {start_y + height}, {start_z})")
            print(f"{'='*60}")
        except Exception as e:
            print(f"Error: {e}")


def main():
    print("=" * 60)
    print("Minecraft Image Drawer - Modern Map Art Algorithm")
    print("=" * 60)

    # Connection
    print("\nServer Connection:")
    ip = "127.0.0.1"
    port = 65535
    token = '6CLlRIvEvzzKJMFuT7__k8DqaKm4j4LynduhYH6DJu0'

    drawer = MinecraftImageDrawer(ip=ip, port=port, token=token)

    # Image settings
    image_path = "test.jpg"
    size = 512
    num_colors = 61

    # Orientation
    print("\nOrientation options:")
    print("  h  - Horizontal flat (2D)")
    print("  hh - Horizontal 3D (full height range Y=-60 to 319)")
    print("  v  - Vertical")
    orientation = input("\nChoose orientation (default: h): ").strip().lower() or "h"

    # Coordinates
    start_x, start_y, start_z = drawer.mc.getPos("TLSChannel")

    # Draw
    if orientation == 'v':
        drawer.draw_vertical(image_path, size, start_x,
                             start_y, start_z, num_colors=num_colors)
    elif orientation == 'hh':
        # 3D horizontal mode uses full Y range (-60 to 319)
        print("\nUsing 3D mode with full height range!")
        drawer.draw_horizontal_3d(image_path, size, start_x,
                                  start_z, num_colors=num_colors)
    else:
        # Flat horizontal mode
        print("\nUsing flat 2D mode!")
        drawer.draw_horizontal(image_path, size, start_x,
                               start_y, start_z, num_colors=num_colors)

    print("\nDone! Check your Minecraft world.")


if __name__ == "__main__":
    main()
