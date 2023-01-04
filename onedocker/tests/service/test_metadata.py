#!/usr/bin/env python3
# Copyright (c) Meta Platforms, Inc. and affiliates.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

import unittest
from unittest.mock import MagicMock, patch

from onedocker.entity.measurement import Measurement, MeasurementType
from onedocker.entity.metadata import PackageMetadata
from onedocker.service.metadata import MetadataService

TEST_METADATA_TABLE = "metadata_test"
TEST_METADATA_KEY = "primary_key"
TEST_REGION = "us-west-1"
TEST_KEY_ID = "test-key-id"
TEST_KEY_DATA = "test-key-data"
TEST_PACKAGE_NAME = "PL"
TEST_PACKAGE_VERSION = "1.1"
TEST_MEASUREMENT_KEY1 = "sha512"
TEST_MEASUREMENT_KEY2 = "sha256"
TEST_MEASUREMENT1 = Measurement(
    MeasurementType(TEST_MEASUREMENT_KEY1), value="sha512-hash"
)
TEST_MEASUREMENT2 = Measurement(
    MeasurementType(TEST_MEASUREMENT_KEY2), value="sha256-hash"
)


class TestMetadataService(unittest.TestCase):
    @patch("onedocker.gateway.dynamodb.DynamoDBGateway")
    def setUp(self, MockDynamoDBGateway):
        self.md_svc = MetadataService(
            region=TEST_REGION,
            table_name=TEST_METADATA_TABLE,
            key_name=TEST_METADATA_KEY,
            access_key_id=TEST_KEY_ID,
            access_key_data=TEST_KEY_DATA,
        )
        self.md_svc.dynamodb_gateway = MockDynamoDBGateway()

    def test_get_medadata(self):
        # Arrange
        expected_attributes = {
            "package_name": TEST_PACKAGE_NAME,
            "version": TEST_PACKAGE_VERSION,
            "measurements": {
                TEST_MEASUREMENT_KEY1: TEST_MEASUREMENT1,
                TEST_MEASUREMENT_KEY2: TEST_MEASUREMENT2,
            },
        }
        expect_res = PackageMetadata(
            package_name=TEST_PACKAGE_NAME,
            version=TEST_PACKAGE_VERSION,
            measurements={
                MeasurementType(TEST_MEASUREMENT_KEY1): TEST_MEASUREMENT1,
                MeasurementType(TEST_MEASUREMENT_KEY2): TEST_MEASUREMENT2,
            },
        )
        self.md_svc.dynamodb_gateway.get_item = MagicMock(
            return_value=expected_attributes
        )

        # Act
        res = self.md_svc.get_medadata(
            package_name=TEST_PACKAGE_NAME, version=TEST_PACKAGE_VERSION
        )

        # Assert
        self.assertEqual(expect_res, res)
        self.md_svc.dynamodb_gateway.get_item.assert_called()

    def test_put_medadata(self):
        # Arrange
        md_dict = {
            self.md_svc.key_name: self.md_svc._build_key(
                TEST_PACKAGE_NAME, TEST_PACKAGE_VERSION
            ),
            "package_name": TEST_PACKAGE_NAME,
            "version": TEST_PACKAGE_VERSION,
            "measurements": {
                TEST_MEASUREMENT_KEY1: TEST_MEASUREMENT1,
                TEST_MEASUREMENT_KEY2: TEST_MEASUREMENT2,
            },
        }
        md = PackageMetadata(
            package_name=TEST_PACKAGE_NAME,
            version=TEST_PACKAGE_VERSION,
            measurements={
                MeasurementType(TEST_MEASUREMENT_KEY1): TEST_MEASUREMENT1,
                MeasurementType(TEST_MEASUREMENT_KEY2): TEST_MEASUREMENT2,
            },
        )
        self.md_svc.dynamodb_gateway.put_item = MagicMock()

        # Act
        self.md_svc.put_metadata(metadata=md)

        # Assert
        self.md_svc.dynamodb_gateway.put_item.assert_called_with(
            table_name=self.md_svc.table_name, item=md_dict
        )
