# Copyright (C) 2026 Andre Cavalcante
# SPDX-License-Identifier: GPL-3.0-only
# See LICENSE for the full license text and warranty disclaimer.

"""Add an Open with Zed action to Nautilus 4 context menus."""

import os
import subprocess

import gi

gi.require_version("Nautilus", "4.0")
from gi.repository import GObject, Nautilus


class ZedExtension(GObject.GObject, Nautilus.MenuProvider):
    def _menu_items(self, files, action):
        executable = os.path.expanduser("~/.local/bin/zed")
        if not files or not os.access(executable, os.X_OK):
            return []

        paths = [file.get_location().get_path() for file in files]
        if any(path is None for path in paths):
            return []

        item = Nautilus.MenuItem(
            name="ZedExtension::" + action,
            label="Open with Zed",
            tip="Open files or folders in Zed",
        )
        item.connect("activate", self._launch, executable, paths)
        return [item]

    def _launch(self, item, executable, paths):
        work_dir = paths[0] if os.path.isdir(paths[0]) else os.path.dirname(paths[0])
        subprocess.Popen(
            [executable, "--new", "--", *paths],
            cwd=work_dir,
            start_new_session=True,
        )

    def get_file_items(self, files):
        return self._menu_items(files, "OpenSelection")

    def get_background_items(self, current_folder):
        return self._menu_items([current_folder], "OpenFolder")
