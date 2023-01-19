#!/usr/bin/env python3
# Copyright (c) Meta Platforms, Inc. and affiliates.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

import unittest
from unittest.mock import MagicMock, patch

from fbpcp.entity.cloud_provider import CloudProvider
from onedocker.util.service_builder import (
    build_repository_service,
    METADATA_TABLE_KEY_NAME,
    METADATA_TABLES,
)

TEST_CLOUD_PROVIDER: CloudProvider = CloudProvider.AWS
TEST_ENV: str = "STAGING"


class TestServiceBuilder(unittest.TestCase):
    @patch("onedocker.util.service_builder.MetadataService")
    @patch("onedocker.util.service_builder.OneDockerRepositoryService")
    @patch("onedocker.util.service_builder.S3StorageService")
    def test_build_repository_service(
        self, MockS3StorageService, MockRepositoryService, MockMetadataService
    ) -> None:
        # Arrange
        expected_repo_svc = MagicMock()
        MockRepositoryService.return_value = expected_repo_svc
        # Act
        repo_svc = build_repository_service(TEST_CLOUD_PROVIDER)
        # Assert
        MockS3StorageService.assert_called_once_with(
            "us-west-2", unsigned_enabled=False
        )
        MockMetadataService.assert_called_once_with(
            region="us-west-2",
            table_name=METADATA_TABLES[TEST_ENV],
            key_name=METADATA_TABLE_KEY_NAME,
        )
        self.assertEqual(repo_svc, expected_repo_svc)
