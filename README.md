# sw - Wallpaper Switching, Supercharged

**sw** is an overly complicated wallpaper switcher designed for
[Hyprland](https://github.com/hyprwm/Hyprland). Whether you prefer manually
curated queues, automated random selections, or systemd powered timers, **sw**
keeps your desktop fresh—on your terms.

## Installation

You can install **sw** either via **PackageCloud** or **from source**.

### From PackageCloud (Recommended)

The PackageCloud repository hosts both:

- A universal Python package
- RPM packages for Red Hat-based systems like Fedora

This makes PackageCloud the easiest and most flexible way to install **sw**.

View on PackageCloud: [AntonVanAssche/sw](https://packagecloud.io/AntonVanAssche/sw)

### From Source

```console
# Clone the repo
git clone https://github.com/AntonVanAssche/sw.git
cd sw

# Set up virtual environment
python -m venv venv
. ./venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Build the package
python -m build .

# Install the package
pip install dist/*.whl
```

## How It Works

**sw** has two components:

- Daemon (sw-daemon): Keeps your wallpaper displayed and ready to change. It
  exposes a socket for real-time communication.
- CLI (sw): Handles queueing, history, favorites, config management, and
  actually telling the daemon what to do.

## Usage

### Daemon Help

```console
$ sw-daemon --help
Usage: sw-daemon [OPTIONS] [IMAGE_PATH]

  sw-daemon - A daemon for managing wallpapers in Hyprland.

Options:
  -h, --help     Show this message and exit.
  -v, --version  Show the installed version of sw.
  -d, --debug    Enable debug logging.
```

### CLI Help

```console
$ sw --help
Usage: sw [OPTIONS] COMMAND [ARGS]...

  sw - An overly complicated wallpaper switcher for Hyprland.

Options:
  -s, --silent                    Suppress output when necessary.
  -c, --color [auto|never|always]
                                  Control colored output: auto, never, or
                                  always.
  -n, --notify                    Send notifications for actions.
  -h, --help                      Show this message and exit.
  -v, --version                   Show the installed version of sw.

Commands:
  config    Manage the configuration of sw
  favorite  Manage favorite wallpapers
  history   Manage wallpaper history
  next      Set the next wallpaper
  prev      Set the previous wallpaper
  queue     Manage the wallpaper queue
  set       Set a wallpaper
  status    Show current wallpaper status
  timer     Manage the sw systemd timer
```

For more detailed information on each command, you can use the `--help`.

## Configuration

Your main configuration file is located at: `~/.config/sw/config.json`

### Example Configuration

```json
{
  "wallpaper": {
    "directory": "~/Pictures/Wallpapers",
    "favorites": [
      "~/Pictures/Wallpapers/Nature/Sunset.jpg",
      "~/Pictures/Wallpapers/Nature/Beach.jpg"
    ],
    "recency": {
      "exclude": [
        "~/Pictures/Wallpapers/Cars/"
      ],
      "timeout": 28800
    }
  },
  "hyprlock": {
    "config": "~/.config/hypr/hyprlock.conf"
  },
  "history": {
    "file": "~/.cache/sw-history",
    "limit": 500
  },
  "queue": {
    "file": "~/.cache/sw-queue"
  },
  "daemon": {
    "socket_path": "/tmp/sw-daemon.sock"
  }
}
```

### Config Options Explained

| Option | Description |
| --- | --- |
| `wallpaper.directory` | Path to your wallpaper folder |
| `wallpaper.favorites` | List of favorite wallpapers |
| `wallpaper.recency.exclude` | Directories to exclude from recency checks |
| `wallpaper.recency.timeout` | Time (seconds) to consider a wallpaper recent |
| `hyprlock.config` | Path to your Hyprlock config |
| `history.file` | Where wallpaper history is stored |
| `history.limit` | Max number of wallpapers to remember |
| `queue.file` | Path to queue file |
| `daemon.socket_path` | Socket used by the daemon |

### Using the CLI to Configure

```console
sw config set <option> <value>     # Set a config option
sw config get <option>             # Get the value of a config option
sw config show                     # Show full config
sw config unset <option>           # Remove a config option
```

## Systemd Timer

**sw** is designed to work with a user-level systemd timer to automate wallpaper
changes.

### Service Unit

```console
$ systemctl --user cat sw.service
[Unit]
Description=Set a random wallpaper every few minutes

[Service]
Type=oneshot
ExecStart=hyprctl --instance 0 dispatch exec "sw --silent set --use-dir"
StandardOutput=journal

[Install]
WantedBy=graphical.target
```

### Timer Unit

```console
$ systemctl --user cat sw.timer
[Unit]
Description=Set a random wallpaper every few minutes
Requires=sw.service

[Timer]
OnBootSec=1m
OnUnitActiveSec=15m

[Install]
WantedBy=timers.target
```

### Timer Management via CLI

```console
sw timer start      # Start the systemd timer
sw timer stop       # Stop the systemd timer
sw timer enable     # Enable and start timer, use --now to start immediately
sw timer disable    # Stop and disable timer, use --now to stop immediately
sw timer status     # View timer status
```

## License

MIT © [Anton Van Assche](https://github.com/AntonVanAssche)
