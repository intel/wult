# -*- coding: utf-8 -*-
# vim: ts=4 sw=4 tw=100 et ai si
#
# Copyright (C) 2026 Intel Corporation
# SPDX-License-Identifier: BSD-3-Clause
#
# Author: Artem Bityutskiy <artem.bityutskiy@linux.intel.com>

"""make-a-release - make a new 'wult' project release."""

from __future__ import annotations # Remove when switching to Python 3.10+.

import os
import re
import types
import typing
import shutil
import subprocess
from pathlib import Path

try:
    argcomplete: types.ModuleType | None
    import argcomplete
except ImportError:
    # We can live without argcomplete, we only lose tab completions.
    argcomplete = None

from pepclibs.helperlibs import ArgParse, Logging, Trivial
from pepclibs.helperlibs.Exceptions import Error
from pepctools import ReleaseHelpers

if typing.TYPE_CHECKING:
    import argparse
    from typing import Final, Literal, cast

    _SkippableStepsType = Literal["branch-check", "remotes-check", "uncommitted-check"]

    class _CmdlineArgsTypedDict(typing.TypedDict, total=False):
        """
        A typed dictionary for command-line arguments of this tool.

        Attributes:
            src_path: Path to the 'wult' project git repository to make a release from (default
                      is the current directory).
            patch: Whether to increment the patch version component (x.y.z -> x.y.(z+1)).
            minor: Whether to increment the minor version component (x.y.z -> x.(y+1).0).
            major: Whether to increment the major version component (x.y.z -> (x+1).0.0).
            skip: A set of steps to skip.
            restore: Restore all modified files upon exit.
        """

        src_path: Path
        patch: bool
        minor: bool
        major: bool
        skip: set[_SkippableStepsType]
        restore: bool

_VERSION: Final[str] = "0.1"
_TOOLNAME: Final[str] = "make-a-release"

_TOOLINFO_PATHS: Final[tuple[Path, ...]] = (
    Path("wulttools/wult/ToolInfo.py"),
    Path("wulttools/ndl/ToolInfo.py"),
    Path("wulttools/pbe/ToolInfo.py"),
)

_RST_PATHS: Final[tuple[Path, ...]] = (
    Path("docs/wult-calc.rst"),
    Path("docs/wult-deploy.rst"),
    Path("docs/wult-filter.rst"),
    Path("docs/wult-scan.rst"),
    Path("docs/wult-start.rst"),
    Path("docs/ndl-calc.rst"),
    Path("docs/ndl-deploy.rst"),
    Path("docs/ndl-filter.rst"),
    Path("docs/ndl-report.rst"),
    Path("docs/ndl-scan.rst"),
    Path("docs/ndl-start.rst"),
    Path("docs/exercise-sut-start.rst"),
    Path("docs/exercise-sut-report.rst"),
    Path("docs/pbe-deploy.rst"),
    Path("docs/pbe-report.rst"),
    Path("docs/pbe-scan.rst"),
    Path("docs/pbe-start.rst"),
)

_MAN_DIR: Final[Path] = Path("wultdata/man/man1")

# Configure the root 'main' logger, not the child 'main.wult', so that messages from pepctools
# ('main.pepc.*') are also visible (e.g. 'ReleaseHelpers' push instructions).
_LOG = Logging.getLogger(f"{Logging.MAIN_LOGGER_NAME}.wult")
Logging.getLogger(Logging.MAIN_LOGGER_NAME).configure(prefix=_TOOLNAME)

