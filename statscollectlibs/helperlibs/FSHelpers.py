# -*- coding: utf-8 -*-
# vim: ts=4 sw=4 tw=100 et ai si
#
# Copyright (C) 2020-2022 Intel Corporation
# SPDX-License-Identifier: BSD-3-Clause
#
# Author: Artem Bityutskiy <artem.bityutskiy@linux.intel.com>

"""
This module contains misc. helper functions related to file-system operations.
"""

import os
import stat
import shutil
from pathlib import Path
from pepclibs.helperlibs.Exceptions import ErrorExists

# pylint: disable=wildcard-import,unused-wildcard-import
from pepclibs.helperlibs.FSHelpers import *

def set_default_perm(path):
    """
    Set access mode for a 'path'. Mode is 666 for file and 777 for directory, and current umask
    value is first masked out.
    """

    try:
        curmode = os.stat(path).st_mode
        # umask() returns existing umask, but requires new mask as an argument. Restore original
        # mask immediately.
        curumask = os.umask(0o022)
        os.umask(curumask)

        if stat.S_ISDIR(curmode):
            mode = 0o0777
        else:
            mode = 0o0666

        mode = ~curumask & mode
        if stat.S_IMODE(curmode) != mode:
            os.chmod(path, mode)
    except OSError as err:
        msg = Error(err).indent(2)
        raise Error(f"cannot change '{path}' permissions to {oct(mode)}:\n{msg}") from None

def _copy_dir(src: Path, dst: Path, ignore=None):
    """Implements the 'copy_dir()' function."""

    try:
        if not dst.parent.exists():
            dst.parent.mkdir(parents=True)

        if src.resolve() in dst.resolve().parents:
            raise Error(f"cannot do recursive copy from '{src}' to '{dst}'")

        ignore_names = None
        if ignore:
            ignore_names = lambda path, content: ignore

        shutil.copytree(src, dst, ignore=ignore_names)
    except (OSError, shutil.Error) as err:
        msg = Error(err).indent(2)
        raise Error(f"cannot copy '{src}' to '{dst}':\n{msg}") from err

def copy_dir(src: Path, dst: Path, exist_ok: bool = False, ignore=None):
    """
    Copy 'src' directory to 'dst'. The 'ignore' argument is a list of file or directory
    names which will be ignored and not copied.
    """

    exists_err = f"cannot copy '{src}' to '{dst}', the destination path already exists"
    if dst.exists():
        if exist_ok:
            return
        raise ErrorExists(exists_err)

    if not src.is_dir():
        raise Error(f"cannot copy '{src}' to '{dst}', the source path is not a directory.")

    _copy_dir(src, dst, ignore)

def move_copy_link(src, dst, action="symlink", exist_ok=False):
    """
    Moves, copy. or link the 'src' file or directory to 'dst' depending on the 'action' contents
    ('move', 'copy', 'symlink').
    """

    exists_err = f"cannot {action} '{src}' to '{dst}', the destination path already exists"
    if dst.exists():
        if exist_ok:
            return
        raise ErrorExists(exists_err)

    # Type cast in shutil.move() can be removed when python is fixed. See
    # https://bugs.python.org/issue32689
    try:
        if action == "move":
            if src.is_dir():
                try:
                    dst.mkdir(parents=True, exist_ok=True)
                except FileExistsError:
                    if not exist_ok:
                        raise ErrorExists(exists_err) from None
                for item in src.iterdir():
                    shutil.move(str(item), dst)
            else:
                shutil.move(str(src), dst)
        elif action == "copy":
            if not dst.parent.exists():
                dst.parent.mkdir(parents=True)

            if src.is_dir():
                _copy_dir(src, dst)
            else:
                shutil.copyfile(src, dst)
        elif action == "symlink":
            if not dst.is_dir():
                dstdir = dst.parent
            else:
                dstdir = dst

            if not dst.parent.exists():
                dst.parent.mkdir(parents=True)

            os.symlink(os.path.relpath(src.resolve(), dstdir.resolve()), dst)
        else:
            raise Error(f"unrecognized action '{action}'")
    except (OSError, shutil.Error) as err:
        raise Error(f"cannot {action} '{src}' to '{dst}':\n{err}") from err
