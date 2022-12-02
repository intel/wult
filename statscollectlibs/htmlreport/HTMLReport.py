# -*- coding: utf-8 -*-
# vim: ts=4 sw=4 tw=100 et ai si
#
# Copyright (C) 2022 Intel Corporation
# SPDX-License-Identifier: BSD-3-Clause
#
# Authors: Adam Hawley <adam.james.hawley@intel.com>

"""This module provides the API for generating HTML reports."""

import dataclasses
import logging
import json
from pathlib import Path
from pepclibs.helperlibs.Exceptions import Error, ErrorNotFound
from statscollectlibs.helperlibs import ToolHelpers, FSHelpers
from statscollectlibs.htmlreport.tabs import _ACPowerTabBuilder, _IPMITabBuilder, _Tabs
from statscollectlibs.htmlreport.tabs.turbostat import _TurbostatTabBuilder
from statscollectlibs.htmlreport.tabs.sysinfo import (_CPUFreqTabBuilder, _CPUIdleTabBuilder,
    _DMIDecodeTabBuilder, _DmesgTabBuilder, _EPPTabBuilder, _LspciTabBuilder, _MiscTabBuilder,
    _PepcTabBuilder)
from statscollectlibs.htmlreport.tabs.sysinfo import _TurbostatTabBuilder as _SysInfoTstatTabBuilder

_LOG = logging.getLogger()

def _copy_assets(outdir):
    """
    This is a helper function for 'generate_report()' which copies assets to 'outdir'.

    "Assets" refers to all of the static files which are included as part of every report.
    """

    # This list defines the assets which should be copied into the output directory. Items in the
    # list are tuples in the format: (asset_description, path_to_asset, path_of_copied_asset).
    assets = [
        ("bundled JavaScript", "js/dist/main.js", outdir / "js/dist/main.js"),
        ("bundled CSS", "js/dist/main.css", outdir / "js/dist/main.css"),
        ("bundled dependency licenses", "js/dist/main.js.LICENSE.txt",
            outdir / "js/dist/main.js.LICENSE.txt"),
        ("root HTML page of the report.", "js/index.html", outdir / "index.html"),
        ("script to serve report directories.", "misc/servedir/serve_directory.py",
            outdir / "serve_directory.py"),
        ("README file for local viewing scripts", "misc/servedir/README.md",
            outdir / "README.md")
    ]

    for asset in assets:
        asset_path = ToolHelpers.find_project_data("wult", asset[1], descr=asset[0])
        FSHelpers.move_copy_link(asset_path, asset[2], "copy", exist_ok=True)

def _dump_json(obj, path, descr):
    """
    Helper function wrapping 'json.dump' operation with a standardised error message so that the
    error messages are consistent. Arguments are as follows:
        * obj - Python object to dump to JSON.
        * path - path to create JSON file at.
        * descr - description of object being dumped.
    """

    try:
        with open(path, "w", encoding="utf-8") as fobj:
            json.dump(obj, fobj, default=str)
    except Exception as err:
        msg = Error(err).indent(2)
        raise Error(f"could not generate report: failed to JSON dump '{descr}' to '{path}':\n"
                    f"{msg}") from None

