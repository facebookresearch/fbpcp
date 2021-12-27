#!/usr/bin/env python3
# Copyright (c) Meta Platforms, Inc. and affiliates.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

import unittest

from fbpcp.util.gcspath import GCSPath


class TestGCSPath(unittest.TestCase):
    def test_gcspath_no_subfolder(self):
        test_gcspath = GCSPath("https://storage.cloud.google.com/bucket-name/key-name")
        self.assertEqual(test_gcspath.bucket, "bucket-name")
        self.assertEqual(test_gcspath.key, "key-name")

    def test_gcspath_with_subfoler(self):
        test_gcspath = GCSPath(
            "https://storage.cloud.google.com/bucket-name/subfolder/key"
        )
        self.assertEqual(test_gcspath.bucket, "bucket-name")
        self.assertEqual(test_gcspath.key, "subfolder/key")

    def test_gcspath_invalid_fileURL(self):
        test_url = "an invalid fileURL"
        with self.assertRaises(ValueError):
            GCSPath(test_url)
