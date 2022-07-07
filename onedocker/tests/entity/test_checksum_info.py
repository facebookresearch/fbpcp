#!/usr/bin/env python3
# Copyright (c) Meta Platforms, Inc. and affiliates.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

import unittest

from onedocker.entity.checksum_info import ChecksumInfo


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

    def test_eq_self(self):
        self.assertEqual(self.good_checksum, self.good_checksum)

    def test_eq_dict(self):
        checksum_info = {
            "package_name": self.TEST_PACKAGE_NAME,
            "version": self.TEST_VERSION,
            "checksums": self.TEST_CHECKSUMS,
        }

        self.assertEqual(self.good_checksum, ChecksumInfo(**checksum_info))

    def test_eq_asdict(self):
        checksum_info = {
            "package_name": self.TEST_PACKAGE_NAME,
            "version": self.TEST_VERSION,
            "checksums": self.TEST_CHECKSUMS,
        }

        self.assertDictEqual(self.good_checksum.asdict(), checksum_info)

    def test_eq_package_name(self):
        checksum_info = {
            "package_name": "bad_package_name",
            "version": self.TEST_VERSION,
            "checksums": self.TEST_CHECKSUMS,
        }

        self.assertNotEqual(self.good_checksum, ChecksumInfo(**checksum_info))

    def test_eq_version(self):
        checksum_info = {
            "package_name": self.TEST_PACKAGE_NAME,
            "version": "bad_version",
            "checksums": self.TEST_CHECKSUMS,
        }

        self.assertNotEqual(self.good_checksum, ChecksumInfo(**checksum_info))

    def test_eq_checksum(self):
        checksum_info = {
            "package_name": self.TEST_PACKAGE_NAME,
            "version": self.TEST_VERSION,
            "checksums": {
                "MD5": "invalid_md5_goes_here",
                "SHA256": "valid_sha256_goes_here",
                "BLAKE2B": "valid_blake2b_goes_here",
            },
        }

        self.assertNotEqual(self.good_checksum, ChecksumInfo(**checksum_info))

    def test_eq_no_matching_checksum(self):
        checksum_info = {
            "package_name": self.TEST_PACKAGE_NAME,
            "version": self.TEST_VERSION,
            "checksums": {
                "NOT_MD5": "valid_not_md5_goes_here",
                "NOT_SHA256": "valid_not_sha256_goes_here",
                "NOT_BLAKE2B": "valid_not_blake2b_goes_here",
            },
        }

        self.assertNotEqual(self.good_checksum, ChecksumInfo(**checksum_info))

    def test_eq_checksum_nonmatching_amount(self):
        checksum_info = {
            "package_name": self.TEST_PACKAGE_NAME,
            "version": self.TEST_VERSION,
            "checksums": {
                "SHA256": "valid_sha256_goes_here",
                "BLAKE2B": "valid_blake2b_goes_here",
            },
        }

        self.assertEqual(self.good_checksum, ChecksumInfo(**checksum_info))
