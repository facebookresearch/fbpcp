#!/usr/bin/env python3
# Copyright (c) Meta Platforms, Inc. and affiliates.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

import unittest
from typing import Dict
from unittest.mock import patch

from fbpcp.error.pcp import InvalidParameterError

from onedocker.entity.attestation_document import (
    AttestationPolicy,
    PolicyName,
    PolicyParams,
)

from onedocker.service.attestation_pc import PCAttestationService

TEST_PACKAGE: str = "echo"
TEST_VERSION: str = "1.0"
TEST_MEASUREMENT_KEY1: str = "MD5"
TEST_MEASUREMENT_VALUE1: str = "md5-hash"
TEST_MEASUREMENT_KEY2: str = "SHA256"
TEST_MEASUREMENT_VALUE2: str = "sha256-hash"
TEST_MEASUREMENT1: Dict[str, str] = {TEST_MEASUREMENT_KEY1: TEST_MEASUREMENT_VALUE1}
TEST_MEASUREMENTS: Dict[str, str] = {
    TEST_MEASUREMENT_KEY1: TEST_MEASUREMENT_VALUE1,
    TEST_MEASUREMENT_KEY2: TEST_MEASUREMENT_VALUE2,
}


class TestPCAttestationService(unittest.TestCase):
    @patch("onedocker.gateway.repository_service.RepositoryServiceGateway")
    def setUp(self, MockRepositoryServiceGateway) -> None:
        self.pc_attestation_svc = PCAttestationService()

    @patch(
        "onedocker.gateway.repository_service.RepositoryServiceGateway.get_measurements"
    )
    def test_binary_match_return_true(self, mock_get_measurements) -> None:
        # Arrange
        mock_get_measurements.return_value = TEST_MEASUREMENTS
        # Act
        result = self.pc_attestation_svc.binary_match(
            package_name=TEST_PACKAGE,
            version=TEST_VERSION,
            measurements=TEST_MEASUREMENT1,
        )
        # Assert
        mock_get_measurements.assert_called_once_with(TEST_PACKAGE, TEST_VERSION)
        self.assertEqual(result, True)

    @patch(
        "onedocker.gateway.repository_service.RepositoryServiceGateway.get_measurements"
    )
    def test_binary_match_false_value(self, mock_get_measurements) -> None:
        # Arrange
        mock_get_measurements.return_value = TEST_MEASUREMENT1
        # Act
        result = self.pc_attestation_svc.binary_match(
            package_name=TEST_PACKAGE,
            version=TEST_VERSION,
            measurements={TEST_MEASUREMENT_KEY1: "false-value"},
        )
        # Assert
        mock_get_measurements.assert_called_once_with(TEST_PACKAGE, TEST_VERSION)
        self.assertEqual(result, False)

    @patch(
        "onedocker.gateway.repository_service.RepositoryServiceGateway.get_measurements"
    )
    def test_binary_match_not_found_key(self, mock_get_measurements) -> None:
        # Arrange
        mock_get_measurements.return_value = TEST_MEASUREMENT1
        # Act
        result = self.pc_attestation_svc.binary_match(
            package_name=TEST_PACKAGE,
            version=TEST_VERSION,
            measurements={"not-found-key": TEST_MEASUREMENT_VALUE1},
        )
        # Assert
        mock_get_measurements.assert_called_once_with(TEST_PACKAGE, TEST_VERSION)
        self.assertEqual(result, False)

    @patch("onedocker.service.attestation_pc.PCAttestationService.binary_match")
    def test_validate_binary_match_policy(self, mock_binary_match) -> None:
        # Arrange
        test_policy = AttestationPolicy(
            policy_name=PolicyName.BINARY_MATCH,
            params=PolicyParams(package_name=TEST_PACKAGE, version=TEST_VERSION),
        )
        test_measurements = TEST_MEASUREMENT1
        mock_binary_match.return_value = True
        # Act
        result = self.pc_attestation_svc.validate(test_policy, test_measurements)
        # Assert
        mock_binary_match.assert_called_once_with(
            TEST_PACKAGE, TEST_VERSION, test_measurements
        )
        self.assertEqual(result, True)

    def test_validate_invalid_params(self) -> None:
        # Arrange
        test_params = PolicyParams(package_name=None, version=None)
        test_policy = AttestationPolicy(
            policy_name=PolicyName.BINARY_MATCH,
            params=test_params,
        )
        # Act and Assert
        with self.assertRaises(InvalidParameterError):
            self.pc_attestation_svc.validate(test_policy, TEST_MEASUREMENT1)
