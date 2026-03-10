import os
import sys

import numpy as np
from PIL import Image
from sklearn.cluster import KMeans

from map_art.colors import get_closest_block


def load_and_resize(image_path, max_size):
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


def quantize_with_kmeans(img_array, num_colors=35):
    """Modern Minecraft map art algorithm: k-means color quantization

    1. Find the N most important colors in the image using k-means
    2. Map those to closest Minecraft blocks
    3. Replace all pixels with their cluster's Minecraft color
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
        block, mc_color = get_closest_block(rgb)
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
