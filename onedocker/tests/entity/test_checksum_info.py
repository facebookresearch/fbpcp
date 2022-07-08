#!/usr/bin/env python3
# Copyright (c) Meta Platforms, Inc. and affiliates.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

import unittest

from onedocker.entity.checksum_info import ChecksumInfo
from onedocker.entity.checksum_type import ChecksumType


class TestChecksumInfo(unittest.TestCase):
    TEST_PACKAGE_NAME = "ls"
    TEST_VERSION = "latest"
    TEST_CHECKSUMS = {
        "MD5": "valid_md5_goes_here",
        "SHA256": "valid_sha256_goes_here",
        "BLAKE2B": "valid_blake2b_goes_here",
    }

    def setUp(self):
        self.good_checksum = ChecksumInfo(
            package_name=self.TEST_PACKAGE_NAME,
            version=self.TEST_VERSION,
            checksums=self.TEST_CHECKSUMS,
        )

    def test_init(self):
        checksum_info = ChecksumInfo(
            self.TEST_PACKAGE_NAME,
            self.TEST_VERSION,
            {
                "MD5": "valid_md5_goes_here",
                "SHA256": "valid_sha256_goes_here",
                "BLAKE2B": "valid_blake2b_goes_here",
            },
        )
        checksum_dict = checksum_info.asdict()

        self.assertEqual(checksum_dict["package_name"], self.TEST_PACKAGE_NAME)
        self.assertEqual(checksum_dict["version"], self.TEST_VERSION)
        self.assertEqual(checksum_dict["checksums"], self.TEST_CHECKSUMS)

    def test_init_bad_types(self):
        checksum_info = {
            "package_name": self.TEST_PACKAGE_NAME,
            "version": self.TEST_VERSION,
            "checksums": {
                "NOT_MD5": "valid_not_md5_goes_here",
                "NOT_SHA256": "valid_not_sha256_goes_here",
                "NOT_BLAKE2B": "valid_not_blake2b_goes_here",
            },
        }

        with self.assertRaises(ValueError):
            ChecksumInfo(**checksum_info)

    def test_post_init(self):
        checksum_info = ChecksumInfo(
            self.TEST_PACKAGE_NAME,
            self.TEST_VERSION,
            {
                ChecksumType("MD5"): "valid_md5_goes_here",
                ChecksumType("SHA256"): "valid_sha256_goes_here",
                ChecksumType("BLAKE2B"): "valid_blake2b_goes_here",
            },
        )
        checksum_dict = checksum_info.asdict()

        self.assertEqual(checksum_dict["package_name"], self.TEST_PACKAGE_NAME)
        self.assertEqual(checksum_dict["version"], self.TEST_VERSION)
        self.assertEqual(checksum_dict["checksums"], self.TEST_CHECKSUMS)
