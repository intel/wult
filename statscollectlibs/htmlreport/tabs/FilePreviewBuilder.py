# -*- coding: utf-8 -*-
# vim: ts=4 sw=4 tw=100 et ai si
#
# Copyright (C) 2023 Intel Corporation
# SPDX-License-Identifier: BSD-3-Clause
#
# Authors: Adam Hawley <adam.james.hawley@intel.com>

"""
This module provides the capability of populating a 'File Preview'. See '_Tabs.FilePreviewDC' for
more information on file previews.
"""

import filecmp
import logging
from difflib import HtmlDiff
from pepclibs.helperlibs import Human
from pepclibs.helperlibs.Exceptions import Error, ErrorExists
from statscollectlibs.helperlibs import FSHelpers
from statscollectlibs.htmlreport.tabs import _Tabs

_LOG = logging.getLogger()

def _reasonable_file_size(fp, name):
    """
    Returns 'True' if the file at path 'fp' is 2MiB or smaller, otherwise returns 'False'. Also
    returns 'False' if the size could not be verified.  Arguments are as follows:
        * fp - path of the file to check the size of.
        * name - name of the file-preview being generated.
    """

    try:
        fsize = fp.stat().st_size
    except OSError as err:
        _LOG.warning("skipping file preview '%s': unable to check the size of file '%s' before "
                     "copying:\n%s", name, fp, err)
        return False

    if fsize > 2*1024*1024:
        _LOG.warning("skipping file preview '%s': the file '%s' (%s) is larger than 2MiB.",
                     name, fp, Human.bytesize(fsize))
        return False
    return True

class FilePreviewBuilder:
    """This class provides the capability of populating a 'File Preview'."""

    def _generate_diff(self, paths, diff_name):
        """
        Helper function for '_add_fpreviews()'. Generates an HTML diff of the files at 'paths' with
        filename 'diff_name.html' in a "diffs" sub-directory. Returns the path of the HTML diff
        relative to 'outdir'.
        """

        if filecmp.cmp(*(self._basedir / path for path in paths.values())):
            _LOG.info("Skipping '%s' diff as both files are identical.", diff_name)
            return None

        # Read the contents of the files into 'lines'.
        lines = []
        for diff_src in paths.values():
            try:
                fp = self._basedir / diff_src
                with open(fp, "r", encoding="utf-8") as f:
                    lines.append(f.readlines())
            except OSError as err:
                msg = Error(err).indent(2)
                raise Error(f"cannot open file at '{fp}' to create diff:\n{msg}") from None

        # Store the diff in a separate directory and with the '.html' file ending.
        diff_path = (self.outdir / "diffs" / diff_name).with_suffix('.html')
        try:
            diff_path.parent.mkdir(parents=True, exist_ok=True)
        except OSError as err:
            msg = Error(err).indent(2)
            raise Error(f"cannot create diffs directory '{diff_path.parent}':\n"
                        f"{msg}") from None

        try:
            with open(diff_path, "w", encoding="utf-8") as f:
                f.write(HtmlDiff().make_file(lines[0], lines[1]))
        except Exception as err:
            msg = Error(err).indent(2)
            raise Error(f"cannot create diff at path '{diff_path}':\n{msg}") from None

        return diff_path.relative_to(self._basedir)

    def build_fpreviews(self, base_paths, files):
        """
        Build file previews. Scans for the files specified in 'files' in each result directory.
        Arguments are as follows:
         * base_paths - dictionary in the format '{ReportID: BasePath}' where 'BasePath' is the base
                        directory for the result with report id 'ReportID'. This class will search
                        this base directory to find the file to display in the preview.
         * files - dictionary in the format '{FilePreviewTitle: FilePath}' where 'FilePath' is the
                   patch that will be used to check for the file in each result in 'base_paths'.
        """

        self.fpreviews = []
        for name, fp in files.items():
            paths = {}
            for reportid, base_path in base_paths.items():
                src_path = base_path / fp

                if not src_path.exists():
                    # If one of the reports does not have a file, exclude the file preview entirely.
                    paths = {}
                    _LOG.debug("skipping file preview '%s' since the file '%s' doesn't exist for "
                               "all reports.", name, fp)
                    break

                # If the file is not in 'outdir' it should be copied to 'outdir'.
                if self.outdir not in src_path.parents:
                    if not _reasonable_file_size(src_path, name):
                        break

                    dst_dir = self.outdir / reportid

                    try:
                        dst_dir.mkdir(parents=True, exist_ok=True)
                    except OSError as err:
                        msg = Error(err).indent(2)
                        raise Error(f"can't create directory '{dst_dir}':\n"
                                    f"{msg}") from None

                    dst_path = dst_dir / fp

                    try:
                        FSHelpers.move_copy_link(src_path, dst_path, "copy")
                    except ErrorExists:
                        _LOG.debug("file '%s' already in output dir: will not replace.", dst_path)
                else:
                    dst_path = src_path

                paths[reportid] = dst_path.relative_to(self._basedir)

            if len(paths) == 2:
                try:
                    diff = self._generate_diff(paths, fp)
                except Error as err:
                    _LOG.info("Unable to generate diff for file preview '%s'.", name)
                    _LOG.debug(err)
                    diff = ""
            else:
                diff = ""

            if paths:
                self.fpreviews.append(_Tabs.FilePreviewDC(name, paths, diff))

        return self.fpreviews

    def __init__(self, outdir, basedir=None):
        """
        The class constructor. Arguments are as follows:
         * outdir - path to the directory to store the files which will be displayed in the preview.
         * basedir - base directory of the report. All paths will be made relative to this.
                     Defaults to 'outdir'.
        """

        self.outdir = outdir
        self._basedir = basedir if basedir else outdir
        self.fpreviews = []
