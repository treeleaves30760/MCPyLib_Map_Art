"""Minecraft map color palette system.

Minecraft maps display colors based on two factors:
1. Block type -> base color (61 base colors, excluding water)
2. Height difference with the block to the NORTH (Z-1) -> shade

Shade rules:
  - current Y > north Y  -> shade "light"  (base_rgb * 255/255 = full)
  - current Y == north Y -> shade "normal" (base_rgb * 220/255)
  - current Y < north Y  -> shade "dark"   (base_rgb * 180/255)

Available palette sizes:
  - Flat mode:      60 colors (all shade "normal")
  - Staircase mode: 180 colors (60 base * 3 shades)
"""

import numpy as np

# Base colors at full brightness (shade "light" = multiply by 255/255).
# Source: Minecraft Wiki map color table.
# Format: (base_rgb, block_name, map_color_id_name)
#
# IMPORTANT: each block MUST actually produce the listed base color on a map.
# e.g. redstone_block -> FIRE color, NOT red_concrete (which gives RED color).
BASE_COLORS = [
    ((127, 178, 56),  "grass_block",           "GRASS"),
    ((247, 233, 163), "sandstone",             "SAND"),
    ((199, 199, 199), "white_wool",            "WOOL"),
    ((255, 0, 0),     "redstone_block",        "FIRE"),
    ((160, 160, 255), "packed_ice",            "ICE"),
    ((167, 167, 167), "iron_block",            "METAL"),
    ((0, 124, 0),     "oak_leaves",            "PLANT"),
    ((255, 255, 255), "white_concrete",        "SNOW"),
    ((164, 168, 184), "clay",                  "CLAY"),
    ((151, 109, 77),  "dirt",                  "DIRT"),
    ((112, 112, 112), "stone",                 "STONE"),
    # WATER (64,64,255) excluded: requires special depth-based shade handling
    ((143, 119, 72),  "oak_planks",            "WOOD"),
    ((255, 252, 245), "quartz_block",          "QUARTZ"),
    ((216, 127, 51),  "orange_concrete",       "COLOR_ORANGE"),
    ((178, 76, 216),  "magenta_concrete",      "COLOR_MAGENTA"),
    ((102, 153, 216), "light_blue_concrete",   "COLOR_LIGHT_BLUE"),
    ((229, 229, 51),  "yellow_concrete",       "COLOR_YELLOW"),
    ((127, 204, 25),  "lime_concrete",         "COLOR_LIME"),
    ((242, 127, 165), "pink_concrete",         "COLOR_PINK"),
    ((76, 76, 76),    "gray_concrete",         "COLOR_GRAY"),
    ((153, 153, 153), "light_gray_concrete",   "COLOR_LIGHT_GRAY"),
    ((76, 127, 153),  "cyan_concrete",         "COLOR_CYAN"),
    ((127, 63, 178),  "purple_concrete",       "COLOR_PURPLE"),
    ((51, 76, 178),   "blue_concrete",         "COLOR_BLUE"),
    ((102, 76, 51),   "brown_concrete",        "COLOR_BROWN"),
    ((102, 127, 51),  "green_concrete",        "COLOR_GREEN"),
    ((153, 51, 51),   "red_concrete",          "COLOR_RED"),
    ((25, 25, 25),    "black_concrete",        "COLOR_BLACK"),
    ((250, 238, 77),  "gold_block",            "GOLD"),
    ((92, 219, 213),  "diamond_block",         "DIAMOND"),
    ((74, 128, 255),  "lapis_block",           "LAPIS"),
    ((0, 217, 58),    "emerald_block",         "EMERALD"),
    ((129, 86, 49),   "podzol",                "PODZOL"),
    ((112, 2, 0),     "netherrack",            "NETHER"),
    ((209, 177, 161), "white_terracotta",      "TERRACOTTA_WHITE"),
    ((159, 82, 36),   "orange_terracotta",     "TERRACOTTA_ORANGE"),
    ((149, 87, 108),  "magenta_terracotta",    "TERRACOTTA_MAGENTA"),
    ((112, 108, 138), "light_blue_terracotta", "TERRACOTTA_LIGHT_BLUE"),
    ((186, 133, 36),  "yellow_terracotta",     "TERRACOTTA_YELLOW"),
    ((103, 117, 53),  "lime_terracotta",       "TERRACOTTA_LIME"),
    ((160, 77, 78),   "pink_terracotta",       "TERRACOTTA_PINK"),
    ((57, 41, 35),    "gray_terracotta",       "TERRACOTTA_GRAY"),
    ((135, 107, 98),  "light_gray_terracotta", "TERRACOTTA_LIGHT_GRAY"),
    ((87, 92, 92),    "cyan_terracotta",       "TERRACOTTA_CYAN"),
    ((122, 73, 88),   "purple_terracotta",     "TERRACOTTA_PURPLE"),
    ((76, 62, 92),    "blue_terracotta",       "TERRACOTTA_BLUE"),
    ((76, 50, 35),    "brown_terracotta",      "TERRACOTTA_BROWN"),
    ((76, 82, 42),    "green_terracotta",      "TERRACOTTA_GREEN"),
    ((142, 60, 46),   "red_terracotta",        "TERRACOTTA_RED"),
    ((37, 22, 16),    "black_terracotta",      "TERRACOTTA_BLACK"),
    ((189, 48, 49),   "crimson_nylium",        "CRIMSON_NYLIUM"),
    ((148, 63, 97),   "crimson_planks",        "CRIMSON_STEM"),
    ((92, 25, 29),    "crimson_hyphae",        "CRIMSON_HYPHAE"),
    ((22, 126, 134),  "warped_nylium",         "WARPED_NYLIUM"),
    ((58, 142, 140),  "warped_planks",         "WARPED_STEM"),
    ((86, 44, 62),    "warped_hyphae",         "WARPED_HYPHAE"),
    ((20, 180, 133),  "warped_wart_block",     "WARPED_WART_BLOCK"),
    ((100, 100, 100), "deepslate",             "DEEPSLATE"),
    ((216, 175, 147), "raw_iron_block",        "RAW_IRON"),
    ((127, 167, 150), "glow_lichen",           "GLOW_LICHEN"),
]

