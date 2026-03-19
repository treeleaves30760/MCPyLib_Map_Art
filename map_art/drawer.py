"""Place map-art blocks in a Minecraft server via MCPyLib."""

import sys

import numpy as np
from mcpylib import MCPyLib

from map_art.colors import (
    MapPalette,
    compute_staircase_heights,
    get_closest_block,
)
from map_art.image import load_and_resize


class MinecraftImageDrawer:
    """Draw images in Minecraft using map-art algorithms."""

    def __init__(self, ip="127.0.0.1", port=65535, token="", timeout=10.0):
        try:
            self.mc = MCPyLib(ip=ip, port=port, token=token, timeout=timeout)
            print(f"Connected to Minecraft server at {ip}:{port}")
        except Exception as e:
            print(f"Failed to connect to Minecraft server: {e}")
            sys.exit(1)

    # ------------------------------------------------------------------
    # Area clearing
    # ------------------------------------------------------------------

    def clear_area(self, start_x, start_z, width, depth,
                   border=16, extra_north=0,
                   y_min=-60, y_max=319, max_per_chunk=100000):
        """Fill the build area (+ border) with air."""
        cx = start_x - border
        cz = start_z - border - extra_north
        cw = width + 2 * border
        cd = depth + 2 * border + extra_north
        y_range = y_max - y_min + 1

        print(f"\n=== Clearing Build Area ===")
        print(f"From ({cx}, {y_min}, {cz})  size {cw} x {y_range} x {cd}")

        xz = cw * cd
        y_per_chunk = max(1, max_per_chunk // xz)
        total_cleared = 0
        cur_y = y_min

        while cur_y <= y_max:
            yl = min(y_per_chunk, y_max - cur_y + 1)
            air = [[[
                "air" for _z in range(cd)]
                for _y in range(yl)]
                for _x in range(cw)]
            count = self.mc.edit(cx, cur_y, cz, air)
            total_cleared += count
            cur_y += yl

        print(f"Cleared {total_cleared:,} blocks\n")

    # ------------------------------------------------------------------
    # Flat (2-D) map art
    # ------------------------------------------------------------------

    def draw_flat(self, image_path, size, start_x, start_y, start_z,
                  dither=False, max_per_chunk=100000):
        """Flat horizontal map art (all blocks at same Y -> shade "normal")."""
        print(f"\n{'='*60}")
        print(f"Drawing FLAT MAP ART  (dither={'ON' if dither else 'OFF'})")
        print(f"Position: ({start_x}, {start_y}, {start_z})")
        print(f"{'='*60}")

        img = load_and_resize(image_path, size)
        width, height = img.size
        img_array = np.array(img)

        palette = MapPalette(mode="flat")
        print(f"Palette: {len(palette.entries)} colours (flat / shade normal)")

        if dither:
            print("Applying Floyd-Steinberg dithering ...")
            idx_map = palette.dither_pixels(img_array)
        else:
            print("Matching pixels to palette ...")
            idx_map = palette.match_pixels(img_array)

        block_map = palette.indices_to_blocks(idx_map)

        # Build 3-D array:  blocks[x][1 y-level][z]
        blocks_3d = []
        for x in range(width):
            blocks_3d.append([[block_map[z][x] for z in range(height)]])

        self._place_chunked(blocks_3d, start_x, start_y, start_z,
                            width, 1, height, max_per_chunk)

    # ------------------------------------------------------------------
    # Staircase (3-D) map art
    # ------------------------------------------------------------------

    def draw_staircase(self, image_path, size, start_x, start_z,
                       dither=False, max_per_chunk=100000):
        """Staircase map art using height differences for 3x colour palette."""
        print(f"\n{'='*60}")
        print(f"Drawing STAIRCASE MAP ART  (dither={'ON' if dither else 'OFF'})")
        print(f"Position: ({start_x}, variable Y, {start_z})")
        print(f"{'='*60}")

        img = load_and_resize(image_path, size)
        width, height = img.size
        img_array = np.array(img)

        palette = MapPalette(mode="staircase")
        print(f"Palette: {len(palette.entries)} colours (staircase)")

        if dither:
            print("Applying Floyd-Steinberg dithering ...")
            idx_map = palette.dither_pixels(img_array)
        else:
            print("Matching pixels to palette ...")
            idx_map = palette.match_pixels(img_array)

        block_map = palette.indices_to_blocks(idx_map)
        shade_map = palette.indices_to_shades(idx_map)

        # Height computation
        print("Computing staircase heights ...")
        heights, ref_heights = compute_staircase_heights(shade_map)

        all_ys = ref_heights[:]
        for row in heights:
            all_ys.extend(row)
        min_y = min(all_ys)
        max_y = max(all_ys)
        y_range = max_y - min_y + 1
        print(f"Y range: {min_y} to {max_y} ({y_range} levels)")

        # Clear area (include 1 row north for reference blocks)
        self.clear_area(start_x, start_z, width, height,
                        border=16, extra_north=1)

        # Build sparse 3-D array:  blocks[x][dy][dz]
        # dz=0 is the reference row (Z = start_z - 1)
        # dz=1..height are image rows (Z = start_z .. start_z+height-1)
        z_depth = height + 1
        print(f"Building block array  {width} x {y_range} x {z_depth} ...")
        blocks_3d = []
        for x in range(width):
            x_layer = [[None] * z_depth for _ in range(y_range)]
            # Reference block
            ry = ref_heights[x] - min_y
            x_layer[ry][0] = block_map[0][x]   # same block as first row
            # Image blocks
            for z in range(height):
                yi = heights[z][x] - min_y
                x_layer[yi][z + 1] = block_map[z][x]
            blocks_3d.append(x_layer)

        self._place_chunked(blocks_3d, start_x, min_y, start_z - 1,
                            width, y_range, z_depth, max_per_chunk)

    # ------------------------------------------------------------------
    # Vertical (wall) art  –  no map rendering, just visual blocks
    # ------------------------------------------------------------------

    def draw_vertical(self, image_path, size, start_x, start_y, start_z):
        """Build a vertical wall of blocks (not map art)."""
        print(f"\n{'='*60}")
        print(f"Drawing VERTICAL at ({start_x}, {start_y}, {start_z})")
        print(f"{'='*60}")

        img = load_and_resize(image_path, size)
        width, height = img.size
        img_array = np.array(img)

        blocks = []
        for x in range(width):
            x_layer = []
            for y in range(height):
                pixel = tuple(img_array[height - 1 - y, x])
                block, _ = get_closest_block(pixel)
                x_layer.append([block])
            blocks.append(x_layer)

        try:
            count = self.mc.edit(start_x, start_y, start_z, blocks)
            print(f"\nSUCCESS! Placed {count} blocks")
        except Exception as e:
            print(f"Error: {e}")

    # ------------------------------------------------------------------
    # Internal: chunked placement
    # ------------------------------------------------------------------

    def _place_chunked(self, blocks_3d, sx, sy, sz,
                       x_size, y_size, z_size, max_per_chunk):
        """Send blocks to server in X-column chunks."""
        blocks_per_col = y_size * z_size
        x_per_chunk = max(1, max_per_chunk // blocks_per_col)
        num_chunks = (x_size + x_per_chunk - 1) // x_per_chunk

        print(f"\nPlacing blocks  ({x_size} x {y_size} x {z_size})")
        print(f"Chunks: {num_chunks}  ({x_per_chunk} X-columns each)\n")

        total = 0
        for ci in range(num_chunks):
            xs = ci * x_per_chunk
            xe = min(xs + x_per_chunk, x_size)
            chunk = blocks_3d[xs:xe]
            n = (xe - xs) * blocks_per_col
            print(f"  Chunk {ci+1}/{num_chunks}:  X {sx+xs}..{sx+xe-1}  ({n:,} slots)")
            count = self.mc.edit(sx + xs, sy, sz, chunk)
            total += count
            print(f"    placed {count:,}")

        print(f"\n{'='*60}")
        print(f"SUCCESS! Placed {total:,} blocks total")
        print(f"{'='*60}")
