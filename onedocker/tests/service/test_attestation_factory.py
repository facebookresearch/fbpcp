#!/usr/bin/env python3
# Copyright (c) Meta Platforms, Inc. and affiliates.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

import unittest
from typing import Dict
from unittest.mock import MagicMock, patch

from onedocker.entity.attestation_document import (
    AttestationDocument,
    AttestationPolicy,
    PolicyName,
    PolicyParams,
)

from onedocker.service.attestation_factory import AttestationFactoryService

TEST_PACKAGE: str = "echo"
TEST_VERSION: str = "1.0"
TEST_PARAMS: PolicyParams = PolicyParams(
    package_name=TEST_PACKAGE, version=TEST_VERSION
)
TEST_POLICY: AttestationPolicy = AttestationPolicy(
    policy_name=PolicyName.BINARY_MATCH, params=TEST_PARAMS
)
TEST_MEASUREMENTS: Dict[str, str] = {"MD5": "md5-hash"}


class TestAttestationFactory(unittest.TestCase):
    def setUp(self) -> None:
        self.attestation_factory_service = AttestationFactoryService()

    @patch(
        "onedocker.service.attestation_factory.AttestationFactoryService._get_attestation_service"
    )
    def test_validate(self, mock_get_attestation_service) -> None:
        # Arrange
        mock_get_attestation_service.return_value.validate = MagicMock(
            return_value=True
        )
        test_document = AttestationDocument(
            policy=TEST_POLICY, measurements=TEST_MEASUREMENTS
        )
        # Act
        result = self.attestation_factory_service.validate(test_document.to_json())
        # Assert
        mock_get_attestation_service.assert_called_once_with(test_document.policy)
        self.assertEqual(result, True)

    def test_validate_invalid_document(self) -> None:
        # Arrange
        test_document = "invalid-document"
        # Act and Assert
        with self.assertRaises(ValueError):
            self.attestation_factory_service.validate(test_document)

    @patch("onedocker.service.attestation_factory.PCAttestationService")
    def test_get_attestation_service(self, MockPCAttestationService) -> None:
        # Arrange
        expected_service = MagicMock()
        MockPCAttestationService.return_value = expected_service
        # Act
        service = self.attestation_factory_service._get_attestation_service(TEST_POLICY)
        # Assert
        self.assertEqual(service, expected_service)

    def test_get_attestation_service_unsupported_policy(self) -> None:
        # Arrange
        test_policy = AttestationPolicy(
            # pyre-ignore
            policy_name="unsupported-policy",
            params=TEST_PARAMS,
        )
        # Act and Assert
        with self.assertRaises(NotImplementedError):
            self.attestation_factory_service._get_attestation_service(test_policy)
