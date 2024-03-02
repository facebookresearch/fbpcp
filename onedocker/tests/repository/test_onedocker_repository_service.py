#!/usr/bin/env python3
# Copyright (c) Meta Platforms, Inc. and affiliates.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

# pyre-unsafe

import unittest
from unittest.mock import MagicMock, patch

from onedocker.entity.measurement import MeasurementType

from onedocker.entity.metadata import PackageMetadata
from onedocker.repository.onedocker_repository_service import (
    DEFAULT_PROD_VERSION,
    OneDockerRepositoryService,
)


class TestOneDockerRepositoryService(unittest.TestCase):
    TEST_PACKAGE_PATH = "private_lift/lift"
    TEST_PACKAGE_NAME = TEST_PACKAGE_PATH.split("/")[-1]
    TEST_PACKAGE_VERSION = "1.0"
    TEST_MEASUREMENT_KEY1 = "sha512"
    TEST_MEASUREMENT_KEY2 = "sha256"
    TEST_MEASUREMENT1 = "sha512-hash"
    TEST_MEASUREMENT2 = "sha256-hash"

    @patch(
        "onedocker.repository.onedocker_repository_service.OneDockerPackageRepository"
    )
    @patch("fbpcp.service.storage_s3.S3StorageService")
    @patch("onedocker.service.metadata.MetadataService")
    @patch("onedocker.service.measurement.MeasurementService")
    def setUp(
        self,
        MockMeasurementService,
        MockMetadataService,
        MockStorageService,
        MockPackageRepoCall,
    ) -> None:
        package_repo_path = "/package_repo_path/"
        self.package_repo = MagicMock()
        MockPackageRepoCall.return_value = self.package_repo
        self.repo_service = OneDockerRepositoryService(
            MockStorageService, package_repo_path, MockMetadataService
        )
        self.metadata_service = MockMetadataService
        self.repo_service.measurement_svc = MockMeasurementService()

    def test_onedocker_repo_service_upload(self) -> None:
        # Arrange
        source_path = "test_source_path"
        expected_measurements = {
            MeasurementType(self.TEST_MEASUREMENT_KEY1): self.TEST_MEASUREMENT1,
            MeasurementType(self.TEST_MEASUREMENT_KEY2): self.TEST_MEASUREMENT2,
        }
        self.repo_service.measurement_svc.generate_measurements = MagicMock(
            return_value=expected_measurements
        )

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

    def test_get_package_measurements(self) -> None:
        # Arrange
        self.metadata_service.get_medadata.return_value = PackageMetadata(
            package_name=self.TEST_PACKAGE_NAME,
            version=self.TEST_PACKAGE_VERSION,
            measurements={
                MeasurementType(self.TEST_MEASUREMENT_KEY1): self.TEST_MEASUREMENT1,
                MeasurementType(self.TEST_MEASUREMENT_KEY2): self.TEST_MEASUREMENT2,
            },
        )
        expect_res = {
            self.TEST_MEASUREMENT_KEY1: self.TEST_MEASUREMENT1,
            self.TEST_MEASUREMENT_KEY2: self.TEST_MEASUREMENT2,
        }

        # Act
        res = self.repo_service.get_package_measurements(
            package_name=self.TEST_PACKAGE_NAME, version=self.TEST_PACKAGE_VERSION
        )

        # Assert
        self.assertEqual(expect_res, res)
        self.metadata_service.get_medadata.assert_called_with(
            package_name=self.TEST_PACKAGE_NAME, version=self.TEST_PACKAGE_VERSION
        )