SHADE_MULTIPLIERS = {
    "dark":   180,   # x * 180 // 255
    "normal": 220,   # x * 220 // 255
    "light":  255,   # x * 255 // 255  (unchanged)
}

SHADE_HEIGHT_DELTA = {
    "light":  1,
    "normal": 0,
    "dark":  -1,
}


def apply_shade(base_rgb, shade):
    """Apply shade multiplier to a base RGB tuple."""
    m = SHADE_MULTIPLIERS[shade]
    return (
        base_rgb[0] * m // 255,
        base_rgb[1] * m // 255,
        base_rgb[2] * m // 255,
    )


class MapPalette:
    """Minecraft map art color palette with matching and dithering."""

    def __init__(self, mode="staircase"):
        """
        Args:
            mode: "flat"      -> 60 colors  (normal shade only)
                  "staircase" -> 180 colors (dark / normal / light)
        """
        self.mode = mode
        shades = ["normal"] if mode == "flat" else ["dark", "normal", "light"]

        self.entries = []
        for base_rgb, block, _name in BASE_COLORS:
            for shade in shades:
                self.entries.append({
                    "displayed_rgb": apply_shade(base_rgb, shade),
                    "base_rgb": base_rgb,
                    "block": block,
                    "shade": shade,
                })

        self.rgb_array = np.array(
            [e["displayed_rgb"] for e in self.entries], dtype=np.float64
        )
        self.blocks = [e["block"] for e in self.entries]
        self.shades = [e["shade"] for e in self.entries]

    # ------------------------------------------------------------------
    # Matching
    # ------------------------------------------------------------------

    def match_pixels(self, img_array, chunk_size=4096):
        """Find closest palette colour for every pixel (vectorised).

        Args:
            img_array: (H, W, 3) uint8
        Returns:
            (H, W) int32 palette indices
        """
        H, W = img_array.shape[:2]
        pixels = img_array.reshape(-1, 3).astype(np.float64)
        P = pixels.shape[0]
        indices = np.empty(P, dtype=np.int32)

        for start in range(0, P, chunk_size):
            end = min(start + chunk_size, P)
            dists = _distance_matrix(pixels[start:end], self.rgb_array)
            indices[start:end] = np.argmin(dists, axis=1)

        return indices.reshape(H, W)

    # ------------------------------------------------------------------
    # Floyd-Steinberg dithering
    # ------------------------------------------------------------------

    def dither_pixels(self, img_array):
        """Floyd-Steinberg error-diffusion dithering to palette.

        Returns: (H, W) int32 palette indices
        """
        H, W = img_array.shape[:2]
        work = img_array.astype(np.float64).copy()
        indices = np.empty((H, W), dtype=np.int32)

        for y in range(H):
            if y % 32 == 0:
                print(f"  Dithering row {y}/{H} ...")
            for x in range(W):
                pixel = np.clip(work[y, x], 0, 255)
                dists = _pixel_distances(pixel, self.rgb_array)
                best = int(np.argmin(dists))
                indices[y, x] = best
                error = pixel - self.rgb_array[best]

                if x + 1 < W:
                    work[y, x + 1] += error * (7.0 / 16.0)
                if y + 1 < H:
                    if x - 1 >= 0:
                        work[y + 1, x - 1] += error * (3.0 / 16.0)
                    work[y + 1, x] += error * (5.0 / 16.0)
                    if x + 1 < W:
                        work[y + 1, x + 1] += error * (1.0 / 16.0)

        return indices

    # ------------------------------------------------------------------
    # Helpers to convert index maps
    # ------------------------------------------------------------------

    def indices_to_image(self, index_map):
        """(H,W) indices -> (H,W,3) uint8 displayed colours."""
        flat = index_map.flatten()
        return self.rgb_array[flat].reshape(
            index_map.shape[0], index_map.shape[1], 3
        ).astype(np.uint8)

    def indices_to_blocks(self, index_map):
        """(H,W) indices -> list[list[str]] block names  [z][x]."""
        H, W = index_map.shape
        return [[self.blocks[index_map[z, x]] for x in range(W)]
                for z in range(H)]

    def indices_to_shades(self, index_map):
        """(H,W) indices -> list[list[str]] shade names  [z][x]."""
        H, W = index_map.shape
        return [[self.shades[index_map[z, x]] for x in range(W)]
                for z in range(H)]


