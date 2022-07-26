#!/usr/bin/env python3
# Copyright (c) Meta Platforms, Inc. and affiliates.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.


import unittest
from unittest.mock import MagicMock, patch

from fbpcp.entity.file_information import FileInfo
from onedocker.entity.package_info import PackageInfo
from onedocker.repository.onedocker_package import OneDockerPackageRepository


class TestOneDockerPackageRepository(unittest.TestCase):
    TEST_PACKAGE_PATH = "project/exe_name"
    TEST_PACKAGE_NAME = TEST_PACKAGE_PATH.split("/")[-1]
    TEST_PACKAGE_VERSION = "1.0"

    @patch("fbpcp.service.storage_s3.S3StorageService")
    def setUp(self, MockStorageService):
        self.repository_url = "/abc/"
        self.onedocker_repository = OneDockerPackageRepository(
            MockStorageService, self.repository_url
        )
        self.expected_s3_dest = f"{self.repository_url}{self.TEST_PACKAGE_PATH}/{self.TEST_PACKAGE_VERSION}/{self.TEST_PACKAGE_NAME}"

    def test_onedockerrepo_upload(self):
        # Arrange
        source = "xyz"

        # Act
        self.onedocker_repository.upload(
            self.TEST_PACKAGE_PATH, self.TEST_PACKAGE_VERSION, source
        )

        # Assert
        self.onedocker_repository.storage_svc.upload_file.assert_called_with(
            source, self.expected_s3_dest, None
        )

    def test_onedockerrepo_download(self):
        # Arrange

        destination = "xyz"

        # Act
        self.onedocker_repository.download(
            self.TEST_PACKAGE_PATH, self.TEST_PACKAGE_VERSION, destination
        )

        # Assert
        self.onedocker_repository.storage_svc.copy.assert_called_with(
            self.expected_s3_dest, destination
        )

    def test_onedockerrepo_get_package_versions(self):
        # Arrange

        test_list_folders = ["1.0/bar", "2.0/bar"]
        package_parent_path = f"{self.repository_url}{self.TEST_PACKAGE_PATH}/"

        self.onedocker_repository.storage_svc.list_folders = MagicMock(
            return_value=test_list_folders
        )

        # Act
        versions = self.onedocker_repository.get_package_versions(
            self.TEST_PACKAGE_PATH
        )

        # Assert
        self.onedocker_repository.storage_svc.list_folders.assert_called_with(
            package_parent_path
        )
        self.assertEqual(test_list_folders, versions)

    def test_onedockerrepo_get_package_info_not_found(self):
        # Arrange
        self.onedocker_repository.storage_svc.file_exists = MagicMock(
            return_value=False
        )

        # Assert
        with self.assertRaises(ValueError):
            self.onedocker_repository.get_package_info(
                self.TEST_PACKAGE_PATH, self.TEST_PACKAGE_VERSION
            )

    def test_onedockerrepo_get_package_info(self):
        # Arrange

        self.onedocker_repository.storage_svc.file_exists = MagicMock(return_value=True)

        file_info = FileInfo(
            file_name="foo",
            last_modified="Sun Jan 01 01:01:05 2022",
            file_size=1048576,
        )

        self.onedocker_repository.storage_svc.get_file_info = MagicMock(
            return_value=file_info
        )

        expected_package_info = PackageInfo(
            package_name=self.TEST_PACKAGE_PATH,
            version=self.TEST_PACKAGE_VERSION,
            last_modified=file_info.last_modified,
            package_size=file_info.file_size,
        )

        # Act
        package_info = self.onedocker_repository.get_package_info(
            self.TEST_PACKAGE_PATH, self.TEST_PACKAGE_VERSION
        )

        # Assert
        self.onedocker_repository.storage_svc.get_file_info.assert_called_with(
            self.expected_s3_dest
        )

        self.assertEqual(expected_package_info, package_info)
