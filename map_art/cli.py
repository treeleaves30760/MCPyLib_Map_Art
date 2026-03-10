import os
import sys

import click
from dotenv import load_dotenv

from map_art.drawer import MinecraftImageDrawer

load_dotenv()


@click.command()
@click.argument('image_path', type=click.Path(exists=True))
@click.option('--ip', default=None, help='Minecraft server IP (env: SERVER_IP)')
@click.option('--port', default=None, type=int, help='Minecraft server port (env: SERVER_PORT)')
@click.option('--token', default=None, help='MCPyLib authentication token (env: SERVER_TOKEN)')
@click.option('--player', default="NightTangerine", help='Player name to get position from')
@click.option('--size', default=512, type=int, help='Maximum image size in blocks')
@click.option('--colors', default=61, type=int, help='Number of colors to use (k-means clusters)')
@click.option('--mode', type=click.Choice(['flat', '3d', 'vertical'], case_sensitive=False),
              default='flat', help='Drawing mode: flat (2D horizontal), 3d (3D staircase), or vertical')
@click.option('--x', default=None, type=int, help='Starting X coordinate (overrides player position)')
@click.option('--y', default=None, type=int, help='Starting Y coordinate (overrides player position)')
@click.option('--z', default=None, type=int, help='Starting Z coordinate (overrides player position)')
def cli(image_path, ip, port, token, player, size, colors, mode, x, y, z):
    """MCPyLib Map Art - Create Minecraft map art from images

    Example usage:

        mcpylib-map-art image.jpg

        mcpylib-map-art image.jpg --mode 3d --size 256

        mcpylib-map-art image.jpg --ip 192.168.1.100 --port 25565
    """
    print("=" * 60)
    print("MCPyLib Map Art - Modern Map Art Algorithm")
    print("=" * 60)

    server_ip = ip or os.getenv('SERVER_IP', '127.0.0.1')
    server_port = port or int(os.getenv('SERVER_PORT', '65535'))
    server_token = token or os.getenv('SERVER_TOKEN', '')

    if not server_token:
        click.echo("Error: No authentication token provided!", err=True)
        click.echo(
            "Set SERVER_TOKEN environment variable or use --token option", err=True)
        sys.exit(1)

    print(f"\nConnecting to server: {server_ip}:{server_port}")
    drawer = MinecraftImageDrawer(
        ip=server_ip, port=server_port, token=server_token)

    if x is not None and y is not None and z is not None:
        start_x, start_y, start_z = x, y, z
        print(f"Using specified coordinates: ({start_x}, {start_y}, {start_z})")
    else:
        try:
            start_x, start_y, start_z = drawer.mc.getPos(player)
            print(f"Using {player}'s position: ({start_x}, {start_y}, {start_z})")
        except Exception as e:
            click.echo(f"Error: Could not get player position: {e}", err=True)
            click.echo(
                "Use --x, --y, --z options to specify coordinates manually", err=True)
            sys.exit(1)

    print(f"\nImage: {image_path}")
    print(f"Max size: {size} blocks")
    print(f"Colors: {colors}")
    print(f"Mode: {mode}")

    if mode == 'vertical':
        drawer.draw_vertical(image_path, size, start_x,
                             start_y, start_z, num_colors=colors)
    elif mode == '3d':
        print("\nUsing 3D mode with full height range!")
        drawer.draw_horizontal_3d(
            image_path, size, start_x, start_z, num_colors=colors)
    else:
        print("\nUsing flat 2D mode!")
        drawer.draw_horizontal(image_path, size, start_x,
                               start_y, start_z, num_colors=colors)

    print("\nDone! Check your Minecraft world.")
