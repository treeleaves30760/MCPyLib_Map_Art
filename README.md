# Minecraft Image Drawer

Draw images in Minecraft using mcpylib! This program converts any image into Minecraft blocks and places them in your world either horizontally (on the ground) or vertically (like a wall).

## Features

- Load any image format (PNG, JPG, GIF, etc.)
- Automatically resize images while maintaining aspect ratio
- **Advanced color processing algorithms:**
  - **Floyd-Steinberg dithering** - Creates smooth color transitions and gradients
  - **LAB color space matching** - Perceptually accurate color selection
  - **Median filtering** - Removes isolated pixels and noise
- Enhanced color palette with 85+ blocks for accurate representation
- Draw horizontally (XZ plane) or vertically (XY plane)
- High-performance bulk placement using mcpylib's `edit()` method
- Interactive command-line interface

## Installation

1. Install dependencies:
```bash
uv sync
```

Or with pip:
```bash
pip install -r pyproject.toml
```

## Usage

Run the program:
```bash
uv run python main.py
```

Or:
```bash
python main.py
```

### Input Prompts

The program will ask you for:

1. **Server IP** - Your Minecraft server IP (default: 127.0.0.1)
2. **Server Port** - Your Minecraft server port (default: 65535)
3. **Authentication Token** - Your mcpylib authentication token
4. **Image File Path** - Path to your image file (e.g., `image.png` or `C:\images\photo.jpg`)
5. **Max Size** - Maximum width/height in blocks (default: 32)
6. **Orientation** - Draw horizontal (h) or vertical (v) (default: h)
7. **Starting Coordinates** - X, Y, Z coordinates where the image will start (default: 0, 64, 0)

### Example Session

```
============================================================
Minecraft Image Drawer using mcpylib
============================================================

Minecraft Server Connection:
Enter server IP (default: 127.0.0.1): 127.0.0.1
Enter server port (default: 65535): 65535
Enter authentication token: your_token_here
Connected to Minecraft server at 127.0.0.1:65535

Image Settings:
Enter image file path: my_image.png
Enter max size (width/height in blocks, default: 32): 50
Draw horizontal (h) or vertical (v)? (default: h): v

Starting Coordinates:
Enter X coordinate (default: 0): 100
Enter Y coordinate (default: 64): 64
Enter Z coordinate (default: 0): 200

============================================================
Drawing image vertically at (100, 64, 200)
Loaded image: 800x600 pixels
Resized to: 50x37 pixels
Successfully placed 1850 blocks vertically!
Image drawn at coordinates: (100, 64, 200) to (150, 101, 200)
============================================================

Done! Check your Minecraft world.
```

## Drawing Modes

### Horizontal Mode (h)
- Draws the image flat on the ground (XZ plane)
- Perfect for pixel art floors, maps, or ground decorations
- Y coordinate is constant (one layer thick)

### Vertical Mode (v)
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
├── main.py           # Main image drawer program
├── pyproject.toml    # Project dependencies
├── Documents.md      # mcpylib API documentation
└── README.md         # This file
```

## Advanced Algorithms

### Floyd-Steinberg Dithering
The program uses **Floyd-Steinberg error diffusion dithering** to create smooth color transitions:
- Distributes quantization error to neighboring pixels
- Creates smooth gradients instead of harsh color bands
- Prevents isolated white/colored pixels
- Results in more coherent, natural-looking images

### LAB Color Space Matching
Instead of simple RGB distance, the program uses **perceptually uniform LAB color space**:
- Matches how human eyes perceive color differences
- More accurate color selection
- Better handling of light/dark variations
- Scientifically proven to be more accurate than RGB

### Median Filtering
Applies a **3x3 median filter** to remove noise:
- Eliminates isolated single pixels
- Preserves edges and important details
- Creates more coherent color regions
- Reduces visual noise

## Requirements

- Python 3.11+
- mcpylib >= 1.0.0
- Pillow >= 10.0.0
- numpy >= 1.24.0
- scipy >= 1.11.0
- Minecraft server with mcpylib plugin installed

## License

See LICENSE file for details.