# ------------------------------------------------------------------
# Staircase height computation
# ------------------------------------------------------------------

def compute_staircase_heights(shade_map, world_min_y=-60, world_max_y=319):
    """Convert shade map to per-block Y coordinates.

    Args:
        shade_map: list[list[str]]  [z][x] shade names
    Returns:
        heights:     list[list[int]] [z][x] Y coordinates
        ref_heights: list[int]       [x]    reference-row Y per column
    """
    H = len(shade_map)
    W = len(shade_map[0]) if H > 0 else 0

    heights = [[0] * W for _ in range(H)]
    ref_heights = [0] * W

    for x in range(W):
        # Cumulative deltas (relative to reference=0)
        cum = []
        for z in range(H):
            delta = SHADE_HEIGHT_DELTA[shade_map[z][x]]
            prev = cum[-1] if cum else 0
            cum.append(prev + delta)

        all_h = [0] + cum  # include reference at 0
        min_h = min(all_h)
        max_h = max(all_h)
        world_range = world_max_y - world_min_y

        if (max_h - min_h) <= world_range:
            shift = world_min_y - min_h + (world_range - (max_h - min_h)) // 2
        else:
            shift = world_min_y - min_h

        ref_heights[x] = shift  # reference row Y
        for z in range(H):
            heights[z][x] = cum[z] + shift

    return heights, ref_heights


# ------------------------------------------------------------------
# Backward-compatible helper for vertical mode (no map rendering)
# ------------------------------------------------------------------

_VERTICAL_PALETTE = None

def get_closest_block(rgb):
    """Simple closest-block lookup using base colours at shade "normal".

    Returns (block_name, matched_rgb).
    Used only for vertical (wall) mode where map shading does not apply.
    """
    global _VERTICAL_PALETTE
    if _VERTICAL_PALETTE is None:
        _VERTICAL_PALETTE = MapPalette(mode="flat")

    pixel = np.array([[list(rgb)]], dtype=np.uint8)
    idx = _VERTICAL_PALETTE.match_pixels(pixel)[0, 0]
    entry = _VERTICAL_PALETTE.entries[idx]
    return entry["block"], entry["displayed_rgb"]


# ------------------------------------------------------------------
# Distance helpers (module-level for reuse)
# ------------------------------------------------------------------

def _distance_matrix(pixels, palette):
    """Redmean perceptual colour distance.  pixels (P,3)  palette (N,3) -> (P,N)"""
    p = pixels[:, np.newaxis, :]
    c = palette[np.newaxis, :, :]
    rmean = (p[:, :, 0] + c[:, :, 0]) / 2.0
    dr = p[:, :, 0] - c[:, :, 0]
    dg = p[:, :, 1] - c[:, :, 1]
    db = p[:, :, 2] - c[:, :, 2]
    return (2 + rmean / 256) * dr * dr + 4 * dg * dg + (2 + (255 - rmean) / 256) * db * db


def _pixel_distances(pixel, palette):
    """Redmean distances from one pixel (3,) to palette (N,3) -> (N,)."""
    rmean = (pixel[0] + palette[:, 0]) / 2.0
    dr = pixel[0] - palette[:, 0]
    dg = pixel[1] - palette[:, 1]
    db = pixel[2] - palette[:, 2]
    return (2 + rmean / 256) * dr * dr + 4 * dg * dg + (2 + (255 - rmean) / 256) * db * db
