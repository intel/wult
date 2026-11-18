#!/usr/bin/python3
#
# -*- coding: utf-8 -*-
# vim: ts=4 sw=4 tw=100 et ai si
#
# Copyright (C) 2026 Intel Corporation
# SPDX-License-Identifier: BSD-3-Clause

"""
Test datapoint filters on metrics whose name starts with the name of another metric, e.g.,
'WakeLatencyRaw' and 'WakeLatency'.
"""

import csv
import shutil
from pathlib import Path
import pytest
from common import run_wult

_GOOD_RESULT = Path(__file__).parent / "testdata" / "wult" / "good"

@pytest.fixture
def raw_result(tmp_path):
    """
    Return a copy of the good wult test result with the 'WakeLatencyRaw' and 'IntrLatencyRaw'
    columns added after 'WakeLatency' and 'IntrLatency', like in results produced by 'wult start'.
    """

    resdir = tmp_path / "result"
    shutil.copytree(_GOOD_RESULT, resdir)
    path = resdir / "datapoints.csv"

    with path.open("r", encoding="utf-8", newline="") as fobj:
        rows = list(csv.reader(fobj))

    for base in ("WakeLatency", "IntrLatency"):
        idx = rows[0].index(base)
        for row in rows:
            row.insert(idx + 1, f"{base}Raw" if row is rows[0] else row[idx])

    with path.open("w", encoding="utf-8", newline="") as fobj:
        csv.writer(fobj).writerows(rows)

    return resdir

@pytest.mark.parametrize("args", ["--include WakeLatencyRaw>5", "--exclude IntrLatencyRaw>50"])
def test_raw_metric_filters(raw_result, tmp_path, args):
    """Test 'filter' and 'report' with datapoint filters on the 'Raw' metrics."""

    run_wult(f"filter {args} {raw_result} -o {tmp_path / 'filtered'}")
    run_wult(f"report {args} {raw_result} -o {tmp_path / 'report'}")
