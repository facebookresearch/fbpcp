#!/usr/bin/env python3
# Copyright (c) Facebook, Inc. and its affiliates.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

import json
import unittest
from unittest.mock import patch, mock_open

from fbpcp.util.yaml import load, dump

TEST_FILENAME = "TEST_FILE"
TEST_DICT = {
    "test_dict": [
        {"test_key_1": "test_value_1"},
        {"test_key_1": "test_value_2"},
    ]
}


class TestYaml(unittest.TestCase):
    data = json.dumps(TEST_DICT)

    @patch("builtins.open", new_callable=mock_open, read_data=data)
    def test_load(self, mock_file):
        self.assertEqual(open(TEST_FILENAME).read(), self.data)
        load_data = load(TEST_FILENAME)
        self.assertEqual(load_data, TEST_DICT)
        mock_file.assert_called_with(TEST_FILENAME)

    @patch("builtins.open")
    @patch("yaml.dump")
    def test_dump(self, mock_dump, mock_open):
        mock_dump.return_value = None
        stream = mock_open().__enter__.return_value
        self.assertIsNone(dump(TEST_DICT, TEST_FILENAME))
        mock_open.assert_called_with(TEST_FILENAME, "w")
        mock_dump.assert_called_with(TEST_DICT, stream)
