import numpy as np

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
    (112, 108, 138): "light_blue_terracotta",  # ID 39 - TERRACOTTA_LIGHT_BLUE
    (186, 133, 36): "yellow_terracotta",     # ID 40 - TERRACOTTA_YELLOW
    (103, 117, 53): "lime_terracotta",       # ID 41 - TERRACOTTA_LIME
    (160, 77, 78): "pink_terracotta",        # ID 42 - TERRACOTTA_PINK
    (57, 41, 35): "gray_terracotta",         # ID 43 - TERRACOTTA_GRAY
    (135, 107, 98): "light_gray_terracotta",  # ID 44 - TERRACOTTA_LIGHT_GRAY
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


def get_closest_block(rgb):
    """Find closest Minecraft block using simple Euclidean distance"""
    r = int(np.clip(rgb[0], 0, 255))
    g = int(np.clip(rgb[1], 0, 255))
    b = int(np.clip(rgb[2], 0, 255))

    min_distance = float('inf')
    closest_block = "white_concrete"
    closest_color = (255, 255, 255)

    for color, block in COLOR_MAP.items():
        cr, cg, cb = color
        dr = r - cr
        dg = g - cg
        db = b - cb
        distance = dr * dr + dg * dg + db * db

        if distance < min_distance:
            min_distance = distance
            closest_block = block
            closest_color = color

    return closest_block, closest_color


def calculate_brightness(rgb):
    """Calculate perceived brightness of an RGB color

    Uses luminance formula: 0.299*R + 0.587*G + 0.114*B
    Returns value between 0.0 and 1.0
    """
    r, g, b = rgb[0], rgb[1], rgb[2]
    return (0.299 * r + 0.587 * g + 0.114 * b) / 255.0


def get_map_tone(brightness):
    """Determine map tone based on brightness for staircase algorithm

    Minecraft maps have 4 tones per color, controlled by height differences:
    - dark: block is 1 level LOWER than previous
    - normal: block is at SAME level as previous
    - light: block is 1 level HIGHER than previous
    """
    if brightness < 0.33:
        return "dark"
    elif brightness < 0.67:
        return "normal"
    else:
        return "light"


def get_height_change(brightness, tone):
    """Calculate height change with aggressive reset strategy

    Returns special value -999 to indicate reset to Y=-60.
    """
    if tone == "light":
        return 1
    elif tone == "normal":
        return 0
    else:  # dark
        if brightness < 0.25:
            return -999  # Special value: reset to Y=-60
        else:
            return -1
