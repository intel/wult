#!/usr/bin/python3
#
# vim: ts=4 sw=4 tw=100 et ai si
#
# Copyright (C) 2019-2021 Intel Corporation
# SPDX-License-Identifier: BSD-3-Clause
#
# Author: Artem Bityutskiy <artem.bityutskiy@linux.intel.com>

"""The standard python packaging script."""

import re
import os
from pathlib import Path
from setuptools import setup, find_packages

_TOOLNAMES = ["wult", "ndl"]

def get_version():
    """Get the project version number."""

    majors, minors, stables = [], [], []

    for toolname in _TOOLNAMES:
        with open(toolname, encoding="utf-8", mode="r") as fobj:
            for line in fobj:
                matchobj = re.match(r'^VERSION = "(\d+.\d+.\d+)"$', line)
                if matchobj:
                    major, minor, stable = matchobj.group(1).split(".")
                    majors.append(int(major.strip()))
                    minors.append(int(minor.strip()))
                    stables.append(int(stable.strip()))
                    break

    major = sum(majors)
    minor = sum(minors)
    stable = sum(stables)

    return f"{major}.{minor}.{stable}"

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

# Python helpers get installed as scripts. We exclude these scripts from being installed as data.
_PYTHON_HELPERS = ["helpers/stats-collect/stats-collect", "helpers/stats-collect/ipmi-helper"]

setup(
    name="wult",
    description="Wake Up Latency Tracer tool",
    author="Artem Bityutskiy",
    author_email="artem.bityutskiy@linux.intel.com",
    python_requires=">=3.7",
    version=get_version(),
    data_files=get_data_files("share/wult/drivers", "drivers") + \
               get_data_files("share/wult/helpers", "helpers", exclude=_PYTHON_HELPERS) + \
               get_data_files("share/wult/defs", "defs") + \
               get_data_files("share/wult/js/dist", "js/dist") + \
               [("share/wult/js", ["js/index.html"])],
    scripts=_TOOLNAMES + _PYTHON_HELPERS,
    packages=find_packages(),
    install_requires=["pepc>=1.3.5,<1.4.0", "plotly>=4", "numpy", "pandas", "pyyml", "colorama"],
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
