#!/usr/bin/env python3
# Copyright (c) Facebook, Inc. and its affiliates.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

import unittest

from fbpcp.util.arg_builder import build_cmd_args


class TestArgBuilder(unittest.TestCase):
    def test_build_cmd_args(self):
        expected_cmd_args = (
            "--arg1=value1 --arg2=value2 --arg3='--k1=v1 --k2=v2' --arg4=0"
        )
        self.assertEqual(
            expected_cmd_args,
            build_cmd_args(
                arg1="value1", arg2="value2", arg3="--k1=v1 --k2=v2", arg4=0, arg5=None
            ),
        )
