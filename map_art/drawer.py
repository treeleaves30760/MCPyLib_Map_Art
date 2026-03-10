import sys

import numpy as np
from mcpylib import MCPyLib

from map_art.colors import get_closest_block, calculate_brightness, get_map_tone, get_height_change
from map_art.image import load_and_resize, quantize_with_kmeans


class MinecraftImageDrawer:
    """Draw images in Minecraft using modern map art algorithms"""

    def __init__(self, ip="127.0.0.1", port=65535, token="", timeout=10.0):
        """Initialize the Minecraft connection"""
        try:
            self.mc = MCPyLib(ip=ip, port=port, token=token, timeout=timeout)
            print(f"Connected to Minecraft server at {ip}:{port}")
        except Exception as e:
            print(f"Failed to connect to Minecraft server: {e}")
            sys.exit(1)

    def clear_area(self, start_x, start_z, width, height, border=16, max_blocks_per_chunk=100000):
        """Clear the build area from Y=-60 to Y=319 with border, in chunks"""
        print(f"\n=== Clearing Build Area ===")
        print(f"Main area: {width}x{height} blocks")
        print(f"Border: {border} blocks on each side")
        print(f"Y range: -60 to 319 (380 blocks height)")

        clear_x = start_x - border
        clear_y_min = -60
        clear_y_max = 319
        clear_z = start_z - border
        clear_width = width + 2 * border
        clear_height = height + 2 * border
        total_y_range = 380

        total_blocks = clear_width * total_y_range * clear_height
        print(f"Clearing from ({clear_x}, {clear_y_min}, {clear_z})")
        print(f"Size: {clear_width}x{total_y_range}x{clear_height} blocks")
        print(f"Total blocks to clear: {total_blocks:,}")

        try:
            xz_area = clear_width * clear_height

            if xz_area > max_blocks_per_chunk:
                print(f"XZ area ({xz_area:,} blocks) exceeds chunk limit!")
                print(f"Splitting horizontally into smaller regions...\n")

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

                        if chunk_count % 100 == 1:
                            print(
                                f"Chunk {chunk_count}: Y={y_start}, Z={z_start} to {z_start + z_count - 1} ({blocks_this_chunk:,} blocks)")

                        air_blocks = []
                        for x in range(clear_width):
                            x_layer = [["air" for _ in range(z_count)]]
                            air_blocks.append(x_layer)

                        count = self.mc.edit(
                            clear_x, y_start, clear_z + z_start, air_blocks)
                        total_cleared += count

                print(f"\nTotal chunks: {chunk_count}")
                print(f"Total cleared: {total_cleared:,} blocks successfully!\n")
            else:
                y_levels_per_chunk = max(1, max_blocks_per_chunk // xz_area)
                num_chunks = (total_y_range + y_levels_per_chunk - 1) // y_levels_per_chunk

                print(f"Splitting into {num_chunks} chunks ({y_levels_per_chunk} Y-levels per chunk)")
                print(f"Max {max_blocks_per_chunk:,} blocks per chunk\n")

                total_cleared = 0
                current_y = clear_y_min

                for chunk_idx in range(num_chunks):
                    y_start = current_y
                    y_levels_this_chunk = min(
                        y_levels_per_chunk, clear_y_max - current_y + 1)
                    y_end = y_start + y_levels_this_chunk - 1

                    blocks_this_chunk = clear_width * y_levels_this_chunk * clear_height

                    print(
                        f"Chunk {chunk_idx + 1}/{num_chunks}: Y={y_start} to Y={y_end} ({blocks_this_chunk:,} blocks)")

                    air_blocks = []
                    for x in range(clear_width):
                        x_layer = []
                        for y in range(y_levels_this_chunk):
                            z_layer = ["air"] * clear_height
                            x_layer.append(z_layer)
                        air_blocks.append(x_layer)

                    count = self.mc.edit(clear_x, y_start, clear_z, air_blocks)
                    total_cleared += count
                    print(f"  Cleared {count:,} blocks")

                    current_y += y_levels_this_chunk

                print(f"\nTotal cleared: {total_cleared:,} blocks successfully!\n")
        except Exception as e:
            print(f"Error clearing area: {e}\n")

    def draw_horizontal(self, image_path, size, start_x, start_y, start_z, num_colors=35, max_blocks_per_chunk=100000):
        """Draw horizontally with k-means quantization (flat 2D version)"""
        print(f"\n{'='*60}")
        print(f"Drawing FLAT HORIZONTAL MAP ART")
        print(f"Position: ({start_x}, {start_y}, {start_z})")
        print(f"{'='*60}")

        img = load_and_resize(image_path, size)
        width, height = img.size

        img_array = np.array(img)
        img_array = quantize_with_kmeans(img_array, num_colors=num_colors)

        print(f"\nConverting to Minecraft blocks (flat)...")
        blocks = []
        for x in range(width):
            x_layer = []
            for y in range(1):
                z_layer = []
                for z in range(height):
                    pixel = tuple(img_array[z, x])
                    block, _ = get_closest_block(pixel)
                    z_layer.append(block)
                x_layer.append(z_layer)
            blocks.append(x_layer)

        try:
            total_blocks = width * height
            print(f"\nPlacing {width}x{height} blocks in Minecraft...")
            print(f"Splitting placement into chunks of max {max_blocks_per_chunk:,} blocks...\n")

            x_per_chunk = max(1, max_blocks_per_chunk // height)
            num_chunks = (width + x_per_chunk - 1) // x_per_chunk

            print(f"Columns per chunk: {x_per_chunk}")
            print(f"Total chunks: {num_chunks}\n")

            total_placed = 0
            for chunk_idx in range(num_chunks):
                x_start = chunk_idx * x_per_chunk
                x_count = min(x_per_chunk, width - x_start)
                x_end = x_start + x_count - 1

                chunk_blocks = blocks[x_start:x_start + x_count]
                blocks_in_chunk = x_count * height

                print(
                    f"Chunk {chunk_idx + 1}/{num_chunks}: X={start_x + x_start} to {start_x + x_end} ({blocks_in_chunk:,} blocks)")

                count = self.mc.edit(
                    start_x + x_start, start_y, start_z, chunk_blocks)
                total_placed += count
                print(f"  Placed {count:,} blocks")

            print(f"\n{'='*60}")
            print(f"SUCCESS! Placed {total_placed:,} blocks total")
            print(
                f"Location: ({start_x}, {start_y}, {start_z}) to ({start_x + width}, {start_y}, {start_z + height})")
            print(f"{'='*60}")
        except Exception as e:
            print(f"Error: {e}")

    def draw_horizontal_3d(self, image_path, size, start_x, start_z, num_colors=35, max_blocks_per_chunk=100000, staircase_mode="classic"):
        """Draw horizontally with staircase algorithm for Minecraft map art (3D version)"""
        print(f"\n{'='*60}")
        print(f"Drawing 3D STAIRCASE MAP ART")
        print(f"Staircase mode: {staircase_mode}")
        print(f"Position: ({start_x}, variable Y, {start_z})")
        print(f"{'='*60}")

        img = load_and_resize(image_path, size)
        width, height = img.size

        self.clear_area(start_x, start_z, width, height, border=16)

        img_array = np.array(img)
        img_array = quantize_with_kmeans(img_array, num_colors=num_colors)

        print(f"\nBuilding staircase structure...")
        print(f"Using absolute brightness for tone calculation")

        physical_columns = []
        tone_stats = {"dark": 0, "normal": 0, "light": 0}
        reset_count = 0

        world_min_y = -60
        world_max_y = 319

        for x in range(width):
            if x % 50 == 0:
                print(f"  Progress: {x}/{width} columns...")

            column_blocks = []
            current_height = world_min_y

            for z in range(height):
                pixel = tuple(img_array[z, x])
                block, _ = get_closest_block(pixel)

                brightness = calculate_brightness(pixel)
                tone = get_map_tone(brightness)

                height_change = get_height_change(brightness, tone)

                if height_change == -999:
                    current_height = world_min_y
                    if x == 0:
                        reset_count += 1
                else:
                    current_height += height_change

                    if current_height > world_max_y:
                        current_height = world_min_y + (current_height - world_max_y - 1)
                    elif current_height < world_min_y:
                        current_height = world_max_y + (current_height - world_min_y + 1)

                column_blocks.append({
                    'x': x,
                    'y': current_height,
                    'z': z,
                    'block': block,
                    'tone': tone,
                    'brightness': brightness
                })

                if x == 0:
                    tone_stats[tone] += 1

            physical_columns.append(column_blocks)

        total_pixels = width * height
        print(f"\n=== Tone Distribution ===")
        print(f"  Dark:   {tone_stats['dark']:6d} pixels ({tone_stats['dark']/total_pixels*100:5.1f}%)")
        print(f"  Normal: {tone_stats['normal']:6d} pixels ({tone_stats['normal']/total_pixels*100:5.1f}%)")
        print(f"  Light:  {tone_stats['light']:6d} pixels ({tone_stats['light']/total_pixels*100:5.1f}%)")

        print(f"\n=== Height Control ===")
        print(f"  Resets to Y=-60: {reset_count} times ({reset_count/total_pixels*100:5.1f}%)")
        print(f"  This helps control maximum height and creates depth")

        all_y_values = [block['y'] for column in physical_columns for block in column]
        min_y = min(all_y_values)
        max_y = max(all_y_values)
        y_range = max_y - min_y + 1

        print(f"\n  Final Y range: {min_y} to {max_y} ({y_range} levels)")
        print(f"  Each column individually adjusted to fit within world limits")

        print(f"\nConverting to block array...")
        blocks = []
        for x in range(width):
            x_layer = []
            for y_level in range(y_range):
                z_layer = ["air"] * height
                x_layer.append(z_layer)

            for block_info in physical_columns[x]:
                y_index = block_info['y'] - min_y
                z_index = block_info['z']
                x_layer[y_index][z_index] = block_info['block']

            blocks.append(x_layer)

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

                print(
                    f"Chunk {chunk_idx + 1}/{num_chunks}: X={start_x + x_start} to {start_x + x_end} ({blocks_in_chunk:,} blocks)")

                count = self.mc.edit(
                    start_x + x_start, min_y, start_z, chunk_blocks)
                total_placed += count
                print(f"  Placed {count:,} blocks")

            print(f"\n{'='*60}")
            print(f"SUCCESS! Placed {total_placed:,} blocks total")
            print(
                f"Location: ({start_x}, {min_y}, {start_z}) to ({start_x + width}, {max_y}, {start_z + height})")
            print(f"{'='*60}")
        except Exception as e:
            print(f"Error: {e}")

    def draw_vertical(self, image_path, size, start_x, start_y, start_z, num_colors=35):
        """Draw vertically with k-means quantization"""
        print(f"\n{'='*60}")
        print(f"Drawing VERTICAL at ({start_x}, {start_y}, {start_z})")
        print(f"{'='*60}")

        img = load_and_resize(image_path, size)
        width, height = img.size

        img_array = np.array(img)
        img_array = quantize_with_kmeans(img_array, num_colors=num_colors)

        print(f"\nConverting to Minecraft blocks...")
        blocks = []
        for x in range(width):
            x_layer = []
            for y in range(height):
                pixel = tuple(img_array[height - 1 - y, x])
                block, _ = get_closest_block(pixel)
                x_layer.append([block])
            blocks.append(x_layer)

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
