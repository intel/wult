#!/usr/bin/python3
#
# vim: ts=4 sw=4 tw=100 et ai si
#
# Copyright (C) 2019-2020 Intel Corporation
# SPDX-License-Identifier: BSD-3-Clause
#
# Author: Artem Bityutskiy <artem.bityutskiy@linux.intel.com>

"""The standard python packaging script."""

import re
import os
import sys
from pathlib import Path
from setuptools import setup, find_packages

_TOOLNAMES = ["wult", "ndl"]

if sys.version_info < (3, 6):
    raise SystemExit("Error: wult: this project requires python version 3.6 or higher.")

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

def get_data_files(installdir, subdir):
    """
    When the task is to include all files in the 'subdir' direcotry to the package and install them
    under the 'installdir' directory, this function can be used to generate the list of files
    suitable for the 'data_files' setup parameter.
    """

    result = []
    for root, _, files in os.walk(subdir):
        for fname in files:
            fname = Path(f"{root}/{fname}")
            installpath = Path(installdir) / fname.relative_to(subdir).parent
            result.append([str(installpath), (str(fname),)])
    return result

setup(
    name="wult",
    description="Wake up LAtency Tracer tool",
    author="Artem Bityutskiy",
    author_email="artem.bityutskiy@linux.intel.com",
    version=get_version(),
    data_files=get_data_files("share/wult/drivers", "drivers") + \
               get_data_files("share/wult/helpers", "helpers") + \
               get_data_files("share/wult/defs", "defs") + \
               get_data_files("share/wult/templates", "templates") + \
               get_data_files("share/wult/css", "css"),
    scripts=_TOOLNAMES,
    packages=find_packages(),
    install_requires=["plotly>=4", "jinja2", "numpy", "pandas", "paramiko", "pyyml"],
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
		"Development Status :: 3 - Beta",
	],
)
