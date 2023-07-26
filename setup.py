#!/usr/bin/python3
#
# vim: ts=4 sw=4 tw=100 et ai si
#
# Copyright (C) 2019-2023 Intel Corporation
# SPDX-License-Identifier: BSD-3-Clause
#
# Author: Artem Bityutskiy <artem.bityutskiy@linux.intel.com>

"""The standard python packaging script."""

import re
import os
from pathlib import Path
from setuptools import setup, find_packages

_TOOLNAMES = ["wult", "ndl", "exercise-sut"]

def get_version(filename):
    """Fetch the project version number."""

    with open(filename, "r", encoding="utf-8") as fobj:
        for line in fobj:
            matchobj = re.match(r'^VERSION = "(\d+.\d+.\d+)"$', line)
            if matchobj:
                return matchobj.group(1)
    return None

def get_data_files(installdir, subdir, exclude=None):
    """
    When the task is to include all files in the 'subdir' directory to the package and install them
    under the 'installdir' directory, this function can be used to generate the list of files
    suitable for the 'data_files' setup parameter.
    """

    files_dict = {}
    for root, _, files in os.walk(subdir):
        for fname in files:
            fname = Path(f"{root}/{fname}")

            if exclude and str(fname) in exclude:
                continue

            key = str(Path(installdir) / fname.relative_to(subdir).parent)
            if key not in files_dict:
                files_dict[key] = []
            files_dict[key].append(str(fname))

    return list(files_dict.items())

setup(
    name="wult",
    description="Wake Up Latency Tracer tool",
    author="Artem Bityutskiy",
    author_email="artem.bityutskiy@linux.intel.com",
    python_requires=">=3.7",
    version=get_version("wulttools/wult/ToolInfo.py"),
    data_files=get_data_files("share/man/man1", "docs/man1") + \
               get_data_files("share/wult/drivers", "drivers") + \
               get_data_files("share/wult/helpers", "helpers") + \
               get_data_files("share/wult/defs/wult", "defs/wult"),
    scripts=_TOOLNAMES,
    packages=find_packages(),
    install_requires=["pepc>=1.4.25", "stats-collect>=1.0.14", "numpy", "pandas", "pyyaml",
                      "colorama"],
    long_description="""This package provides wult - a Linux command-line tool for measuring Intel
                        CPU C-state wake latency.""",
    classifiers=[
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research"
        "Topic :: System :: Hardware",
        "Topic :: System :: Operating System Kernels :: Linux",
        "License :: OSI Approved :: BSD License",
        "License :: OSI Approved :: GNU General Public License v2 (GPLv2)",
        "Programming Language :: Python :: 3 :: Only",
        "Development Status :: 4 - Beta",
    ],
)
