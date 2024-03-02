#!/usr/bin/env python3
# Copyright (c) Meta Platforms, Inc. and affiliates.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

# pyre-unsafe

import json
import unittest

from fbpcp.entity.certificate_request import CertificateRequest, KeyAlgorithm
from fbpcp.error.pcp import InvalidParameterError


class TestCertificateRequest(unittest.TestCase):
    TEST_KEY_ALGORITHM = KeyAlgorithm.RSA
    TEST_KEY_SIZE = 4096
    TEST_PASSPHRASE = "test"
    TEST_ORGANIZATION_NAME = "Test Company"
    TEST_COUNTRY_NAME = "US"

    def test_create_instance(self):
        # Arrange
        expected = CertificateRequest(
            key_algorithm=self.TEST_KEY_ALGORITHM,
            key_size=self.TEST_KEY_SIZE,
            passphrase=self.TEST_PASSPHRASE,
            cert_folder=None,
            private_key_name=None,
            certificate_name=None,
            days_valid=None,
            country_name=self.TEST_COUNTRY_NAME,
            state_or_province_name=None,
            locality_name=None,
            organization_name=None,
            common_name=None,
            dns_name=None,
        )
        test_cert_params = expected.convert_to_cert_params()

        # Act
        result = CertificateRequest.create_instance(test_cert_params)

        # Assert
        self.assertEqual(expected, result)

    def test_create_instance_format_exception(self):
        # Arrange
        wrong_cert_params = "'test':"

        # Act
        # Assert
        with self.assertRaises(InvalidParameterError):
            CertificateRequest.create_instance(wrong_cert_params)

    def test_create_instance_missing_parameter_exception(self):
        # Arrange
        wrong_cert_params = str(
            {
                "key_algorithm": self.TEST_KEY_ALGORITHM.value,
                "key_size": self.TEST_KEY_SIZE,
                "organization_name": self.TEST_ORGANIZATION_NAME,
            }
        )

        # Act
        # Assert
        with self.assertRaises(InvalidParameterError):
            CertificateRequest.create_instance(wrong_cert_params)

    def test_convert_to_cert_params(self):
        # Arrange
        cert_request = CertificateRequest(
            key_algorithm=self.TEST_KEY_ALGORITHM,
            key_size=self.TEST_KEY_SIZE,
            passphrase=self.TEST_PASSPHRASE,
            cert_folder=None,
            private_key_name=None,
            certificate_name=None,
            days_valid=None,
            country_name=None,
            state_or_province_name=None,
            locality_name=None,
            organization_name=self.TEST_ORGANIZATION_NAME,
            common_name=None,
            dns_name=None,
        )
        expected_cert_params = json.dumps(
            {
                "key_algorithm": self.TEST_KEY_ALGORITHM.value,
                "key_size": self.TEST_KEY_SIZE,
                "passphrase": self.TEST_PASSPHRASE,
                "organization_name": self.TEST_ORGANIZATION_NAME,
            }
        )
        # Act
        test_cert_params = cert_request.convert_to_cert_params()

        # Assert
        self.assertEqual(test_cert_params, expected_cert_params)
