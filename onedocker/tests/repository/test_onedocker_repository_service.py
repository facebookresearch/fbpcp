#!/usr/bin/env python3
# Copyright (c) Meta Platforms, Inc. and affiliates.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

import json

import unittest
from unittest.mock import MagicMock, patch

from onedocker.repository.onedocker_repository_service import (
    DEFAULT_PROD_VERSION,
    OneDockerRepositoryService,
)


class TestOneDockerRepositoryService(unittest.TestCase):
    TEST_PACKAGE_PATH = "private_lift/lift"
    TEST_PACKAGE_NAME = TEST_PACKAGE_PATH.split("/")[-1]
    TEST_PACKAGE_VERSION = "1.0"

    @patch("onedocker.repository.onedocker_repository_service.OneDockerMetadataService")
    @patch(
        "onedocker.repository.onedocker_repository_service.OneDockerPackageRepository"
    )
    @patch("onedocker.repository.onedocker_repository_service.StorageService")
    def setUp(self, mockStorageService, mockPackageRepo, mockMetadataService) -> None:
        package_repo_path = "/package_repo_path/"
        self.package_repo = MagicMock()
        self.metadata_svc = MagicMock()
        mockPackageRepo.return_value = self.package_repo
        mockMetadataService.return_value = self.metadata_svc
        self.repo_service = OneDockerRepositoryService(
            mockStorageService, package_repo_path
        )
        self.storage_svc = mockStorageService

    def test_onedocker_repo_service_upload(self) -> None:
        # Arrange
        source_path = "test_source_path"

        # Act
        self.repo_service.upload(
            self.TEST_PACKAGE_PATH, self.TEST_PACKAGE_VERSION, source_path
        )

        # Assert
        self.package_repo.get_package_versions.assert_called_with(
            self.TEST_PACKAGE_PATH
        )
        self.package_repo.upload.assert_called_with(
            self.TEST_PACKAGE_PATH, self.TEST_PACKAGE_VERSION, source_path
        )

    def test_onedocker_repo_service_download(self) -> None:
        # Arrange
        destination = "test_destination_path"

        # Act
        self.repo_service.download(
            self.TEST_PACKAGE_PATH, self.TEST_PACKAGE_VERSION, destination
        )

        # Assert
        self.package_repo.download.assert_called_with(
            self.TEST_PACKAGE_PATH, self.TEST_PACKAGE_VERSION, destination
        )

    def test_onedocker_repo_service_archive(self) -> None:
        # Act
        self.repo_service.archive_package(
            self.TEST_PACKAGE_PATH, self.TEST_PACKAGE_VERSION
        )
        # Assert
        self.package_repo.archive_package.assert_called_once_with(
            self.TEST_PACKAGE_PATH, self.TEST_PACKAGE_VERSION
        )

    def test_onedocker_repo_service_upload_to_latest(self) -> None:
        # Arrange
        source_path = "test_source_path"

        # Act
        self.repo_service.upload(
            self.TEST_PACKAGE_PATH, DEFAULT_PROD_VERSION, source_path
        )

        # Assert
        self.package_repo.get_package_versions.assert_not_called()
        self.package_repo.upload.assert_called_with(
            self.TEST_PACKAGE_PATH, DEFAULT_PROD_VERSION, source_path
        )

    def test_onedocker_repo_service_set_metadata(self) -> None:
        # Arrange
        metadata_dict = {"checksum": "checksum_data", "not_a_valid_field": "some_data"}
        path = "test_metadata_path"
        self.package_repo._build_package_path.return_value = path
        # Act
        self.repo_service._set_metadata(
            self.TEST_PACKAGE_NAME, self.TEST_PACKAGE_VERSION, metadata_dict
        )
        # Assert
        self.metadata_svc.set_metadata.assert_called_once_with(path, metadata_dict)

    def test_onedocker_repo_service_get_metadata(self) -> None:
        # Arrange
        metadata_dict = {"checksum": "checksum_data"}
        metadata_json = json.dumps(metadata_dict)
        path = "test_metadata_path"
        self.package_repo._build_package_path.return_value = path
        self.storage_svc.read.return_value = metadata_json
        # Act
        self.repo_service._get_metadata(
            self.TEST_PACKAGE_NAME, self.TEST_PACKAGE_VERSION
        )
        # Assert
        self.metadata_svc.get_metadata.assert_called_once_with(path)
        # TODO: add result validation after implementing get_metadata
