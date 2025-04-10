# -*- coding: utf-8 -*-
# vim: ts=4 sw=4 tw=100 et ai si
#
# Copyright (C) 2023 Intel Corporation
# SPDX-License-Identifier: BSD-3-Clause
#
# Author: Antti Laakso <antti.laakso@linux.intel.com>
#         Artem Bityutskiy <artem.bityutskiy@linux.intel.com>

"""A helper module for the 'exercise-sut' tool for generating reports and diffs."""

import os
from pathlib import Path
from pepclibs.helperlibs import Logging, Trivial, YAML
from pepclibs.helperlibs.Exceptions import Error, ErrorNotFound
from statscollecttools import ToolInfo as StcToolInfo
from wulttools.exercisesut import _Common
from wulttools.ndl import ToolInfo as NdlToolInfo
from wulttools.pbe import ToolInfo as PbeToolInfo
from wulttools.wult import ToolInfo as WultToolInfo

_LOG = Logging.getLogger(f"{Logging.MAIN_LOGGER_NAME}.wult.{__name__}")

class BatchReport(_Common.CmdlineRunner):
    """Helper class for 'exercise-sut' tool to create reports for series of results."""

    def _resolve_toolpath(self):
        """Find out tool name from results, and return full path to it."""

        try:
            infopath = self._respaths[0] / "info.yml"
            resinfo = YAML.load(infopath)
            return self._lpman.which(resinfo["toolname"])
        except Error as err:
            raise ErrorNotFound(f"failed to read toolname from '{infopath}', use '--toolpath' to "
                                f"specify tool to generate reports\n{err}") from err

    def _search_result_paths(self, searchpaths):
        """Find all result paths in list of paths 'searchpaths'. Returns single list of paths."""

        respaths = []
        for searchpath in searchpaths:
            if not searchpath.exists():
                raise Error(f"input path '{searchpath}' does not exist")

            if not searchpath.is_dir():
                raise Error(f"input path '{searchpath}' is not a directory")

            for respath in os.scandir(searchpath):
                if respath.is_dir():
                    respaths.append(Path(respath.path))

        return respaths

    def _filter_result_paths(self, include, exclude):
        """
        Filter result directories with following arguments.
          * include - List of monikers that must be found from the result path name.
          * exclude - List of monikers that must not be found from the result path name.
        """

        include_monikers = set()
        exclude_monikers = set()

        if include:
            for moniker in Trivial.split_csv_line(include):
                include_monikers.add(moniker.lower())

        if exclude:
            for moniker in Trivial.split_csv_line(exclude):
                exclude_monikers.add(moniker.lower())

        respaths = []
        for respath in self._respaths:
            path_monikers = [moniker.lower() for moniker in respath.name.split("-")]

            if include_monikers and not include_monikers.issubset(set(path_monikers)):
                continue

            if exclude_monikers and exclude_monikers.intersection(set(path_monikers)):
                continue

            respaths.append(respath)

        return respaths

    def _match_reportid_monikers(self, diff_monikers, reportid_monikers):
        """Find common monikers of moniker lists 'diff_monikers' and 'reportid_monikers'."""

        common_monikers = []
        for diff_moniker in diff_monikers:
            # Diff moniker might include dash ('-'), in which case we need to look for each
            # sub-string.
            sub_strings = diff_moniker.split("-")
            if set(sub_strings).issubset(reportid_monikers):
                for sub_string in sub_strings:
                    common_monikers.append(sub_string)

        return common_monikers

    def _get_grouped_paths(self, respaths, diff_monikers):
        """
        Group results from paths 'respaths'. Group results according to list of monikers in
        'diff_monikers', if any. Returns dictionary with common directory name as key and list
        matching paths as values.
        """

        basepath = Path("-vs-".join([moniker for moniker in diff_monikers if moniker]))

        groups = {}
        for respath in respaths:
            result_monikers = respath.name.split("-")
            common_monikers = self._match_reportid_monikers(diff_monikers, result_monikers)
            if not common_monikers and "" not in diff_monikers:
                continue

            # Remove common monikers from path name.
            for common_moniker in common_monikers:
                if common_moniker in result_monikers:
                    result_monikers.remove(common_moniker)

            outdir = basepath / "-".join(result_monikers)
            if outdir not in groups:
                groups[outdir] = []

            groups[outdir].append(respath)

        return groups

    def _get_diff_paths(self, respaths, diff_monikers):
        """
        Find results matching to list of monikers 'diff_monikers' and yield diff output path with
        list of result paths.
        """

        def _get_path_sortkey(path):
            """
            Method for sorting paths according to order of given diff monikers, or order of input
            paths. Returns first diff moniker index found in monikers of given path 'path'.
            """

            path_monikers = path.name.split("-")
            # First check only multi-part monikers.
            # Example
            # diff_monikers: ['c6', 'c6-pc6']
            # We want to search 'c6-pc6' first, as 'c6' moniker would match to both paths:
            # path1 monikers: ['spr0', 'hrt', 'c6', 'pc6', 'hfm', 'uf_2ghz']
            # path2 monikers: ['spr0', 'hrt', 'c6', 'hfm', 'uf_2ghz']
            for moniker in diff_monikers:
                split = moniker.split("-")
                if len(split) < 2:
                    continue

                if set(split).issubset(set(path_monikers)) and moniker in path.name:
                    return diff_monikers.index(moniker)

            for moniker in diff_monikers:
                if moniker in path_monikers:
                    return diff_monikers.index(moniker)

            # Empty diff moniker is special, handle it after non-empty diff monikers.
            if "" in diff_monikers:
                return diff_monikers.index("")

            # If no diff, sort according to order of result paths.
            for respath in respaths:
                if path.parent == respath:
                    return respaths.index(respath)

            return len(diff_monikers)

        grouped_paths = self._get_grouped_paths(respaths, diff_monikers)
        for outdir, paths in grouped_paths.items():
            paths.sort(key=_get_path_sortkey)

            # Yield paths only for diffs where all requested results are found.
            if diff_monikers and len(paths) < len(diff_monikers):
                continue

            yield outdir, paths

    def group_results(self, diffs=None, include=None, exclude=None):
        """
        Find results and group them according to arguments:
          * diffs - List of lists of monikers to group results with.
          * include - Comma-separated list of monikers that must be found from the result path name.
          * exclude - Comma-separated list of monikers that must not be found from the result path
                      name.

        Yields tuple with common directory name as key and list of paths matching to the rules as
        value.
        """

        respaths = self._filter_result_paths(include, exclude)

        if diffs:
            for diff_monikers in diffs:
                diff_monikers = [moniker.lower() for moniker in diff_monikers]
                yield from self._get_diff_paths(respaths, diff_monikers)
        else:
            for respath in respaths:
                outdir = "individual" / Path(respath.name)
                yield outdir, [respath]

    def generate_report(self, respaths, outdir):
        """Generate the report for list of results in 'respaths', store the report to 'outdir'."""

        if outdir.exists():
            _LOG.warning("path '%s' exists", outdir)

        cmd = f"nice -n19 ionice -c3 {self.toolpath} "

        if self.toolpath.name in (NdlToolInfo.TOOLNAME, WultToolInfo.TOOLNAME,
                                  StcToolInfo.TOOLNAME, PbeToolInfo.TOOLNAME):
            cmd += "report "

        if self._toolopts:
            toolopts = self._toolopts.replace("{REPORTID}", outdir.name)
            cmd += f"{toolopts} "

        res_str = " ".join([str(path) for path in respaths])
        cmd += f"-o {outdir} {res_str}"

        self.run_command(cmd)

    def __init__(self, respaths, dry_run=False, jobs=None, toolpath=None, toolopts=None,
                 ignore_errors=False):
        """
        The class constructor.

        Args:
            respaths: Path to search results from.
            dry_run: If 'True', print the command instead of running it.
            jobs: Number of processes to run in parallel.
            toolpath: Path to the tool to generate report with.
            toolopts: Options for the report generation tool.
            ignore_errors: If 'True', keep processing commands even if some fail.
        """

        super().__init__(dry_run=dry_run, proc_count=jobs, ignore_errors=ignore_errors)

        self.toolpath = toolpath
        self._toolopts = toolopts
        self._respaths = self._search_result_paths(respaths)

        if not self.toolpath:
            self.toolpath = self._resolve_toolpath()
