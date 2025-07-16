#!/usr/bin/env python

import logging

import click

from sw_daemon import __version__
from sw_daemon.app import start


@click.command()
@click.help_option("--help", "-h")
@click.version_option(__version__, "--version", "-v", help="Show the installed version of sw.")
@click.option("--debug", "-d", is_flag=True, help="Enable debug logging.")
@click.argument("image_path", default=None, required=False, type=click.Path(exists=True))
def cli(debug=False, image_path=None):
    """sw-daemon - A daemon for managing wallpapers in Hyprland."""
    logging.basicConfig(
        level=logging.DEBUG if debug else logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
    )

    start(image_path)


if __name__ == "__main__":
    cli()
