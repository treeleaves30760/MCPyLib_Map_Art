"""Image loading and preprocessing for map art."""

import os
import sys

from PIL import Image


def load_and_resize(image_path, max_size):
    """Load an image and resize so the longest side <= max_size.

    Returns a PIL Image in RGB mode.
    """
    if not os.path.exists(image_path):
        print(f"Error: Image not found: {image_path}")
        sys.exit(1)

    try:
        img = Image.open(image_path)
        print(f"Loaded: {img.size[0]}x{img.size[1]} pixels")

        if img.mode != "RGB":
            img = img.convert("RGB")

        img.thumbnail((max_size, max_size), Image.Resampling.LANCZOS)
        print(f"Resized: {img.size[0]}x{img.size[1]} pixels")
        return img
    except Exception as e:
        print(f"Error loading image: {e}")
        sys.exit(1)
