# Open with Zed for Nautilus

A Python extension that adds **Open with Zed** to the Nautilus (Files) context
menu. It supports files, folders, multiple selected items, and the empty area
inside a folder.

## Compatibility

This extension targets **Nautilus with extension API 4.0**, rather than a specific
Linux distribution. It should work on other distributions with the required
dependencies and executable path, but those environments have not been tested.
It does not integrate with Dolphin, Thunar, Nemo, or other file managers.

The original environment is Zorin OS with GNOME, Nautilus 46.4, and
`python3-nautilus` 4.0. Automated validation uses the real Nautilus API;
visual confirmation of the context menu is still pending.

## Requirements

- Nautilus with extension API 4.0 and the matching nautilus-python bindings.
- Python 3, PyGObject, and the Nautilus 4.0 introspection typelib.
- An executable Zed installation at `~/.local/bin/zed` (a symlink is supported).
- For the installation scripts: a POSIX shell and GNU core utilities.

On Zorin OS/Ubuntu, install missing dependencies with:

```sh
sudo apt install python3-gi python3-nautilus gir1.2-nautilus-4.0
```

Package names and installation commands may differ on other distributions.
The extension currently uses a fixed Zed path and does not search `PATH`.
In the original environment, `~/.local/bin/zed` points to
`~/.local/zed.app/bin/zed`. If your installation uses another location, provide
a symlink at `~/.local/bin/zed` or adjust the executable path in `zed_nautilus.py`.

## Install or update

From the project root, run as your regular user, without `sudo`:

```sh
./scripts/install.sh
nautilus -q
```

Open Files again. The `nautilus -q` command closes Nautilus windows so the
extension can be loaded the next time the application starts.

The installer copies `zed_nautilus.py` to
`${XDG_DATA_HOME:-$HOME/.local/share}/nautilus-python/extensions/`, following
the [GNOME extension directory documentation](https://gnome.pages.gitlab.gnome.org/nautilus-python/nautilus-python-overview.html).
By default, the destination is
`~/.local/share/nautilus-python/extensions/zed_nautilus.py`.

Installing again replaces the previous `zed_nautilus.py`; save any changes to
the installed copy before updating. The installed file is independent of the
project: after editing the source, run the installer and restart Nautilus again.
The installer only updates this file, so the VS Code extension can coexist with it.

## Uninstall

```sh
./scripts/uninstall.sh
nautilus -q
```

Open Files again. Uninstalling removes only `zed_nautilus.py` from your user
extension directory. If you customized `XDG_DATA_HOME`, use the same value as
during installation. The project and the Zed application are retained.

## Behavior

- The entire selection opens in a new window using `zed --new -- <paths>`.
- Paths containing spaces or shell characters are passed as separate arguments
  using `subprocess.Popen` without a shell and with `start_new_session=True`.
- The working directory is the first selected item if it is a folder, or the
  parent directory of the first selected file.
- The menu is hidden if `~/.local/bin/zed` is not executable or any selected item
  has no local path representation, such as a remote URI without a local path.
- Menu text is in English.

## Validation

Run the tests with the system Python, which has access to the GI packages:

```sh
/usr/bin/python3 -m unittest discover -s tests -v
```

Tests load the real Nautilus API, check menu creation, and mock process creation
to verify Zed arguments and working directories. Installation and uninstallation
run in temporary directories, including paths with spaces, without modifying
your personal installation.

Visual confirmation is still pending. To check it manually:

1. Install the extension, quit Nautilus, and open Files again.
2. Check the context menu for a file, a folder, and the empty area inside a folder.
3. Select multiple items, including names with spaces, and choose **Open with Zed**.
4. Confirm that a new Zed window receives the selected items.

## Troubleshooting

If the menu does not appear, check the executable and the API import:

```sh
test -x "$HOME/.local/bin/zed" && "$HOME/.local/bin/zed" --version
/usr/bin/python3 -c 'import gi; gi.require_version("Nautilus", "4.0"); from gi.repository import Nautilus'
```

Also check that the installed copy is in the extension directory used by your
session, all selected items have local paths, and Nautilus has been restarted.
Python virtual environments may not expose the system `gi` module.

## Project layout

```text
zed_nautilus.py        Extension loaded by Nautilus
scripts/install.sh    Per-user installation and updates
scripts/uninstall.sh  Per-user removal
tests/                Automated tests
```

The initial source was imported from an existing local extension and its menu
text was translated into English. API reference:
[nautilus-python documentation](https://gnome.pages.gitlab.gnome.org/nautilus-python/).

## License

Copyright (C) 2026 Andre Cavalcante.

This project is licensed under the GNU General Public License, version 3 only
(`GPL-3.0-only`). See [LICENSE](LICENSE) for the full text.

This program is distributed without any warranty; without even the implied
warranty of merchantability or fitness for a particular purpose.
