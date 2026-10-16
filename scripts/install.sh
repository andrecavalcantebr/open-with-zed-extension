#!/bin/sh
# Copyright (C) 2026 Andre Cavalcante
# SPDX-License-Identifier: GPL-3.0-only
# See LICENSE for the full license text and warranty disclaimer.

set -eu

project_dir=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
data_home=${XDG_DATA_HOME:-"$HOME/.local/share"}
case "$data_home" in
    /*) ;;
    *) printf '%s\n' 'XDG_DATA_HOME must be an absolute path.' >&2; exit 1 ;;
esac
destination="$data_home/nautilus-python/extensions/zed_nautilus.py"

install -D -m 644 -- "$project_dir/zed_nautilus.py" "$destination"
printf 'Extension installed at %s\n' "$destination"
printf '%s\n' 'Run nautilus -q and open Files again.'
