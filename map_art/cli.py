"""CLI entry-point for MCPyLib Map Art."""

import os
import sys

import click
from dotenv import load_dotenv

load_dotenv()


@click.group(invoke_without_command=True)
@click.pass_context
def cli(ctx):
    """MCPyLib Map Art - Create Minecraft map art from images.

    \b
    Commands:
      draw      Draw map art on a Minecraft server
      simulate  Preview / analyse map art without a server
    """
    if ctx.invoked_subcommand is None:
        click.echo(ctx.get_help())


# ------------------------------------------------------------------
# draw
# ------------------------------------------------------------------

@cli.command()
@click.argument("image_path", type=click.Path(exists=True))
@click.option("--ip", default=None, help="Server IP  (env: SERVER_IP)")
@click.option("--port", default=None, type=int, help="Server port  (env: SERVER_PORT)")
@click.option("--token", default=None, help="Auth token  (env: SERVER_TOKEN)")
@click.option("--player", default="NightTangerine", help="Player name for position")
@click.option("--size", default=128, type=int, help="Max image size in blocks")
@click.option("--mode",
              type=click.Choice(["flat", "staircase", "vertical"], case_sensitive=False),
              default="flat", help="Drawing mode")
@click.option("--dither", is_flag=True, help="Enable Floyd-Steinberg dithering")
@click.option("--x", default=None, type=int, help="Start X (overrides player pos)")
@click.option("--y", default=None, type=int, help="Start Y (overrides player pos)")
@click.option("--z", default=None, type=int, help="Start Z (overrides player pos)")
def draw(image_path, ip, port, token, player, size, mode, dither, x, y, z):
    """Draw map art on a Minecraft server.

    \b
    Examples:
      mcpylib-map-art draw photo.jpg
      mcpylib-map-art draw photo.jpg --mode staircase --dither
      mcpylib-map-art draw photo.jpg --mode staircase --dither --size 128
    """
    from map_art.drawer import MinecraftImageDrawer

    print("=" * 60)
    print("MCPyLib Map Art")
    print("=" * 60)

    server_ip = ip or os.getenv("SERVER_IP", "127.0.0.1")
    server_port = port or int(os.getenv("SERVER_PORT", "65535"))
    server_token = token or os.getenv("SERVER_TOKEN", "")

    if not server_token:
        click.echo("Error: No authentication token provided!", err=True)
        click.echo("Set SERVER_TOKEN env var or use --token", err=True)
        sys.exit(1)

    print(f"\nConnecting to {server_ip}:{server_port}")
    drawer = MinecraftImageDrawer(ip=server_ip, port=server_port, token=server_token)

    if x is not None and y is not None and z is not None:
        sx, sy, sz = x, y, z
        print(f"Coordinates: ({sx}, {sy}, {sz})")
    else:
        try:
            sx, sy, sz = drawer.mc.getPos(player)
            print(f"Player {player} position: ({sx}, {sy}, {sz})")
        except Exception as e:
            click.echo(f"Error getting player position: {e}", err=True)
            click.echo("Use --x --y --z to specify coordinates", err=True)
            sys.exit(1)

    print(f"\nImage: {image_path}")
    print(f"Size:  {size}   Mode: {mode}   Dither: {dither}")

    if mode == "vertical":
        drawer.draw_vertical(image_path, size, sx, sy, sz)
    elif mode == "staircase":
        drawer.draw_staircase(image_path, size, sx, sz, dither=dither)
    else:
        drawer.draw_flat(image_path, size, sx, sy, sz, dither=dither)

    print("\nDone! Check your Minecraft world.")


# ------------------------------------------------------------------
# simulate
# ------------------------------------------------------------------

@cli.command()
@click.argument("image_path", type=click.Path(exists=True))
@click.option("--size", default=128, type=int,
              help="Max image size in pixels (default 128 = one map)")
@click.option("--output-dir", default="output",
              help="Output directory (default: output/)")
def simulate(image_path, size, output_dir):
    """Simulate map art and compare with the original image (no server needed)."""
    from map_art.simulator import simulate as run_sim

    print("=" * 60)
    print("Map Art Simulator")
    print("=" * 60)
    run_sim(image_path, size=size, output_dir=output_dir)
    print("\nDone!")
