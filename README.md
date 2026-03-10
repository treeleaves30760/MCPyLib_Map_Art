# Minecraft Map Art Drawer

Draw Map Art in Minecraft using mcpylib! This program converts any image into Minecraft blocks and places them in your world either horizontally (on the ground) or vertically (like a wall).

## Features

- Load any image format (PNG, JPG, GIF, etc.)
- Automatically resize images while maintaining aspect ratio
- **K-Means color quantization** - Finds the most important colors in the image and maps them to Minecraft blocks
- Official Minecraft map color palette with 61 distinct colors
- RGB Euclidean distance for accurate color matching
- Draw horizontally (XZ plane) or vertically (XY plane)
- High-performance bulk placement using mcpylib's `edit()` method
- CLI interface with environment variable support

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

### Using the CLI Tool

After installation, you can use the `mcpylib-map-art` command:

```bash
# Basic usage (uses .env configuration)
mcpylib-map-art image.jpg

# With uv
uv run mcpylib-map-art image.jpg

# Specify mode
mcpylib-map-art image.jpg --mode 3d

# Custom size and colors
mcpylib-map-art image.jpg --size 256 --colors 35

# Vertical wall drawing
mcpylib-map-art image.jpg --mode vertical

# Override environment variables
mcpylib-map-art image.jpg --ip 192.168.1.100 --port 25565 --token your_token

# Specify coordinates manually
mcpylib-map-art image.jpg --x 100 --y 64 --z 200
```

### Command Options

- `IMAGE_PATH` - Path to the image file (required)
- `--ip` - Minecraft server IP (default: from SERVER_IP env)
- `--port` - Minecraft server port (default: from SERVER_PORT env)
- `--token` - Authentication token (default: from SERVER_TOKEN env)
- `--player` - Player name to get position from (default: NightTangerine)
- `--size` - Maximum image size in blocks (default: 512)
- `--colors` - Number of colors/k-means clusters (default: 61)
- `--mode` - Drawing mode: `flat`, `3d`, or `vertical` (default: flat)
- `--x`, `--y`, `--z` - Starting coordinates (overrides player position)

### Environment Variables

The tool supports the following environment variables (configured in `.env`):

- `SERVER_IP` - Minecraft server IP address
- `SERVER_PORT` - Minecraft server port
- `SERVER_TOKEN` - MCPyLib authentication token

Command-line options override environment variables.

### Example Session

```bash
$ mcpylib-map-art Logo.jpg --mode flat --size 128
============================================================
MCPyLib Map Art - Modern Map Art Algorithm
============================================================

Connecting to server: 127.0.0.1:65535
Connected to Minecraft server at 127.0.0.1:65535
Using NightTangerine's position: (100, 64, 200)

Image: Logo.jpg
Max size: 128 blocks
Colors: 61
Mode: flat

=== K-Means Color Quantization (Modern Map Art Algorithm) ===
Reducing to 61 most important colors...

[1/3] Finding dominant colors in image...
[2/3] Mapping to Minecraft palette...
[3/3] Applying quantization...

Placing 128x96 blocks in Minecraft...
SUCCESS! Placed 12,288 blocks total

Done! Check your Minecraft world.
```

## Drawing Modes

### Flat Mode (`--mode flat`)
- Draws the image flat on the ground (XZ plane)
- Perfect for pixel art floors, maps, or ground decorations
- Y coordinate is constant (one layer thick)
- Default mode

### 3D Mode (`--mode 3d`)
- Creates 3D staircase map art with height variations
- Uses brightness to determine height changes
- Full height range from Y=-60 to Y=319
- Perfect for realistic map art with depth and shading

### Vertical Mode (`--mode vertical`)
- Draws the image as a wall (XY plane)
- Perfect for paintings, murals, or vertical pixel art
- Z coordinate is constant (one block deep)

## Color Mapping

The program uses the **official Minecraft map color system** with 61 distinct colors, providing highly accurate color representation. Colors are automatically matched to the closest available block using Euclidean distance calculation in RGB color space.

### Available Color Categories:

**Basic Colors (Concrete & Wool):**
- White, Light Gray, Gray, Black
- Red, Orange, Yellow
- Lime, Green
- Cyan, Light Blue, Blue
- Purple, Magenta, Pink
- Brown

**Terracotta Colors (Muted Tones):**
- All basic colors in terracotta variants
- Perfect for more subdued, natural-looking pixel art

**Natural Blocks:**
- Grass, Dirt, Sand, Stone, Wood
- Podzol, Clay, Netherrack
- Leaves, Ice, Snow

**Special Blocks:**
- Gold Block, Diamond Block, Emerald Block, Lapis Block
- Iron Block, Deepslate, Raw Iron
- Crimson/Warped Nether blocks
- Glow Lichen (unique greenish glow)

**Total: 61 unique colors** for maximum image accuracy!

## Tips

1. **Image Size**: Start with smaller sizes (32x32) for testing, then scale up
2. **Color Accuracy**: The program now uses 61 official Minecraft colors for better accuracy
3. **Complex Images**: With 61 colors, you can now render more detailed images with better color gradients
4. **Coordinates**: Make sure you have space in your world for the image
5. **Performance**: The `edit()` method can handle thousands of blocks at once
6. **Vertical Drawings**: Good for building facades or interior decoration
7. **Block Availability**: Some blocks like nether blocks, terracotta, and ores may require creative mode or resource gathering

## Troubleshooting

- **Image not found**: Check that the file path is correct
- **Connection failed**: Verify server IP, port, and token
- **Out of bounds**: Check that coordinates are within your world limits
- **Colors look wrong**: The program uses nearest color matching - simplify your image for better results

## Project Structure

```
.
├── main.py              # Entry point
├── map_art/
│   ├── __init__.py      # Package exports
│   ├── cli.py           # CLI interface (click)
│   ├── colors.py        # Minecraft color palette & color utilities
│   ├── drawer.py        # MinecraftImageDrawer class (drawing methods)
│   └── image.py         # Image loading & k-means quantization
├── pyproject.toml       # Project dependencies
├── Documents.md         # mcpylib API documentation
└── README.md            # This file
```

## Algorithm

### K-Means Color Quantization
The program uses **k-means clustering** to produce clean, coherent map art:
1. Finds the N most important colors in the image via k-means clustering
2. Maps each cluster center to the closest Minecraft block color (RGB Euclidean distance)
3. Replaces all pixels with their cluster's Minecraft color
- Produces clean color regions without dithering noise
- Configurable number of colors via `--colors` (default: 61)

## Requirements

- Python 3.11+
- mcpylib >= 1.0.0
- Pillow >= 10.0.0
- numpy >= 1.24.0
- scikit-learn >= 1.3.0
- click >= 8.1.0
- python-dotenv >= 1.0.0
- Minecraft server with mcpylib plugin installed

## License

This project is licensed under a **Dual License** model:

### Non-Commercial Use (Free)
✅ **FREE** for personal, educational (non-profit), research, and open-source projects
- Personal hobby projects
- Non-profit educational institutions for teaching
- Academic research
- Community projects

### Commercial Use (Authorization Required)
⚠️ **AUTHORIZATION REQUIRED** for commercial purposes, including:
- Paid tutoring/cram schools (補習班)
- For-profit training courses
- Commercial educational programs
- Business or for-profit entities
- Revenue-generating services

**For commercial use authorization, please contact:**
📧 treeleaves30760@gmail.com
🔗 https://github.com/treeleaves30760/MCPyLib_Map_Art

See the [LICENSE](LICENSE) file for complete terms and conditions.
