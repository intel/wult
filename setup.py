#!/usr/bin/python3
#
# vim: ts=4 sw=4 tw=100 et ai si
#
# Copyright (C) 2019-2020 Intel Corporation
# SPDX-License-Identifier: BSD-3-Clause
#
# Author: Artem Bityutskiy <artem.bityutskiy@linux.intel.com>

"""The standard python packaging script."""

from setuptools import setup, find_packages

setup(
    name="wult-web",
    description="Dummy package to bring pelican dependencies.",
    author="Artem Bityutskiy",
    author_email="artem.bityutskiy@linux.intel.com",
    install_requires=["pelican", "ghp-import", "typogrify"],
    long_description="""Dummy package to bring pelican dependencies.""",
	classifiers=[
		"Intended Audience :: Developers",
        "Intended Audience :: Science/Research"
        "Topic :: System :: Hardware",
		"Topic :: System :: Operating System Kernels :: Linux",
		"License :: OSI Approved :: BSD License",
	],
)
