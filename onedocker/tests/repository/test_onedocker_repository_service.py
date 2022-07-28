#!/usr/bin/env python3
# Copyright (c) Meta Platforms, Inc. and affiliates.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

import unittest
from datetime import datetime
from unittest.mock import call, MagicMock, patch

from onedocker.entity.package_info import PackageInfo

from onedocker.repository.onedocker_repository_service import OneDockerRepositoryService


class TestOneDockerRepositoryService(unittest.TestCase):
    TEST_PACKAGE_PATH = "private_lift/lift"
    TEST_PACKAGE_NAME = TEST_PACKAGE_PATH.split("/")[-1]
    TEST_PACKAGE_VERSION = "test_version"

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
        self.package_repo_path = "/package_repo_path/"
        checksum_repo_path = "/checksum_repo_path/"
        self.package_repo = MagicMock()
        mockPackageRepoCall.return_value = self.package_repo
        self.repo_service = OneDockerRepositoryService(
            mockStorageService, self.package_repo_path, checksum_repo_path
        )
        self.storage_svc = mockStorageService
        self.package_repo.build_package_path = MagicMock(
            side_effect=self._build_package_path
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

    def _build_package_path(self, package_name: str, version: str) -> str:
        return f"{self.package_repo_path}{self.TEST_PACKAGE_NAME}/{version}/{package_name.split('/')[-1]}"

    def test_onedocker_repo_service_promote_to_latest(self) -> None:
        # Arrange
        old_version = self.TEST_PACKAGE_VERSION
        new_version = "latest"
        date = datetime.today().ctime()
        formatted_date = datetime.strftime(
            datetime.strptime(date, "%a %b %d %H:%M:%S %Y"),
            "%Y-%m-%d",
        )
        self.package_repo.get_package_info.return_value = PackageInfo(
            package_name=self.TEST_PACKAGE_NAME,
            version=old_version,
            last_modified=date,
            package_size=1,
        )
        target_path = self._build_package_path(self.TEST_PACKAGE_NAME, new_version)
        current_path = self._build_package_path(self.TEST_PACKAGE_NAME, old_version)
        archive_path = self._build_package_path(self.TEST_PACKAGE_NAME, formatted_date)
        # Act
        self.repo_service.promote(self.TEST_PACKAGE_PATH, old_version, new_version)

        # Assert
        self.storage_svc.copy.assert_has_calls(
            [call(target_path, archive_path), call(current_path, target_path)]
        )

    def test_onedocker_repo_service_promote(self) -> None:
        # Arrange
        old_version = self.TEST_PACKAGE_VERSION
        new_version = "rc"
        target_path = self._build_package_path(self.TEST_PACKAGE_NAME, new_version)
        current_path = self._build_package_path(self.TEST_PACKAGE_NAME, old_version)
        # Act
        self.repo_service.promote(self.TEST_PACKAGE_PATH, old_version, new_version)

        # Assert
        self.storage_svc.copy.assert_called_once_with(current_path, target_path)
