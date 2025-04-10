# -*- coding: utf-8 -*-
# vim: ts=4 sw=4 tw=100 et ai si
#
# Copyright (C) 2023-2024 Intel Corporation
# SPDX-License-Identifier: BSD-3-Clause
#
# Author: Antti Laakso <antti.laakso@linux.intel.com>
#         Artem Bityutskiy <artem.bityutskiy@linux.intel.com>

"""
A helper module for the 'exercise-sut' tool to configure target system with various system property
permutations.
"""

from pepclibs import CPUIdle, CPUInfo
from pepclibs.helperlibs import Logging, ClassHelpers
from pepclibs.helperlibs import Systemctl
from wulttools.exercisesut import _Common, _CmdBuilder, _PepcCmdBuilder

_LOG = Logging.getLogger(f"{Logging.MAIN_LOGGER_NAME}.wult.{__name__}")

class BatchConfig(_Common.CmdlineRunner):
    """
    Helper class for 'exercise-sut' tool to configure and exercise SUT with different system
    configuration permutations (according to the input properties).
    """

    def deploy(self):
        """Deploy workload tool to the target system. Raise Error if tool cannot be deployed."""

        deploy_cmd = self._wcb.get_deploy_command()
        self._run_command(deploy_cmd)

    def props_to_str(self, props):
        """Convert property dictionary 'props' to human readable string."""

        return self._pcb.props_to_str(props)

    def get_props_batch(self, inprops):
        """
        Yield dictionary with system properties, with property name as key and property value as
        value. The arguments are as follows.
          * inprops - the input properties dictionary, descripting the proprties and the values that
                      should be measured.
        """

        yield from self._pcb.iter_props(inprops)

    def configure(self, props, cpu):
        """
        Configure the system for measurement. The arguments are as follows.
          * props - the measured properties and their values.
          * cpu - CPU number to configure.
        """

        for cmd in self._pcb.get_commands(props, cpu):
            self._run_command(cmd)

    def create_reportid(self, props, **kwargs):
        """
        Create and return report ID. The arguments are as follows.
          * props - the measured properties and their values.
          * kwargs - additional parameters that may affect the report ID (TODO: why 'kwargs' should
                     be used?)
        """

        return self._wcb.create_reportid(props, **kwargs)

    def run(self, props, reportid, **kwargs):
        """
        Run the measurements. The arguments are as follows.
          * props - the measured properties and their values.
          * reportid - report ID of the measurement result.
          * kwargs - additional parameters that may affect the report ID (TODO: why 'kwargs' should
                     be used?)
        """

        cmd = self._wcb.get_command(props, reportid, **kwargs)
        self._run_command(cmd)

    def __init__(self, pman, args):
        """
        The class constructor. The arguments are as follows.
          * args - the 'exercise-sut' input command line arguments.
        """

        self._cpuinfo = None
        self._cpuidle = None
        self._pcb = None
        self._wcb = None
        self._systemctl = None

        super().__init__(dry_run=args.dry_run, ignore_errors=args.ignore_errors)

        self._cpuinfo = CPUInfo.CPUInfo(pman)
        self._cpuidle = CPUIdle.CPUIdle(pman, cpuinfo=self._cpuinfo)
        self._pcb = _PepcCmdBuilder._PepcCmdBuilder(pman, self._cpuinfo, self._cpuidle, args)
        self._wcb = _CmdBuilder._get_workload_cmd_builder(self._cpuidle, args)

        self._systemctl = Systemctl.Systemctl(pman)
        if self._systemctl.is_active("tuned"):
            self._systemctl.stop("tuned", save=True)

    def close(self):
        """Uninitialize the class objetc."""

        if self._systemctl:
            self._systemctl.restore()

        ClassHelpers.close(self, close_attrs=("_pcb", "_wcb", "_systemctl"))