def _build_arguments_parser() -> ArgParse.ArgsParser:
    """
    Build and return the command-line arguments parser.

    Returns:
        An initialized command-line arguments parser object.
    """

    text = f"""{_TOOLNAME} - make a new 'wult' project release."""
    parser = ArgParse.ArgsParser(description=text, prog=_TOOLNAME, ver=_VERSION)

    text = """Path to the 'wult' project git repository to make a release from (default is the
              current directory)."""
    parser.add_argument("-s", "--src-path", help=text, type=Path, default=Path.cwd())

    text = """Increment the patch version component: x.y.z -> x.y.(z+1). This is the default
              if no version component increment options are specified."""
    parser.add_argument("-p", "--patch", help=text, action="store_true")

    text = """Increment the minor version component: x.y.z -> x.(y+1).0."""
    parser.add_argument("-m", "--minor", help=text, action="store_true")

    text = """Increment the major version component: x.y.z -> (x+1).0.0."""
    parser.add_argument("-M", "--major", help=text, action="store_true")

    text = """Skip one or more steps. Accepts a comma-separated list of step names. Valid step
              names are: 'branch-check', 'remotes-check', 'uncommitted-check'. For development \
              and debugging only."""
    parser.add_argument("--skip", help=text, default="")

    text = """Restore all files modified by this tool upon exit. For development and debugging
              only."""
    parser.add_argument("--restore", help=text, action="store_true")

    if argcomplete is not None:
        getattr(argcomplete, "autocomplete")(parser)

    return parser

def _parse_arguments() -> argparse.Namespace:
    """
    Parse the command-line arguments.

    Returns:
        argparse.Namespace: The parsed arguments.
    """

    parser = _build_arguments_parser()
    args = parser.parse_args()

    return args

def _get_cmdline_args(args: argparse.Namespace) -> _CmdlineArgsTypedDict:
    """
    Format command-line arguments into a typed dictionary.

    Args:
        args: Command-line arguments namespace.

    Returns:
        A dictionary containing the parsed command-line arguments.
    """

    cmdl: _CmdlineArgsTypedDict = {}

    src_path: Path = args.src_path
    cmdl["src_path"] = src_path.resolve()

    cmdl["patch"] = args.patch
    cmdl["minor"] = args.minor
    cmdl["major"] = args.major

    if not (cmdl["patch"] or cmdl["minor"] or cmdl["major"]):
        # Default to patch increment if no version component increment options are specified.
        cmdl["patch"] = True

    if sum((cmdl["patch"], cmdl["minor"], cmdl["major"])) > 1:
        raise Error("Only one of the '--patch', '--minor', or '--major' options can be specified")

    cmdl["skip"] = set()
    if args.skip:
        skip = set(Trivial.split_csv_line(args.skip))
        if typing.TYPE_CHECKING:
            cmdl["skip"] = cast(set[_SkippableStepsType], skip)
        else:
            cmdl["skip"] = skip

        valid_skip: set[_SkippableStepsType] = {
            "branch-check", "remotes-check", "uncommitted-check"
        }

        unknown = cmdl["skip"] - valid_skip
        if unknown:
            raise Error(f"Unknown '--skip' value(s): {', '.join(sorted(unknown))}\n"
                        f"Valid values are: {', '.join(sorted(valid_skip))}")

    cmdl["restore"] = args.restore
    return cmdl

def _update_toolinfo_version(toolinfo_path: Path,
                             upcoming_version: tuple[int, int, int]):
    """
    Update the 'VERSION = "..."' line in a tool info Python source file.

    Args:
        toolinfo_path: Path to the tool info source file.
        upcoming_version: The upcoming release version as a (major, minor, patch) tuple.
    """

    upcoming_ver_str = f"{upcoming_version[0]}.{upcoming_version[1]}.{upcoming_version[2]}"

    try:
        content = toolinfo_path.read_text(encoding="utf-8")
    except OSError as err:
        raise Error(f"Failed to read '{toolinfo_path}': {err}") from err

    pattern = r'^(VERSION\s*=\s*")[^"]*("\s*)$'
    new_content, count = re.subn(pattern, rf"\g<1>{upcoming_ver_str}\g<2>", content,
                                 count=1, flags=re.MULTILINE)
    if count == 0:
        raise Error(f"No 'VERSION = \"...\"' line found in '{toolinfo_path}'")

    tmp_path = toolinfo_path.with_suffix(".py.tmp")
    try:
        with tmp_path.open("w", encoding="utf-8") as fobj:
            fobj.write(new_content)
            fobj.flush()
            os.fsync(fobj.fileno())
        shutil.move(str(tmp_path), toolinfo_path)
    except OSError as err:
        raise Error(f"Failed to write '{toolinfo_path}': {err}") from err
    finally:
        if tmp_path.exists():
            tmp_path.unlink()

