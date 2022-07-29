#!/usr/bin/env python3
# Copyright (c) Meta Platforms, Inc. and affiliates.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

import unittest
from unittest.mock import MagicMock, patch

from onedocker.repository.onedocker_repository_service import OneDockerRepositoryService


class TestOneDockerRepositoryService(unittest.TestCase):
    TEST_PACKAGE_PATH = "private_lift/lift"
    TEST_PACKAGE_NAME = TEST_PACKAGE_PATH.split("/")[-1]
    TEST_PACKAGE_VERSION = "latest"

    @patch(
        "onedocker.repository.onedocker_repository_service.OneDockerChecksumRepository"
    )
    @patch(
        "onedocker.repository.onedocker_repository_service.OneDockerPackageRepository"
    )
    @patch("fbpcp.service.storage_s3.S3StorageService")
    def setUp(
        self, mockStorageService, mockPackageRepoCall, mockChecksumRepoCall
    ) -> None:
        package_repo_path = "/package_repo_path/"
        checksum_repo_path = "/checksum_repo_path/"
        self.package_repo = MagicMock()
        mockPackageRepoCall.return_value = self.package_repo
        self.repo_service = OneDockerRepositoryService(
            mockStorageService, package_repo_path, checksum_repo_path
        )

    def test_onedocker_repo_service_upload(self) -> None:
        # Arrange
        source_path = "test_source_path"

        # Act
        self.repo_service.upload(
            self.TEST_PACKAGE_PATH, self.TEST_PACKAGE_VERSION, source_path
        )

        # Assert
        self.package_repo.upload.assert_called_with(
            self.TEST_PACKAGE_PATH, self.TEST_PACKAGE_VERSION, source_path
        )
