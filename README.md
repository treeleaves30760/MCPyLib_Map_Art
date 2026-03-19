# Minecraft Map Art Drawer

Draw Map Art in Minecraft using mcpylib! This program converts any image into Minecraft blocks and places them in your world, fully leveraging the map's shade system for maximum colour accuracy.

## Features

- Load any image format (PNG, JPG, GIF, etc.)
- Automatically resize images while maintaining aspect ratio
- **Accurate map colour system** - 60 base colours x 3 shades = **180 colours** in staircase mode
- **Perceptual colour matching** using redmean weighted distance
- **Floyd-Steinberg dithering** for smoother gradients
- **Staircase map art** - uses block height differences to unlock the full shade palette
- **Built-in simulator** - preview results and analyse quality without a Minecraft server
- High-performance bulk placement using mcpylib's `edit()` method
- CLI interface with environment variable support

## How Minecraft Map Colours Work

Each pixel on a Minecraft map is determined by **two factors**:

| Factor | Description |
|--------|-------------|
| **Base colour** | Determined by block type (60 usable colours) |
| **Shade** | Determined by height difference with the block to the **north (Z-1)** |

The shade multiplies the base colour RGB values:

| Shade | Multiplier | Trigger |
|-------|-----------|---------|
| Dark | x 180/255 (71%) | Current block **lower** than north neighbour |
| Normal | x 220/255 (86%) | Current block **same height** as north neighbour |
| Light | x 255/255 (100%) | Current block **higher** than north neighbour |

This means:
- **Flat mode** (all same height) = 60 colours (all shade "normal")
- **Staircase mode** (varying heights) = **180 colours** (60 x 3 shades)

## Installation

1. Clone the repository:
```bash
git clone https://github.com/treeleaves30760/MCPyLib_Map_Art.git
cd MCPyLib_Map_Art
```

2. Install dependencies and the CLI tool using uv:
```bash
uv sync
uv pip install -e .
```

Or with pip:
```bash
pip install -e .
```

3. Configure environment variables:
```bash
cp .env.example .env
```

Edit `.env` and set your server credentials:
```
SERVER_IP=127.0.0.1
SERVER_PORT=65535
SERVER_TOKEN=your_token_here
```

## Usage

### Simulate (Preview Without Server)

Preview map art and compare quality metrics **without connecting to Minecraft**:

```bash
# Basic simulation (128x128 = one map)
python main.py simulate photo.jpg

# Custom size and output directory
python main.py simulate photo.jpg --size 256 --output-dir my_output
```

The simulator automatically tests all four algorithm variants and outputs:

| Output File | Description |
|-------------|-------------|
| `*_original.png` | Resized input image |
| `*_flat.png` | Flat mode result |
| `*_flat_dither.png` | Flat mode + dithering |
| `*_staircase.png` | Staircase mode result |
| `*_staircase_dither.png` | Staircase mode + dithering |
| `*_comparison.png` | Side-by-side comparison with error heatmaps |
| `*_heightmap.png` | Staircase height visualisation |
| `*_metrics.txt` | PSNR, SSIM, mean error, colour count |

### Draw on Server

```bash
# Flat mode (simple, all blocks at same height)
python main.py draw photo.jpg --mode flat

# Staircase mode with dithering (best quality)
python main.py draw photo.jpg --mode staircase --dither

# Vertical wall art (not map art, just visual blocks)
python main.py draw photo.jpg --mode vertical

# Override server settings
python main.py draw photo.jpg --ip 192.168.1.100 --port 25565 --token your_token

# Specify coordinates manually
python main.py draw photo.jpg --mode staircase --dither --x 100 --y 64 --z 200
```

### Command Options

**`draw` subcommand:**

| Option | Description | Default |
|--------|-------------|---------|
| `IMAGE_PATH` | Path to the image file | (required) |
| `--mode` | `flat`, `staircase`, or `vertical` | `flat` |
| `--dither` | Enable Floyd-Steinberg dithering | off |
| `--size` | Maximum image size in blocks | `128` |
| `--ip` | Server IP | `SERVER_IP` env |
| `--port` | Server port | `SERVER_PORT` env |
| `--token` | Auth token | `SERVER_TOKEN` env |
| `--player` | Player name for position | `NightTangerine` |
| `--x`, `--y`, `--z` | Starting coordinates | player position |

**`simulate` subcommand:**

| Option | Description | Default |
|--------|-------------|---------|
| `IMAGE_PATH` | Path to the image file | (required) |
| `--size` | Maximum image size in pixels | `128` |
| `--output-dir` | Output directory | `output/` |

### Environment Variables

