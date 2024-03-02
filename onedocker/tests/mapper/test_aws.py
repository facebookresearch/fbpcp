#!/usr/bin/env python3
# Copyright (c) Meta Platforms, Inc. and affiliates.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

# pyre-unsafe

import unittest

from onedocker.entity.measurement import MeasurementType
from onedocker.entity.metadata import PackageMetadata
from onedocker.mapper.aws import map_dynamodbitem_to_packagemetadata


class TestAWSMapper(unittest.TestCase):
    def test_map_dynamodbitem_to_packagemetadata(self):
        # Arrange
        test_package_name = "PA"
        test_package_version = "0.0.1"
        test_sha256_measurement = "123"
        test_dynamodb_item = {
            "package_name": test_package_name,
            "version": test_package_version,
            "measurements": {"sha256": test_sha256_measurement},
        }
        expect_res = PackageMetadata(
            package_name=test_package_name,
            version=test_package_version,
            measurements={MeasurementType.sha256: test_sha256_measurement},
        )

        # Act
        res = map_dynamodbitem_to_packagemetadata(dynamodb_item=test_dynamodb_item)

        # Assert
        self.assertEqual(expect_res, res)
