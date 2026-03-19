"""Map art simulator — preview and analyse results without a Minecraft server.

Usage:
    python -m map_art.simulator photo.jpg
    python -m map_art.simulator photo.jpg --size 128 --output-dir output
"""

import os
import sys

import click
import numpy as np
from PIL import Image, ImageDraw, ImageFont

from map_art.colors import MapPalette, compute_staircase_heights, SHADE_HEIGHT_DELTA
from map_art.image import load_and_resize


# ------------------------------------------------------------------
# Metrics
# ------------------------------------------------------------------

def compute_psnr(img1, img2):
    """Peak Signal-to-Noise Ratio (dB).  Higher = better."""
    mse = np.mean((img1.astype(np.float64) - img2.astype(np.float64)) ** 2)
    if mse == 0:
        return float("inf")
    return 10.0 * np.log10(255.0 ** 2 / mse)


def compute_ssim(img1, img2, window=7):
    """Simplified per-channel SSIM averaged over R/G/B.  Range [0, 1]."""
    try:
        from scipy.ndimage import uniform_filter
    except ImportError:
        return float("nan")

    C1 = (0.01 * 255) ** 2
    C2 = (0.03 * 255) ** 2
    a = img1.astype(np.float64)
    b = img2.astype(np.float64)

    vals = []
    for c in range(3):
        mu1 = uniform_filter(a[:, :, c], size=window)
        mu2 = uniform_filter(b[:, :, c], size=window)
        s1 = np.maximum(uniform_filter(a[:, :, c] ** 2, size=window) - mu1 ** 2, 0)
        s2 = np.maximum(uniform_filter(b[:, :, c] ** 2, size=window) - mu2 ** 2, 0)
        s12 = uniform_filter(a[:, :, c] * b[:, :, c], size=window) - mu1 * mu2
        num = (2 * mu1 * mu2 + C1) * (2 * s12 + C2)
        den = (mu1 ** 2 + mu2 ** 2 + C1) * (s1 + s2 + C2)
        vals.append(np.mean(num / den))
    return float(np.mean(vals))


def compute_mean_error(img1, img2):
    """Mean Euclidean RGB distance per pixel."""
    diff = img1.astype(np.float64) - img2.astype(np.float64)
    return float(np.mean(np.sqrt(np.sum(diff ** 2, axis=2))))


# ------------------------------------------------------------------
# Error heatmap
# ------------------------------------------------------------------

def error_heatmap(img1, img2):
    """Generate a blue->red heatmap of per-pixel colour error."""
    diff = np.sqrt(np.sum(
        (img1.astype(np.float64) - img2.astype(np.float64)) ** 2, axis=2
    ))
    # Normalise to 0..1  (max possible error = sqrt(3)*255 ~ 441)
    norm = np.clip(diff / 120.0, 0, 1)  # 120 gives a useful visual range

    hm = np.zeros((*norm.shape, 3), dtype=np.uint8)
    hm[:, :, 0] = (norm * 255).astype(np.uint8)          # red channel
    hm[:, :, 2] = ((1 - norm) * 255).astype(np.uint8)    # blue channel
    return hm


# ------------------------------------------------------------------
# Staircase height-map visualisation
# ------------------------------------------------------------------

def height_map_image(shade_map):
    """Render staircase heights as a greyscale image."""
    heights, _ = compute_staircase_heights(shade_map)
    H = len(heights)
    W = len(heights[0]) if H else 0
    arr = np.array(heights, dtype=np.float64)
    lo, hi = arr.min(), arr.max()
    if hi == lo:
        hi = lo + 1
    norm = ((arr - lo) / (hi - lo) * 255).astype(np.uint8)
    return np.stack([norm, norm, norm], axis=2)


# ------------------------------------------------------------------
# Comparison canvas
# ------------------------------------------------------------------

def _label(draw, x, y, text, font):
    draw.text((x, y), text, fill=(255, 255, 255), font=font)


def create_comparison(original, results, output_path):
    """Build a combined comparison image.

    results: list of (label, simulated_img_array) tuples
    """
    H, W = original.shape[:2]
    n = 1 + len(results)
    pad = 4
    lbl_h = 20
    cell_w = W
    cell_h = H

    total_w = n * cell_w + (n + 1) * pad
    total_h = 2 * (cell_h + lbl_h) + 3 * pad  # two rows: sim + error

    canvas = Image.new("RGB", (total_w, total_h), (30, 30, 30))
    draw = ImageDraw.Draw(canvas)

    try:
        font = ImageFont.truetype("arial.ttf", 14)
    except (OSError, IOError):
        font = ImageFont.load_default()

    def paste(arr, col, row):
        img = Image.fromarray(arr).resize((cell_w, cell_h), Image.NEAREST)
        cx = pad + col * (cell_w + pad)
        cy = pad + lbl_h + row * (cell_h + lbl_h + pad)
        canvas.paste(img, (cx, cy))

    def label(text, col, row):
        cx = pad + col * (cell_w + pad)
        cy = pad + row * (cell_h + lbl_h + pad)
        _label(draw, cx, cy, text, font)

    # Original
    label("Original", 0, 0)
    paste(original, 0, 0)
    label("(reference)", 0, 1)
    paste(original, 0, 1)

    for i, (name, sim_arr) in enumerate(results, start=1):
        label(name, i, 0)
        paste(sim_arr, i, 0)

        label(f"{name} error", i, 1)
        paste(error_heatmap(original, sim_arr), i, 1)

    canvas.save(output_path)
    print(f"  Saved comparison -> {output_path}")


