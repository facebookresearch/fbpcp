#!/usr/bin/env python3
# Copyright (c) Facebook, Inc. and its affiliates.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

import unittest

from fbpcp.util.aws import (
    convert_dict_to_list,
    convert_list_to_dict,
    prepare_tags,
)

TEST_DICT = {"k1": "v1", "k2": "v2"}
TEST_LIST = [{"Name": "k1", "Value": "v1"}, {"Name": "k2", "Value": "v2"}]


class TestAWSUtil(unittest.TestCase):
    def test_convert_dict_to_list(self):
        expected_list = [
            {"Name": "k1", "Values": ["v1"]},
            {"Name": "k2", "Values": ["v2"]},
        ]
        self.assertEqual(
            expected_list, convert_dict_to_list(TEST_DICT, "Name", "Values")
        )
        self.assertEqual([], convert_dict_to_list({}, "Name", "Values"))

    def test_convert_list_dict(self):
        self.assertEqual(TEST_DICT, convert_list_to_dict(TEST_LIST, "Name", "Value"))

    def test_prepare_tags(self):
        expected_tags = {"tag:k1": "v1", "tag:k2": "v2"}
        self.assertEqual(expected_tags, prepare_tags(TEST_DICT))