class HTMLReport:
    """This class provides the API for generating HTML reports."""

    def _generate_stats_tabs(self, stats_paths, measured_cpus=None):
        """
        Generate and return a list sub-tabs for the statistics tab. The statistics tab includes
        metrics from the statistics collectors, such as 'turbostat'.

        The 'stats_paths' argument is a dictionary mapping in the following format:
           {Report ID: Stats directory path}
        where "stats directory path" is the directory containing raw statistics files.

        The elements of the returned list are tab dataclass objects, such as 'CTabDC'.
        """

        _LOG.info("Generating statistics tabs.")

        if measured_cpus is None:
            measured_cpus = {}
        tab_builders = {
            _ACPowerTabBuilder.ACPowerTabBuilder: {},
            _TurbostatTabBuilder.TurbostatTabBuilder: {"measured_cpus": measured_cpus},
            _IPMITabBuilder.IPMITabBuilder: {}
        }

        tabs = []

        for tab_builder, args in tab_builders.items():
            try:
                tbldr = tab_builder(stats_paths, self.outdir, **args)
            except ErrorNotFound as err:
                _LOG.info("Skipping '%s' tab as '%s' statistics not found for all reports.",
                          tab_builder.name, tab_builder.name)
                _LOG.debug(err)
                continue

            _LOG.info("Generating '%s' tab.", tbldr.name)
            try:
                tabs.append(tbldr.get_tab())
            except Error as err:
                _LOG.info("Skipping '%s' statistics: error occurred during tab generation.",
                          tab_builder.name)
                _LOG.debug(err)
                continue

        return tabs

    def _generate_sysinfo_tabs(self, stats_paths):
        """
        Generate and return a list of data tabs for the SysInfo container tab. The container tab
        includes tabs representing various system information about the SUTs.

        The 'stats_paths' argument is a dictionary mapping in the following format:
           {'report_id': 'stats_directory_path'}
        where 'stats_directory_path' is the directory containing raw statistics files.

        The elements of the returned list are tab dataclass objects, such as '_Tabs.DTabDC'.
        """

        tab_builders = [
            _PepcTabBuilder.PepcTabBuilder,
            _SysInfoTstatTabBuilder.TurbostatTabBuilder,
            _DMIDecodeTabBuilder.DMIDecodeTabBuilder,
            _EPPTabBuilder.EPPTabBuilder,
            _CPUFreqTabBuilder.CPUFreqTabBuilder,
            _CPUIdleTabBuilder.CPUIdleTabBuilder,
            _DmesgTabBuilder.DmesgTabBuilder,
            _LspciTabBuilder.LspciTabBuilder,
            _MiscTabBuilder.MiscTabBuilder
        ]

        tabs = []

        for tab_builder in tab_builders:
            tbldr = tab_builder(self.outdir)

            _LOG.info("Generating '%s' tab.", tbldr.name)
            try:
                tabs.append(tbldr.get_tab(stats_paths))
            except Error as err:
                _LOG.info("Skipping '%s' SysInfo tab: error occurred during tab generation.",
                          tbldr.name)
                _LOG.debug(err)
                continue

        return tabs

    def _generate_tabs(self, stats_paths, measured_cpus=None):
        """Helper function for 'generate_report()'. Generates statistics and sysinfo tabs."""

        tabs = []

        try:
            stats_tabs = self._generate_stats_tabs(stats_paths, measured_cpus)
        except Error as err:
            _LOG.info("Error occurred during statistics tabs generation: %s", err)
            stats_tabs = []

        if stats_tabs:
            tabs.append(_Tabs.CTabDC("Stats", tabs=stats_tabs))
        else:
            _LOG.info("All statistics have been skipped, therefore the report will not contain "
                      "a 'Stats' tab.")

        try:
            sysinfo_tabs = self._generate_sysinfo_tabs(stats_paths)
        except Error as err:
            _LOG.info("Error occurred during info tab generation: %s", err)
            sysinfo_tabs = []

        if sysinfo_tabs:
            tabs.append(_Tabs.CTabDC("SysInfo", tabs=sysinfo_tabs))
        else:
            _LOG.info("All SysInfo tabs have been skipped, therefore the report will not "
                      "contain a 'SysInfo' tab.")

        return tabs

    def generate_report(self, tabs=None, stats_paths=None, intro_tbl=None, title=None, descr=None,
                        measured_cpus=None):
        """
        Generate a report in 'outdir' with 'tabs'. Arguments are as follows:
         * tabs - a list of additional container tabs which should be included in the report. If,
                  omitted, 'stats_paths' is required to generate statistics tabs.
         * stats_paths - a dictionary in the following format: {'report_id': 'stats_dir_path'}
                         where 'stats_dir_path' is the directory containing raw statistics files. If
                         not provided, no statistics tabs will be generated and 'tabs' will be
                         required to populate the report.
         * intro_tbl - an '_IntroTable.IntroTable' instance which represents the table which will be
                       included in the report. If one is not provided, it will be omitted from the
                       report.
         * title - the title of the report. If one is not provided, omits the title.
         * descr - a description of the report. If one is not provided, omits the description.
         * measured_cpus - dictionary in the format {'reportid': 'measured_cpu'} where
                           'measured_cpu' is the CPU that was being tested during the workload. If
                           not provided, the turbostat "Measured CPU" tab will not be generated.
        """

        if not tabs and not stats_paths:
            raise Error("both 'tabs' and 'stats_paths' can't be 'None'. One of the two parameters "
                        "should be provided.")

        if not tabs:
            tabs = []

        # Make sure the output directory exists.
        try:
            self.outdir.mkdir(parents=True, exist_ok=True)
        except OSError as err:
            msg = Error(err).indent(2)
            raise Error(f"failed to create directory '{self.outdir}':\n{msg}") from None

        # 'report_info' stores data used by the Javascript to generate the main report page
        # including the intro table, the file path of the tabs JSON dump plus the report title and
        # description.
        report_info = {"title": title, "descr": descr}

        if intro_tbl is not None:
            intro_tbl_path = self.outdir / "intro_tbl.json"
            intro_tbl.generate(intro_tbl_path)
            report_info["intro_tbl"] = intro_tbl_path.relative_to(self.outdir)

        if stats_paths is not None:
            tabs += self._generate_tabs(stats_paths, measured_cpus)

        # Convert Dataclasses to dictionaries so that they are JSON serialisable.
        json_tabs = [dataclasses.asdict(tab) for tab in tabs]
        tabs_path = self.outdir / "tabs.json"
        _dump_json(json_tabs, tabs_path, "tab container")
        report_info["tab_file"] = tabs_path.relative_to(self.outdir)

        rinfo_path = self.outdir / "report_info.json"
        _dump_json(report_info, rinfo_path, "report information dictionary")

        _copy_assets(self.outdir)

    def __init__(self, outdir):
        """
        The class constructor. The arguments are as follows:
         * outdir - the directory which will contain the report.
        """

        self.outdir = Path(outdir)
