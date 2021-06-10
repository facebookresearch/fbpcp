#!/usr/bin/env python3
# Copyright (c) Facebook, Inc. and its affiliates.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

import subprocess
import unittest

from onedocker.common.util import run_cmd


class TestUtil(unittest.TestCase):
    def test_run_cmd(self):
        self.assertEqual(0, run_cmd("cat", 1))

    def test_run_cmd_with_timeout(self):
        self.assertRaises(subprocess.TimeoutExpired, run_cmd, "vi", 1)