# ------------------------------------------------------------------
# Core simulation driver
# ------------------------------------------------------------------

def simulate(image_path, size=128, output_dir="output"):
    """Run all four algorithm variants and produce comparison outputs."""
    os.makedirs(output_dir, exist_ok=True)
    base = os.path.splitext(os.path.basename(image_path))[0]

    img = load_and_resize(image_path, size)
    width, height = img.size
    img_array = np.array(img)

    # Save resized original
    orig_path = os.path.join(output_dir, f"{base}_original.png")
    img.save(orig_path)
    print(f"  Saved original -> {orig_path}")

    results = []    # (label, simulated_array)
    metrics = []    # (label, psnr, ssim, mean_err, n_colours)

    configs = [
        ("Flat",              "flat",      False),
        ("Flat+Dither",       "flat",      True),
        ("Staircase",         "staircase", False),
        ("Staircase+Dither",  "staircase", True),
    ]

    for label, mode, dither in configs:
        print(f"\n--- {label} ---")
        palette = MapPalette(mode=mode)
        print(f"  Palette: {len(palette.entries)} colours")

        if dither:
            idx_map = palette.dither_pixels(img_array)
        else:
            idx_map = palette.match_pixels(img_array)

        sim_img = palette.indices_to_image(idx_map)

        # Save individual result
        out_path = os.path.join(output_dir, f"{base}_{label.lower().replace('+','_')}.png")
        Image.fromarray(sim_img).save(out_path)
        print(f"  Saved -> {out_path}")

        # If staircase, also save height map
        if mode == "staircase":
            shade_map = palette.indices_to_shades(idx_map)
            hm = height_map_image(shade_map)
            hm_path = os.path.join(output_dir, f"{base}_{label.lower().replace('+','_')}_heightmap.png")
            Image.fromarray(hm).save(hm_path)
            print(f"  Saved height map -> {hm_path}")

        # Metrics
        psnr = compute_psnr(img_array, sim_img)
        ssim = compute_ssim(img_array, sim_img)
        merr = compute_mean_error(img_array, sim_img)
        unique = len(set(map(tuple, sim_img.reshape(-1, 3).tolist())))
        metrics.append((label, psnr, ssim, merr, unique))
        results.append((label, sim_img))

    # Comparison image
    comp_path = os.path.join(output_dir, f"{base}_comparison.png")
    create_comparison(img_array, results, comp_path)

    # Print metrics table
    print(f"\n{'='*72}")
    print(f"{'Mode':<22} {'PSNR (dB)':>10} {'SSIM':>8} {'Mean Err':>10} {'Colours':>8}")
    print(f"{'-'*72}")
    for label, psnr, ssim, merr, nc in metrics:
        psnr_s = f"{psnr:.2f}" if psnr != float("inf") else "inf"
        ssim_s = f"{ssim:.4f}" if not np.isnan(ssim) else "n/a"
        print(f"{label:<22} {psnr_s:>10} {ssim_s:>8} {merr:>10.2f} {nc:>8}")
    print(f"{'='*72}")

    # Save metrics text
    metrics_path = os.path.join(output_dir, f"{base}_metrics.txt")
    with open(metrics_path, "w", encoding="utf-8") as f:
        f.write(f"Image: {image_path}\n")
        f.write(f"Size:  {width} x {height}\n\n")
        f.write(f"{'Mode':<22} {'PSNR (dB)':>10} {'SSIM':>8} {'Mean Err':>10} {'Colours':>8}\n")
        f.write(f"{'-'*72}\n")
        for label, psnr, ssim, merr, nc in metrics:
            psnr_s = f"{psnr:.2f}" if psnr != float("inf") else "inf"
            ssim_s = f"{ssim:.4f}" if not np.isnan(ssim) else "n/a"
            f.write(f"{label:<22} {psnr_s:>10} {ssim_s:>8} {merr:>10.2f} {nc:>8}\n")
    print(f"\nMetrics saved -> {metrics_path}")


# ------------------------------------------------------------------
# CLI
# ------------------------------------------------------------------

@click.command("simulate")
@click.argument("image_path", type=click.Path(exists=True))
@click.option("--size", default=128, type=int,
              help="Max image size in pixels (default 128 = one map)")
@click.option("--output-dir", default="output",
              help="Directory for output files (default: output/)")
def main(image_path, size, output_dir):
    """Simulate Minecraft map art and compare with the original image."""
    print("=" * 60)
    print("Map Art Simulator")
    print("=" * 60)
    simulate(image_path, size=size, output_dir=output_dir)
    print("\nDone!")


if __name__ == "__main__":
    main()
