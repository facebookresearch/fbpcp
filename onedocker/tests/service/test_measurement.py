# Copyright (c) Meta Platforms, Inc. and affiliates.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

# pyre-unsafe

import hashlib
import unittest
from unittest.mock import mock_open, patch

from onedocker.entity.measurement import MeasurementType

from onedocker.service.measurement import MeasurementService


class TestMeasurementService(unittest.TestCase):
    def setUp(self) -> None:
        self.measurement_svc = MeasurementService()

    def test_generate_measurements(self):
        # Arrange
        test_binary = b"123"
        test_path = "test_path"
        test_measurement_types = [MeasurementType.sha256, MeasurementType.sha512]
        expect_hash_sha256 = hashlib.sha256(test_binary).hexdigest()
        expect_hash_sha512 = hashlib.sha512(test_binary).hexdigest()
        expect_res = {
            MeasurementType.sha256: expect_hash_sha256,
            MeasurementType.sha512: expect_hash_sha512,
        }
        open_mock = mock_open(read_data=test_binary)

        # Act
        with patch("builtins.open", open_mock, create=True):
            result = self.measurement_svc.generate_measurements(
                measurement_types=test_measurement_types, file_path=test_path
            )

        # Assert
        self.assertEqual(expect_res, result)
