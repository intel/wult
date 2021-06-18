#!/bin/sh -euf
#
# -*- coding: utf-8 -*-
# vim: ts=4 sw=4 tw=100 et ai si
#
# Copyright (C) 2014-2021 Intel Corporation
# SPDX-License-Identifier: BSD-3-Clause
#
# Author: Artem Bityutskiy <artem.bityutskiy@linux.intel.com>

# Create a stand-alone version of 'stats-collect' and 'ipmi-helper' tools.

TOOLS="stats-collect ipmi-helper"
MODULES_DIR="wultlibs/helperlibs"

# Remove all temporary files.
remove_tmpfiles() {
    rm -rf ${MODULES_DIR%%/*}
    rm -f __main__.py
    for toolname in $TOOLS; do
        rm -f $toolname.zip
    done
}

remove_tmpfiles

if [ "${1:-}" = "clean" ]; then
    for toolname in $TOOLS; do
        rm -f $toolname.standalone
    done
    exit 0
fi

for toolname in $TOOLS; do
    mkdir -p "$MODULES_DIR"
    toolpath="$(which $toolname)"
    deps="$($toolpath --print-module-paths)"

    for dep in $deps; do
        cp "$dep" "$MODULES_DIR"
        cp "$toolpath" __main__.py

        # Zip the tool and all its dependencies.
        python3 -m zipfile -c $toolname.zip __main__.py ${MODULES_DIR%%/*}

        # Turn it into an executable file.
        echo '#!/usr/bin/python3' > "$toolname".standalone
        cat "$toolname".zip >> "$toolname".standalone
        chmod a+x "$toolname".standalone
    done

	remove_tmpfiles
done
