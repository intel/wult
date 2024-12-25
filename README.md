<!--
-*- coding: utf-8 -*-
vim: ts=4 sw=4 tw=100 et ai si

Copyright (C) 2019-2024 Intel, Inc.
SPDX-License-Identifier: BSD-3-Clause

Author: Artem Bityutskiy <artem.bityutskiy@linux.intel.com>
-->

# Introduction

Wult stands for "Wake Up Latency Tracer", and this is a project that provides tools for measuring
C-state latency in Linux.

# Documentation

Please, refer to the [documentation web pages](https://intel.github.io/wult) for detailed
information on the 'wult' and 'ndl' tools, how they work and what they can be used to measure.

## Installation

Steps to install the tools are included as part of the documentation web pages in the
[installation guide](https://intel.github.io/wult/pages/install-local.html).

## Usage

Command-specific documentation is available for each command of the 'wult', 'ndl' and 'exercise-sut'
tools as listed below. For more general information on how to use the tools, see the
[user guide](https://intel.github.io/wult/pages/user-guide.html).

### WULT

 * `wult scan` - [Documentation](docs/wult-scan.rst)
 * `wult deploy` - [Documentation](docs/wult-deploy.rst)
 * `wult start` - [Documentation](docs/wult-start.rst)
 * `wult report` - [Documentation](docs/wult-report.rst)
 * `wult filter` - [Documentation](docs/wult-filter.rst)
 * `wult calc` - [Documentation](docs/wult-calc.rst)

### NDL

 * `ndl scan` - [Documentation](docs/ndl-scan.rst)
 * `ndl deploy` - [Documentation](docs/ndl-deploy.rst)
 * `ndl start` - [Documentation](docs/ndl-start.rst)
 * `ndl report` - [Documentation](docs/ndl-report.rst)
 * `ndl filter` - [Documentation](docs/ndl-filter.rst)
 * `ndl calc` - [Documentation](docs/ndl-calc.rst)

### Exercise-Sut

 * `exercise-sut start` - [Documentation](docs/exercise-sut-start.rst)
 * `exercise-sut report` - [Documentation](docs/exercise-sut-report.rst)

### PBE
 * `pbe scan` - [Documentation](docs/pbe-scan.rst)
 * `pbe deploy` - [Documentation](docs/pbe-deploy.rst)
 * `pbe start` - [Documentation](docs/pbe-start.rst)
 * `pbe report` - [Documentation](docs/pbe-report.rst)

# Authors and contributors

* Artem Bityutskiy <dedekind1@gmail.com> - original author, project maintainer.
* Antti Laakso <antti.laakso@linux.intel.com> - contributor, project maintainer.
* Adam Hawley <adam.james.hawley@intel.com> - contributor.
* Tero Kristo <tero.kristo@intel.com> - contributor.
* Ali Erdinç Köroğlu <ali.erdinc.koroglu@intel.com> - contributor.
* Dapeng Mi <dapeng1.mi@intel.com> - contributor.
* Juha Haapakorpi <juha.haapakorpi@intel.com> - contributor.
* Vladislav Govtva <vlad.govtva@gmail.com> - contributor.
