#!/usr/bin/env python3
# Copyright (c) Meta Platforms, Inc. and affiliates.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

import unittest

from onedocker.entity.checksum_type import ChecksumType
from onedocker.service.checksum import LocalChecksumGenerator


class TestLocalChecksumGenerator(unittest.TestCase):
    def setUp(self):
        self.checksum_service = LocalChecksumGenerator()

    def test_generate_checksum(self):
        # Arrange
        test_path = "/usr/bin/ls"

        algorithms = [ChecksumType.MD5, ChecksumType.SHA256]

        test_dict = {
            "MD5": "",
            "SHA256": "",
        }

        # Act
        act_dict = self.checksum_service.generate_checksums(test_path, algorithms)

        # Assert
        self.assertEqual(test_dict.keys(), act_dict.keys())

    def test_generate_checksum_no_args(self):
        # Arrange
        test_path = "/usr/bin/ls"

        algorithms = []

        # Act & Assert
        with self.assertRaises(ValueError):
            self.checksum_service.generate_checksums(test_path, algorithms)
