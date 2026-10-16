# Copyright (C) 2026 Andre Cavalcante
# SPDX-License-Identifier: GPL-3.0-only
# See LICENSE for the full license text and warranty disclaimer.

import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import zed_nautilus
from gi.repository import Gio, Nautilus


class FileInfo:
    """Supply the location that Nautilus normally passes to the provider."""

    def __init__(self, location):
        self.location = location

    def get_location(self):
        return self.location


class ExtensionTests(unittest.TestCase):
    def setUp(self):
        self.extension = zed_nautilus.ZedExtension()
        self.access = patch("zed_nautilus.os.access", return_value=True)
        self.access.start()
        self.addCleanup(self.access.stop)

    def local(self, path):
        return FileInfo(Gio.File.new_for_path(str(path)))

    def test_selection_menu_uses_real_nautilus_item(self):
        items = self.extension.get_file_items([self.local("/tmp/example")])
        self.assertEqual(len(items), 1)
        self.assertIsInstance(items[0], Nautilus.MenuItem)
        self.assertEqual(items[0].props.label, "Open with Zed")
        self.assertEqual(items[0].props.name, "ZedExtension::OpenSelection")

    def test_empty_selection_is_hidden(self):
        self.assertEqual(self.extension.get_file_items([]), [])

    def test_missing_executable_hides_both_menus(self):
        with patch("zed_nautilus.os.access", return_value=False):
            self.assertEqual(self.extension.get_file_items([self.local("/tmp")]), [])
            self.assertEqual(self.extension.get_background_items(self.local("/tmp")), [])

    def test_mixed_remote_selection_is_hidden(self):
        remote = FileInfo(Gio.File.new_for_uri("sftp://example.com/file"))
        self.assertEqual(self.extension.get_file_items([self.local("/tmp"), remote]), [])
        self.assertEqual(self.extension.get_background_items(remote), [])

    @patch("zed_nautilus.subprocess.Popen")
    def test_activation_preserves_multiple_paths_and_special_characters(self, popen):
        with tempfile.TemporaryDirectory() as directory:
            paths = [str(Path(directory) / name) for name in ("a b.txt", "-$(example);.txt")]
            for path in paths:
                Path(path).touch()
            item = self.extension.get_file_items([self.local(path) for path in paths])[0]
            item.activate()
            popen.assert_called_once_with(
                [str(Path.home() / ".local/bin/zed"), "--new", "--", *paths],
                cwd=directory,
                start_new_session=True,
            )

    @patch("zed_nautilus.subprocess.Popen")
    def test_background_opens_folder_as_working_directory(self, popen):
        with tempfile.TemporaryDirectory(prefix="zed folder ") as directory:
            item = self.extension.get_background_items(self.local(directory))[0]
            self.assertEqual(item.props.name, "ZedExtension::OpenFolder")
            item.activate()
            popen.assert_called_once_with(
                [str(Path.home() / ".local/bin/zed"), "--new", "--", directory],
                cwd=directory,
                start_new_session=True,
            )
