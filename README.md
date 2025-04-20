# sw - Wallpaper Switching, Supercharged

**sw** is an overly complicated wallpaper switcher designed for
[Hyprland](https://github.com/hyprwm/Hyprland). Whether you prefer manually
curated queues, automated random selections, or systemd powered timers, `sw`
keeps your desktop fresh—on your terms.

## Installation

### From PackageCloud

sw can be installed in two ways: via PackageCloud or from source. The
PackageCloud repository hosts both the Python package (compatible with most
systems) and RPM packages for Red Hat-based systems like Fedora. This makes
using the PackageCloud repository the easiest and most versatile installation
option.

For more details and installation instructions, visit the sw repository on
PackageCloud: <https://packagecloud.io/AntonVanAssche/sw>

### From Source

1. Clone the repository:

  ```console
  git clone https://github.com/AntonVanAssche/sw.git
  cd jamjar
  ```

2. Set up a virtual environment:

  ```console
  python3 -m venv venv
  source venv/bin/activate  # For Linux/macOS
  ```

3. Install dependencies:

  ```console
  pip install -r requirements.txt
  ```

4. Build the package:

  ```console
  python -m build .
  ```

5. Install the package:

  ```console
  pip install dist/*.whl
  ```

## Usage

### General Command Structure

```console
$ sw --help
Usage: sw [OPTIONS] COMMAND [ARGS]...

  sw - An overly complicated wallpaper switcher for Hyprland.

Options:
  -s, --silent   Suppress output when necessary.
  -h, --help     Show this message and exit.
  -v, --version  Show the installed version of sw.

Commands:
  config   Manage the configuration of sw
  history  Manage wallpaper history
  next     Set the next wallpaper
  prev     Set the previous wallpaper in the queue
  queue    Manage the wallpaper queue
  set      Set a wallpaper from file or dir
  status   Show current wallpaper status
  timer    Manage the sw systemd timer
```

For more detailed information on each command, you can use the `--help`.

## Configuration

sw can be configured via a JSON file located at `~/.config/sw/config.json`.
Below is an example configuration:

```json
{
  "hyprpaper_config_file": "~/.config/hypr/hyprpaper.conf",
  "hyprlock_config_file": "~/.config/hypr/hyprlock.conf",
  "queue_file": "~/.cache/sw-queue",
  "history_file": "~/.cache/sw-history",
  "history_limit": 500,
  "recency_timeout": 28800,
  "recency_exclude": [
    "~/Pictures/Wallpapers/Cars/"
  ],
  "wallpaper_dir": "~/Pictures/Wallpapers/Nature/"
}
```

### Configuration Options

- `hyprpaper_config_file`: Path to the Hyprpaper configuration file.
- `hyprlock_config_file`: Path to the Hyprlock configuration file.
- `queue_file`: Path to the wallpaper queue file.
- `history_file`: Path to the wallpaper history file.
- `history_limit`: Maximum number of wallpapers to keep in history.
- `recency_timeout`: Time in seconds to consider a wallpaper recent.
- `recency_exclude`: List of directories to exclude from recency checks.
- `wallpaper_dir`: Directory containing wallpapers.

### Configuring sw

To configure sw, you can either manually edit the `config.json` file or use the
`config` command.

- To set a configuration option, you can run: `sw config set <option> <value>`.
- To get a configuration option, you can run: `sw config get <option>`.
- To view the current configuration, you can run: `sw config show`.
- To unset a configuration option, you can run: `sw config unset <option>`.

## Systemd Timer

sw is meant to be run in combination with a systemd user timer. This timer will
be responsible for running sw at regular intervals to change the wallpaper.
Below, you can find a systemd timer unit, and a service unit that can be used to
accomplish this.

### Service Unit

```console
$ systemctl --user cat sw.service
[Unit]
Description=Set a randeom wallpaper every few minutes

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
Description=Set a randeom wallpaper every few minutes
Requires=sw.service

[Timer]
OnBootSec=1m
OnUnitActiveSec=15m

[Install]
WantedBy=timers.target
```

### Managing the Timer

The following commands can be used to manage the systemd timer:

- Enable and start the timer: `sw timer enable`
- Disable and stop the timer: `sw timer disable`
- Check the timer status: `sw timer status`

## License

MIT © [Anton Van Assche](https://github.com/AntonVanAssche)