def _regenerate_man_pages(src_path: Path) -> list[Path]:
    """
    Regenerate wult man pages from the reStructuredText source files in 'docs/'.

    Args:
        src_path: Path to the 'wult' project git repository.

    Returns:
        A list of paths to the regenerated man page files.
    """

    man_paths: list[Path] = []
    for rst_relpath in _RST_PATHS:
        rst_path = src_path / rst_relpath
        man_path = src_path / _MAN_DIR / f"{rst_path.stem}.1"
        cmd = ["pandoc", "--toc", "-f", "rst", "-s",
               str(rst_path), "-t", "man", "-o", str(man_path)]
        try:
            subprocess.run(cmd, capture_output=True, text=True, check=True)
        except subprocess.SubprocessError as err:
            raise Error(f"Failed to regenerate man page '{man_path}': {err}") from err
        _LOG.info("Regenerated man page '%s'", man_path)
        man_paths.append(man_path)

    return man_paths

def _main(cmdl: _CmdlineArgsTypedDict):
    """
    The main body of the tool.

    Args:
        cmdl: The command-line arguments description dictionary.
    """

    src_path = cmdl["src_path"]
    cur_version = ReleaseHelpers.get_current_version(src_path)
    upcoming_version = ReleaseHelpers.get_upcoming_version(cur_version, cmdl["patch"],
                                                           cmdl["minor"], cmdl["major"])
    branch = ReleaseHelpers.get_current_branch(src_path)
    if "branch-check" not in cmdl["skip"] and branch != "main":
        raise Error(f"Current branch is '{branch}', but must be 'main'")
    if "remotes-check" not in cmdl["skip"]:
        ReleaseHelpers.check_remote_branches(src_path)

    _LOG.info("Project version: %d.%d.%d -> %d.%d.%d", *cur_version, *upcoming_version)

    if "uncommitted-check" not in cmdl["skip"]:
        ReleaseHelpers.check_everything_committed(src_path)

    modified: list[Path] = []
    committed = False
    tagged = False

    try:
        ReleaseHelpers.prepare_changelog(src_path, cur_version, upcoming_version)
        modified.append(src_path / "CHANGELOG.md")
        ReleaseHelpers.prepare_pyproject_toml(src_path, upcoming_version)
        modified.append(src_path / "pyproject.toml")
        for relpath in _TOOLINFO_PATHS:
            toolinfo_path = src_path / relpath
            _update_toolinfo_version(toolinfo_path, upcoming_version)
            modified.append(toolinfo_path)
        modified.extend(_regenerate_man_pages(src_path))
        ReleaseHelpers.commit_release(src_path, upcoming_version, modified)
        committed = True
        ReleaseHelpers.tag_release(src_path, upcoming_version)
        tagged = True
    finally:
        if cmdl["restore"]:
            if tagged:
                ReleaseHelpers.untag_release(src_path, upcoming_version)
            if committed:
                ReleaseHelpers.uncommit_release(src_path)
            ReleaseHelpers.restore_files(modified)

    if not cmdl["restore"]:
        ReleaseHelpers.print_push_instructions(upcoming_version)

def main():
    """
    The entry point of the tool.

    Returns:
        The program exit code.
    """

    try:
        args = _parse_arguments()
        cmdl = _get_cmdline_args(args)
        _main(cmdl)
    except KeyboardInterrupt:
        _LOG.info("\nInterrupted, exiting")
    except Error as err:
        _LOG.error_out(str(err))

    return 0
