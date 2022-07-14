#!/usr/bin/env python3
# Copyright (c) Meta Platforms, Inc. and affiliates.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.


import unittest
from unittest.mock import MagicMock, patch

from onedocker.repository.onedocker_checksum import OneDockerChecksumRepository


class TestOneDockerChecksumRepository(unittest.TestCase):
    TEST_PACKAGE_NAME = "project/exe_name"
    TEST_PACKAGE_VERSION = "1.0"

    @patch("fbpcp.service.storage_s3.S3StorageService")
    def setUp(self, MockStorageService):
        self.checksum_repository_path = "/abc/"
        self.onedocker_checksum = OneDockerChecksumRepository(
            MockStorageService, self.checksum_repository_path
        )
        self.expected_s3_dest = f"{self.checksum_repository_path}{self.TEST_PACKAGE_NAME}/{self.TEST_PACKAGE_VERSION}/{self.TEST_PACKAGE_NAME.split('/')[-1]}.json"

    def test_onedockerrepo_write(self):
        # Arrange
        checksum_data = "xyz"

        # Act
        self.onedocker_checksum.write(
            package_name=self.TEST_PACKAGE_NAME,
            version=self.TEST_PACKAGE_VERSION,
            checksum_data=checksum_data,
        )

        # Assert
        self.onedocker_checksum.storage_svc.write.assert_called_with(
            filename=self.expected_s3_dest, data=checksum_data
        )

    def test_onedockerrepo_write_no_checksum_path(self):
        # Arrange
        checksum_data = "xyz"

        onedocker_checksum = OneDockerChecksumRepository(MagicMock(), "")

        # Act & Assert
        with self.assertRaises(ValueError):
            onedocker_checksum.write(
                package_name=self.TEST_PACKAGE_NAME,
                version=self.TEST_PACKAGE_VERSION,
                checksum_data=checksum_data,
            )
