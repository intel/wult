# -*- coding: utf-8 -*-
# vim: ts=4 sw=4 tw=100 et ai si
#
# Copyright (C) 2022 Intel Corporation
# SPDX-License-Identifier: BSD-3-Clause
#
# Authors: Adam Hawley <adam.james.hawley@intel.com>

"""
This module provides the API for parsing and reading statistics collection configuration files.
"""

import logging
from pathlib import Path
from pepclibs.helperlibs import YAML

_SYSTEM_CFG_FILE = "/etc/statscollect.conf"
_USER_CFG_FILE_NAME = ".statscollect.conf"

_LOG = logging.getLogger()

class StatsConfig:
    """
    This class provides the API for parsing and reading statistics collection configuration files.
    """

    def get_sut_cfg(self, sutname):
        """
        Returns a dictionary containing names of statistics with configured properties in the
        following format:
            { stname: { property: value,
                        ... etc ...},
              ... etc ... }
        Returns an empty dictionary if no configuration file specifies any statistic names for
        'sutname'.
        """

        if sutname not in self._cfg.get("suts", {}):
            return {}

        return self._cfg["suts"][sutname].get("collectors", {})

    @staticmethod
    def _iterate_configs():
        """
        Helper function for '_parse_config_files()'. For every existing statistics configuration
        file, parse and yield the contents as a dictionary.
        """

        paths = [Path(_SYSTEM_CFG_FILE)]
        try:
            paths.append(Path.home() / _USER_CFG_FILE_NAME)
        except RuntimeError as err:
            _LOG.debug("error occured while resolving home directory, skipping check for '~/%s':"
                       "\n%s", _USER_CFG_FILE_NAME, err)

        for path in paths:
            if path.is_file():
                yield YAML.load(path)

    def _parse_config_files(self):
        """
        Returns an aggregate dictionary representation of the parsed statistics configuration files.
        """

        cfg = {"suts": {}}
        for cfg in self._iterate_configs():
            cfg.update(cfg)

        return cfg

    def __init__(self):
        """
        Class constructor. Loads configuration files at '/etc/stats-collect.config' and
        '~/.stats-collect.config'.

        Firstly, the configuration file in '/etc/' is read, followed by the configuration file in
        the user's home. Settings configured in the config file in the home directory will overwrite
        settings configured in '/etc/'.
        """

        self._cfg = self._parse_config_files()