| Variable | Description |
|----------|-------------|
| `SERVER_IP` | Minecraft server IP address |
| `SERVER_PORT` | Minecraft server port |
| `SERVER_TOKEN` | MCPyLib authentication token |

Command-line options override environment variables.

## Drawing Modes

### Flat Mode (`--mode flat`)
- All blocks at the same Y height -> every pixel uses shade "normal"
- Available palette: **60 colours**
- Simple to build, no height variation needed
- Add `--dither` for visually smoother gradients

### Staircase Mode (`--mode staircase`)
- Block heights vary to control shade per pixel
- Available palette: **180 colours** (60 base x 3 shades)
- A reference row is placed one block north to control the first row's shade
- Heights are automatically centred within world limits (Y -60 to 319)
- **Recommended mode** for best quality; combine with `--dither`

### Vertical Mode (`--mode vertical`)
- Draws the image as a wall on the XY plane
- Not map art — just visual block placement
- Useful for paintings, murals, or interior decoration

## Algorithm

### Colour Matching Pipeline

```
Input Image
    |
    v
Resize to target size (LANCZOS)
    |
    v
Build palette (60 or 180 colours depending on mode)
    |
    v
For each pixel, find closest palette colour (redmean distance)
    |                                |
    v                                v
  [no dither]                   [--dither]
  Direct mapping          Floyd-Steinberg error diffusion
    |                                |
    v                                v
        Block map + Shade map
              |
              v
     Compute staircase heights (for staircase mode)
              |
              v
        Place blocks in Minecraft
```

### Redmean Colour Distance

Instead of simple Euclidean RGB distance, we use the **redmean** approximation which better matches human colour perception:

```
rmean = (R1 + R2) / 2
d = (2 + rmean/256) * dR^2 + 4 * dG^2 + (2 + (255-rmean)/256) * dB^2
```

### Floyd-Steinberg Dithering

Error diffusion distributes quantisation error to neighbouring pixels, creating the visual illusion of more colours:

```
             pixel   7/16 ->
   3/16      5/16    1/16
```

### Staircase Height Management

For each column (fixed X), the algorithm:
1. Determines the ideal shade for every row based on colour matching
2. Computes cumulative height changes (light: +1, normal: 0, dark: -1)
3. Centres the height range within world limits (Y -60 to 319)
4. Places a reference block one row north to control the first row's shade

## Quality Comparison

Test results with a 128x128 image:

| Mode | PSNR (dB) | SSIM | Mean Error | Colours Used |
|------|-----------|------|------------|-------------|
| Flat | 17.38 | 0.9470 | 58.82 | 29 |
| Flat + Dither | 17.28 | 0.9284 | 59.69 | 40 |
| **Staircase** | **29.69** | **0.9658** | **4.44** | 66 |
| **Staircase + Dither** | **29.01** | **0.9577** | **5.08** | 85 |

Staircase mode reduces mean colour error by **13x** compared to flat mode.

## Project Structure

```
.
├── main.py              # Entry point
├── map_art/
│   ├── __init__.py      # Package exports
│   ├── cli.py           # CLI interface (click) - draw & simulate commands
│   ├── colors.py        # Map palette, shade system, colour matching, dithering
│   ├── drawer.py        # MinecraftImageDrawer (server block placement)
│   ├── image.py         # Image loading & resizing
│   └── simulator.py     # Offline simulation & quality analysis
├── pyproject.toml       # Project dependencies
├── Documents.md         # mcpylib API documentation
└── README.md            # This file
```

## Requirements

- Python 3.11+
- mcpylib >= 1.0.0
- Pillow >= 10.0.0
- numpy >= 1.24.0
- scipy >= 1.10.0
- click >= 8.1.0
- python-dotenv >= 1.0.0
- Minecraft server with mcpylib plugin installed (for drawing; simulator works offline)

## Troubleshooting

- **Image not found**: Check that the file path is correct
- **Connection failed**: Verify server IP, port, and token in `.env`
- **Out of bounds**: Check that coordinates are within your world limits
- **Dithering is slow**: Normal for large images; use `--size 128` for faster processing
- **Colours look wrong**: Use `--mode staircase --dither` for best accuracy; run `simulate` first to preview

## License

This project is licensed under a **Dual License** model:

### Non-Commercial Use (Free)
**FREE** for personal, educational (non-profit), research, and open-source projects.

### Commercial Use (Authorization Required)
**AUTHORIZATION REQUIRED** for commercial purposes, including paid tutoring, for-profit training courses, commercial educational programs, business use, and revenue-generating services.

**For commercial use authorization, please contact:**
- Email: treeleaves30760@gmail.com
- GitHub: https://github.com/treeleaves30760/MCPyLib_Map_Art

See the [LICENSE](LICENSE) file for complete terms and conditions.
