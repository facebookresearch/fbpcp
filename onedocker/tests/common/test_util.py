#!/usr/bin/env python3
# Copyright (c) Meta Platforms, Inc. and affiliates.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

# pyre-strict

import subprocess
import unittest
from unittest.mock import MagicMock

from onedocker.common.util import run_cmd


class TestUtil(unittest.TestCase):
    def test_run_cmd(self) -> None:
        self.assertEqual(0, run_cmd("cat", 1, None))

    def test_run_cmd_with_timeout(self) -> None:
        self.assertRaises(subprocess.TimeoutExpired, run_cmd, "vi", 1, None)

    def test_run_cmd_with_preexec_fn(self) -> None:
        self.assertRaises(
            subprocess.SubprocessError,
            run_cmd,
            "cat",
            1,
            MagicMock(side_effect=Exception),
        )
