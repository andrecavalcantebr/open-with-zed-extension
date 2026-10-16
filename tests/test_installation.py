# Copyright (C) 2026 Andre Cavalcante
# SPDX-License-Identifier: GPL-3.0-only
# See LICENSE for the full license text and warranty disclaimer.

import os
from pathlib import Path
import subprocess
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]


class InstallationTests(unittest.TestCase):
    def run_script(self, name, env, cwd, check=True):
        return subprocess.run(
            ["sh", str(ROOT / "scripts" / name)],
            env=env, cwd=cwd, check=check, capture_output=True, text=True,
        )

    def test_install_update_and_uninstall(self):
        for custom_data_home in (False, True):
            with self.subTest(custom_data_home=custom_data_home):
                with tempfile.TemporaryDirectory(prefix="zed install ") as directory:
                    home = Path(directory)
                    env = dict(os.environ, HOME=str(home))
                    env.pop("XDG_DATA_HOME", None)
                    data_home = home / ".local/share"
                    if custom_data_home:
                        data_home = home / "custom data"
                        env["XDG_DATA_HOME"] = str(data_home)
                    extensions = data_home / "nautilus-python/extensions"
                    extensions.mkdir(parents=True)
                    unrelated = extensions / "vscode_nautilus.py"
                    unrelated.write_text("# keep me\n")
                    destination = extensions / "zed_nautilus.py"
                    destination.write_text("# old version\n")

                    for _ in range(2):
                        self.run_script("install.sh", env, directory)
                        self.assertEqual(destination.read_bytes(), (ROOT / "zed_nautilus.py").read_bytes())
                        self.assertEqual(destination.stat().st_mode & 0o777, 0o644)
                    for _ in range(2):
                        self.run_script("uninstall.sh", env, directory)
                        self.assertFalse(destination.exists())
                        self.assertEqual(unrelated.read_text(), "# keep me\n")

    def test_relative_data_home_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            env = dict(os.environ, HOME=directory, XDG_DATA_HOME="relative")
            for script in ("install.sh", "uninstall.sh"):
                result = self.run_script(script, env, directory, check=False)
                self.assertNotEqual(result.returncode, 0)
                self.assertIn("absolute path", result.stderr)
            self.assertFalse((Path(directory) / "relative").exists())
