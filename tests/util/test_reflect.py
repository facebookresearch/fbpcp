#!/usr/bin/env python3
# Copyright (c) Facebook, Inc. and its affiliates.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

import unittest

from fbpcp.util.reflect import get_class
from fbpcp.util.s3path import S3Path

TEST_CLASS_PATH = "fbpcp.util.s3path.S3Path"


class TestReflect(unittest.TestCase):
    def test_get_class(self):
        self.assertEqual(S3Path, get_class(TEST_CLASS_PATH))
