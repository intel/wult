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
from pepclibs.helperlibs.Exceptions import Error, ErrorNotSupported
from statscollectlibs.collector import _STCAgent

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
    def _validate_collectors(subcfg):
        """
        Helper function for '_validate_suts()'. Validates the contents of a "collectors" section in
        the configuration file. The section of the configuration file is provided in dictionary form
        as 'subcfg'.
        """

        configurable_attrs = {
            "interval": int,
            "enabled": bool,
            "toolpath": str,
            "props": dict
        }

        if subcfg is None:
            raise Error(f"\"collectors\" section specified without configuring any collectors. "
                        f"Configurable collector names are:\n  '{', '.join(_STCAgent.STINFO)}'")

        for stname, stinfo in subcfg.items():
            if stname not in _STCAgent.STINFO:
                raise ErrorNotSupported(f"config file specified unsupported statistics collector "
                                        f"'{stname}'. Configurable collector names are:\n  "
                                        f"'{', '.join(_STCAgent.STINFO)}'")

            if stinfo is None:
                raise Error(f"statistics collector '{stname}' specified without specifying any "
                            f"collector attributes. Configurable attributes are:\n  "
                            f"'{', '.join(configurable_attrs)}'")

            for attr, val in stinfo.items():
                if attr not in configurable_attrs:
                    raise Error(f"unconfigurable attribute '{attr}' specified for '{stname}' "
                                f"collector. Configurable attributes are:\n  "
                                f"'{', '.join(configurable_attrs)}'")

                if not isinstance(val, configurable_attrs[attr]):
                    raise Error(f"invalid value '{val}' for '{attr}'. Value should be of type "
                                f"'{configurable_attrs[attr].__name__}'.")

    def _validate_suts(self, subcfg):
        """
        Helper function for '_validate_loaded_cfg()'. Validates the contents of the "suts" section
        of the configuration file. The section of the configuration file is provided in dictionary
        form as 'subcfg'.
        """

        if subcfg is None:
            raise Error("\"suts\" section specified without specifying any SUTs.")

        valid_keys = ("collectors",)
        for sutname, sutinfo in subcfg.items():
            if sutinfo is None:
                raise Error(f"SUT '{sutname}' specified without specifying any keys. Valid keys "
                            f"are:\n  '{', '.join(valid_keys)}'")

            for key in sutinfo:
                if key in valid_keys:
                    try:
                        self._validate_collectors(sutinfo["collectors"])
                    except Error as err:
                        raise Error(f"invalid configuration for SUT '{sutname}':\n"
                                    f"{err.indent(2)}") from None
                else:
                    raise Error(f"invalid key '{key}' for SUT '{sutname}', valid keys are:\n"
                                f"  '{', '.join(valid_keys)}'")

    def _validate_loaded_cfg(self, cfg, path):
        """
        Helper function for '_iterate_configs()'. Validates the contents of loaded configuration
        files. If the contents are deemed invalid, an appropriate error will be raised. Arguments
        are as follows:
         * cfg - dictionary representation of the loaded configuration file.
         * path - path of the loaded configuration file.
        """

        if "suts" not in cfg:
            _LOG.warning("\"suts\" section was not found in configuration file '%s'", path)
            return

        try:
            self._validate_suts(cfg["suts"])
        except Error as err:
            raise Error(f"invalid configuration file at '{path}':\n{err.indent(2)}") from None

    def _iterate_configs(self):
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
                cfg = YAML.load(path)
                self._validate_loaded_cfg(cfg, path)
                yield cfg

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
