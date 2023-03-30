
# -*- coding: utf-8 -*-
# vim: ts=4 sw=4 tw=100 et ai si
#
# Copyright (C) 2019-2023 Intel Corporation
# SPDX-License-Identifier: BSD-3-Clause
#
# Author: Artem Bityutskiy <artem.bityutskiy@linux.intel.com>

"""
This module provides the API for deploying bpf helpers. Refer to the 'DeployBase' module
docstring for more information.
"""

from pathlib import Path
import logging
from pepclibs.helperlibs.Exceptions import ErrorNotFound
from statscollectlibs.deploylibs import DeployHelpersBase

_LOG = logging.getLogger()

class DeployBPFHelpers(DeployHelpersBase.DeployHelpersBase):
    """This class provides the API for deploying bpf helpers."""

    def _check_for_shared_library(self, soname):
        """
        Check if a shared library 'soname' is available on the build host. Returns if it is
        available, raises 'ErrorNotFound' otherwise.
        """

        _, stderr, _ = self._bpman.run(f"cc -l{soname}")
        if f"cannot find -l{soname}" in stderr:
            msg = f"The 'lib{soname}' library is not installed{self._bpman.hostmsg}"

            btchk = self._get_btchk()
            pkgname = btchk.tool_to_pkg(f"lib{soname}")
            if pkgname:
                msg += f"\nTry to install OS package '{pkgname}'."
            raise ErrorNotFound(msg)

    def _find_ebpf_include_dirs(self, headers):
        """
        eBPF helpers depend on various C header files from kernel source. The location of some of
        these files varies depending on kernel version and/or how the OS package places them. This
        method finds the locations of header files 'headers' and return the locations list.

        For example, Ubuntu 22.04 puts the 'bpf/bpf_helpers.h' file to '/usr/include', and it comes
        from the 'libbpf-dev' package, not from the kernel sources package. Fedora 36 delivers this
        file via the kernel sources package.
        """

        search_info = {}

        # The search_info to use when searching in the kernel directory.
        #
        # Note, this list is crafted so that the 'include' subdirectory would go before the
        # 'usr/include' subdirectory. Otherwise the compilation breaks. And this only happens when
        # user ran 'make headers_install', so that 'usr/include' contains the "processed UAPI
        # headers".
        basedir = self._ksrc
        search_info[basedir] = ("libbpf/include", "tools/lib", "tools/lib/bpf", "include",
                                "usr/include", "libbpf/include/bpf",
                                # Fedora-specific UAPI and libbpf include directories (the
                                # 'kernel-devel' module places them there).
                                "include/generated/uapi",
                                "tools/bpf/resolve_btfids/libbpf",
                                "tools/bpf/resolve_btfids/libbpf/include")

        # Some bpf headers may be found in '/usr/include'. Examples.
        basedir = Path("/usr/include")
        if self._bpman.is_dir(basedir):
            search_info[basedir] = ("", "bpf")

        incdirs = []
        for header in headers:
            tried = []

            for basedir, suffixes in search_info.items():
                found = False
                for sfx in suffixes:
                    incdir = basedir / sfx
                    tried.append(incdir)
                    if self._bpman.is_file(incdir / header):
                        incdirs.append(incdir)
                        found = True
                        break
                if found:
                    break
            else:
                tried = "\n * ".join([str(path) for path in tried])
                err = f"failed to find C header file '{header}'.\nTried the following paths" \
                      f"{self._bpman.hostmsg}:\n* {tried}"

                # In Ubuntu, the '/usr/include/asm/types.h' file does not exist unless the
                # 'gcc-multilib' package is installed. Include this information to the error
                # message.
                btchk = self._get_btchk()
                if header == "asm/types.h" and btchk.get_osname() == "Ubuntu":
                    err += "\nTry to install the 'gcc-multilib' Ubuntu package"

                raise ErrorNotFound(err)

        return incdirs

    def _find_or_build_libbpf_a_from_ksrc(self):
        """
        The searches for 'libbpf.a' (static libbpf library) in the kernel sources and returns its
        path. If 'libbpf.a' was not found, this method compiles it in the kernel sources and
        returns the path to 'libbpf.a'.
        """

        # The location of 'libbpf.a' in kernel sources may vary, check several known paths.
        suffixes = ("tools/lib/bpf", "tools/bpf/resolve_btfids/libbpf", "libbpf")
        tried_paths = []

        for sfx in suffixes:
            path = self._ksrc / sfx / "libbpf.a"
            tried_paths.append(path)
            if self._bpman.is_file(path):
                return path

        tried = "\n * ".join([str(path) for path in tried_paths])
        msg = f"failed to find 'libbpf.a', tried these paths{self._bpman.hostmsg}:\n * {tried}\n" \
              f"Trying to compile it."

        # Try to compile 'libbpf.a'. It requires 'libelf'.
        self._check_for_shared_library("elf")

        cmd = f"make -C '{self._ksrc}/tools/lib/bpf'"
        self._bpman.run_verify(cmd)

        path = f"{self._ksrc}/tools/lib/bpf/libbpf.a"
        if self._bpman.is_file(path):
            return path

        raise ErrorNotFound(f"{msg}\nCompiled 'libbpf.a', but it was still not found in " \
                            f"'{path}'{self._bpman.hostmsg}")

    def _prepare(self, helpersrc, helpers):
        """
        Build and prepare eBPF helpers for deployment. The arguments are as follows:
          * helpersrc - path to the helpers base directory on the controller.
          * helpers - bpf helpers to deploy.
        """

        btchk = self._get_btchk()
        btchk.check_tool("cc")

        # Copy eBPF helpers to the temporary directory on the build host.
        for bpfhelper in helpers:
            srcdir = helpersrc / bpfhelper
            _LOG.debug("copying eBPF helper '%s' to %s:\n  '%s' -> '%s'",
                       bpfhelper, self._bpman.hostname, srcdir, self._btmpdir)
            self._bpman.rsync(srcdir, self._btmpdir, remotesrc=False,
                              remotedst=self._bpman.is_remote)

        if self._rebuild_src:
            # In order to compile the eBPF components of eBPF helpers, the build host must have
            # 'clang' and 'bpftool' available. These tools are used from the 'Makefile'. Let's check
            # for them in order to generate a user-friendly message if one of them is not installed.

            clang_path = btchk.check_tool("clang")

            # Check if kernel sources provide 'bpftool' first. The user could have compiled it in
            # the kernel tree. Use it, if so.
            bpftool_path = None
            for path in ("bpftool", "tools/bpf/bpftool/bpftool"):
                if self._bpman.is_file(self._ksrc / path):
                    bpftool_path = self._ksrc / path
                    break
            if not bpftool_path:
                bpftool_path = btchk.check_tool("bpftool")

            # Check for 'libbpf' library. We do this because the OS package that brings 'libbpf.so'
            # ('libbpf-devel' in Fedora) also brings headers like 'bpf/bpf_helper_defs.h', which are
            # required.
            self._check_for_shared_library("bpf")

            headers = ("bpf/bpf_helpers.h", "bpf_helper_defs.h", "bpf/bpf_tracing.h",
                       "uapi/linux/bpf.h", "linux/version.h", "asm/types.h")
            incdirs = self._find_ebpf_include_dirs(headers)
            bpf_inc = "-I " + " -I ".join([str(incdir) for incdir in incdirs])

            # Build the eBPF components of eBPF helpers.
            for bpfhelper in helpers:
                _LOG.info("Compiling the eBPF component of '%s'%s", bpfhelper, self._bpman.hostmsg)
                cmd = f"make -C '{self._btmpdir}/{bpfhelper}' KSRC='{self._ksrc}' " \
                      f"CLANG='{clang_path}' BPFTOOL='{bpftool_path}' BPF_INC='{bpf_inc}' bpf"
                stdout, stderr = self._bpman.run_verify(cmd)
                self._log_cmd_output(stdout, stderr)

        libbpf_path, u_inc = None, None
        if not self._bpman.is_remote and self._spman.is_remote:
            # We are building on a local system for a remote host. Everything should come from
            # kernel sources in this case: 'libbpf.a' and 'bpf/bpf.h'.
            libbpf_path = self._find_or_build_libbpf_a_from_ksrc()
            incdirs = self._find_ebpf_include_dirs(("bpf/bpf.h", ))
            u_inc = "-I " + " -I ".join([str(incdir) for incdir in incdirs])
        else:
            # We are building on the SUT for the kernel running on the SUT. In this case we assume
            # that libbpf is installed on the system via an OS kernel package, and we use the shared
            # 'libbpf' library.
            self._check_for_shared_library("bpf")

        # Build eBPF helpers.
        for bpfhelper in helpers:
            _LOG.info("Compiling eBPF helper '%s'%s", bpfhelper, self._bpman.hostmsg)
            cmd = f"make -C '{self._btmpdir}/{bpfhelper}'"
            if libbpf_path:
                # Note, in case of static libbpf library, we have to specify 'libelf' adn 'libz'
                # linker flags, because 'libbpf.a' requires them.
                cmd += f" LIBBPF='{libbpf_path}' U_INC='{u_inc}' LDFLAGS='-lz -lelf'"
            stdout, stderr = self._bpman.run_verify(cmd)
            self._log_cmd_output(stdout, stderr)

    def __init__(self, prjname, toolname, ksrc,  rebuild_src, spman, bpman, stmpdir, btmpdir,
                 btchk=None, debug=False):
        """
        Class constructor. Arguments are the same as in 'DeployHelpersBase.DeployHelpersBase()'
        except for:
         * ksrc - path to the kernel sources to compile drivers against.
         * rebuild_src - boolean value representing whether this method should rebuild bpf helpers.
        """

        self._ksrc = ksrc
        self._rebuild_src = rebuild_src

        what = f"{toolname} eBPF helpers"
        super().__init__(prjname, toolname, what, spman, bpman, stmpdir, btmpdir, btchk=btchk,
                         debug=debug)
