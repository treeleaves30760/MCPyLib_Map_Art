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

    def draw_horizontal(self, image_path, size, start_x, start_y, start_z, num_colors=35):
        """Draw horizontally with k-means quantization"""
        print(f"\n{'='*60}")
        print(f"Drawing HORIZONTAL at ({start_x}, {start_y}, {start_z})")
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
            for y in range(1):
                z_layer = []
                for z in range(height):
                    pixel = tuple(img_array[z, x])
                    block, _ = self.get_closest_block(pixel)
                    z_layer.append(block)
                x_layer.append(z_layer)
            blocks.append(x_layer)

        # Place blocks
        try:
            print(f"\nPlacing {width}x{height} blocks in Minecraft...")
            count = self.mc.edit(start_x, start_y, start_z, blocks)
            print(f"\n{'='*60}")
            print(f"SUCCESS! Placed {count} blocks")
            print(
                f"Location: ({start_x}, {start_y}, {start_z}) to ({start_x + width}, {start_y}, {start_z + height})")
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
    orientation = input(
        "\nDraw horizontal (h) or vertical (v)? (default: h): ").strip().lower() or "h"

    # Coordinates
    start_x, start_y, start_z = drawer.mc.getPos("TLSChannel")

    # Draw
    if orientation == 'v':
        drawer.draw_vertical(image_path, size, start_x,
                             start_y, start_z, num_colors=num_colors)
    else:
        drawer.draw_horizontal(image_path, size, start_x,
                               start_y, start_z, num_colors=num_colors)

    print("\nDone! Check your Minecraft world.")


if __name__ == "__main__":
    main()
