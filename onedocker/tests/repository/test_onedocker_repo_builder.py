#!/usr/bin/env python3
# Copyright (c) Facebook, Inc. and its affiliates.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

import unittest
from unittest.mock import patch

from fbpcp.service.storage_gcs import GCSStorageService
from fbpcp.service.storage_s3 import S3StorageService
from onedocker.repository.onedocker_repo_builder import (
    OneDockerPackageRepositoryBuilder,
)

TEST_S3_REPO = "https://bucket-name.s3.us-west-2.amazonaws.com/key"
TEST_GCS_REPO = "https://storage.cloud.google.com/bucket_name/key"


class TestOneDockerPackageRepositoryBuilder(unittest.TestCase):
    @patch("fbpcp.service.storage_s3.S3Gateway")
    def test_create_onedocker_s3_repository(self, MockS3Gateway):
        onedocker_package_repo = OneDockerPackageRepositoryBuilder.create_repository(
            repository_path=TEST_S3_REPO
        )
        self.assertIsInstance(onedocker_package_repo.storage_svc, S3StorageService)

    @patch("fbpcp.service.storage_gcs.GCSGateway")
    def test_create_onedocker_gcs_repository(self, MockGCSGateway):
        onedocker_package_repo = OneDockerPackageRepositoryBuilder.create_repository(
            repository_path=TEST_GCS_REPO
        )
        self.assertIsInstance(onedocker_package_repo.storage_svc, GCSStorageService)
