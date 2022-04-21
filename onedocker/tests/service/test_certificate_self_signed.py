#!/usr/bin/env python3
# Copyright (c) Meta Platforms, Inc. and affiliates.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

import unittest
from unittest.mock import MagicMock, patch

from fbpcp.entity.certificate_request import KeyAlgorithm, CertificateRequest
from onedocker.service.certificate_self_signed import SelfSignedCertificateService

TEST_CERT_FOLDER = "certificate_test"
TEST_CERTIFICATE_NAME = "certificate.pem"
TEST_KEY_ALGORITHM = KeyAlgorithm.RSA
TEST_KEY_SIZE = 4096
TEST_PASSPHRASE = "test"
TEST_COUNTRY_NAME = "US"
TEST_STATE_OR_PROVINCE_NAME = "California"
TEST_LOCALITY_NAME = "San Francisco"
TEST_ORGANIZATION_NAME = "OneDocker"
TEST_COMMON_NAME = "test_site.com"
TEST_DNS_NAME = "localhost"
TEST_ROOT_PATH = "/root/onedocker"


class TestSelfSignedCertificateService(unittest.TestCase):
    def setUp(self):
        test_cert_request = CertificateRequest(
            key_algorithm=TEST_KEY_ALGORITHM,
            key_size=TEST_KEY_SIZE,
            passphrase=TEST_PASSPHRASE,
            cert_folder=TEST_CERT_FOLDER,
            private_key_name=None,
            certificate_name=None,
            days_valid=None,
            country_name=TEST_COUNTRY_NAME,
            state_or_province_name=TEST_STATE_OR_PROVINCE_NAME,
            locality_name=TEST_LOCALITY_NAME,
            organization_name=TEST_ORGANIZATION_NAME,
            common_name=TEST_COMMON_NAME,
            dns_name=TEST_DNS_NAME,
        )
        exe_path = TEST_ROOT_PATH
        self.cert_svc = SelfSignedCertificateService(test_cert_request, exe_path)

    @patch("os.makedirs")
    def test_generate_certificate(self, mock_makedirs) -> None:
        # Arrange

        self.cert_svc._write_bytes_to_file = MagicMock()
        expect_path = "/".join([TEST_ROOT_PATH, TEST_CERT_FOLDER])

        # Act
        cert_pem = self.cert_svc.generate_certificate()

        # Assert
        self.assertEqual(cert_pem, expect_path)
