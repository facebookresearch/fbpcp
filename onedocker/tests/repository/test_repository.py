#!/usr/bin/env python3
# Copyright (c) Meta Platforms, Inc. and affiliates.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.


import hashlib
import unittest
from unittest.mock import MagicMock, patch

from fbpcp.entity.file_information import FileInfo
from onedocker.entity.package_info import PackageInfo
from onedocker.repository.onedocker_package import OneDockerPackageRepository

TEST_PACKAGE_NAME = "project/exe_name"
TEST_VERSION = "1.0"


class TestOneDockerPackageRepository(unittest.TestCase):
    @patch("fbpcp.service.storage_s3.S3StorageService")
    def setUp(self, MockStorageService):
        self.repository_path = "/abc/"
        self.onedocker_repository = OneDockerPackageRepository(
            MockStorageService, self.repository_path
        )

    def test_onedockerrepo_upload(self):
        # Arrange
        source = "xyz"

        expected_s3_dest = f"{self.repository_path}{TEST_PACKAGE_NAME}/{TEST_VERSION}/{TEST_PACKAGE_NAME.split('/')[-1]}"

        # Act
        self.onedocker_repository.upload(TEST_PACKAGE_NAME, TEST_VERSION, source)

        # Assert
        self.onedocker_repository.storage_svc.copy.assert_called_with(
            source, expected_s3_dest
        )

    def test_onedockerrepo_download(self):
        # Arrange

        destination = "xyz"

        expected_s3_dest = f"{self.repository_path}{TEST_PACKAGE_NAME}/{TEST_VERSION}/{TEST_PACKAGE_NAME.split('/')[-1]}"

        # Act
        self.onedocker_repository.download(TEST_PACKAGE_NAME, TEST_VERSION, destination)

        # Assert
        self.onedocker_repository.storage_svc.copy.assert_called_with(
            expected_s3_dest, destination
        )

    def test_onedockerrepo_get_package_versions(self):
        # Arrange

        test_list_folders = ["1.0/bar", "2.0/bar"]
        package_parent_path = f"{self.repository_path}{TEST_PACKAGE_NAME}/"

        self.onedocker_repository.storage_svc.list_folders = MagicMock(
            return_value=test_list_folders
        )

        # Act
        versions = self.onedocker_repository.get_package_versions(TEST_PACKAGE_NAME)

        # Assert
        self.onedocker_repository.storage_svc.list_folders.assert_called_with(
            package_parent_path
        )
        self.assertEqual(test_list_folders, versions)

    def test_onedockerrepo_generate_checksum(self):
        # Arrange
        expected_file_contents = "Test File Contents"
        expected_file_checksum = hashlib.sha512(
            expected_file_contents.encode("utf8")
        ).hexdigest()
        expected_file_path = f"{self.repository_path}{TEST_PACKAGE_NAME}/{TEST_VERSION}/{TEST_PACKAGE_NAME.split('/')[-1]}"
        self.onedocker_repository.storage_svc.read = MagicMock(
            return_value=expected_file_contents,
        )

        # Act
        actual_file_checksum = self.onedocker_repository.generate_checksum(
            package_name=TEST_PACKAGE_NAME,
            version=TEST_VERSION,
        )

        # Assert
        self.assertEqual(expected_file_checksum, actual_file_checksum)
        self.onedocker_repository.storage_svc.read.assert_called_with(
            expected_file_path
        )

    def test_onedockerrepo_get_package_info_not_found(self):
        # Arrange
        self.onedocker_repository.storage_svc.file_exists = MagicMock(
            return_value=False
        )

        # Assert
        with self.assertRaises(ValueError):
            self.onedocker_repository.get_package_info(TEST_PACKAGE_NAME, TEST_VERSION)

    def test_onedockerrepo_get_package_info(self):
        # Arrange
        package_path = f"{self.repository_path}{TEST_PACKAGE_NAME}/{TEST_VERSION}/{TEST_PACKAGE_NAME.split('/')[-1]}"

        expected_file_contents = "Test File Contents"
        expected_file_checksum = hashlib.sha512(
            expected_file_contents.encode("utf8")
        ).hexdigest()
        self.onedocker_repository.storage_svc.file_exists = MagicMock(return_value=True)
        self.onedocker_repository.storage_svc.read = MagicMock(
            return_value=expected_file_contents,
        )

        file_info = FileInfo(
            file_name="foo",
            last_modified="Sun Jan 01 01:01:05 2022",
            file_size=1048576,
        )

        self.onedocker_repository.storage_svc.get_file_info = MagicMock(
            return_value=file_info
        )

        expected_package_info = PackageInfo(
            package_name=TEST_PACKAGE_NAME,
            version=TEST_VERSION,
            last_modified=file_info.last_modified,
            package_size=file_info.file_size,
            checksum=expected_file_checksum,
        )

        # Act
        package_info = self.onedocker_repository.get_package_info(
            TEST_PACKAGE_NAME, TEST_VERSION
        )

        # Assert
        self.onedocker_repository.storage_svc.get_file_info.assert_called_with(
            package_path
        )

        self.assertEqual(expected_package_info, package_info)
