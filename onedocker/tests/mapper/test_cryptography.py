#!/usr/bin/env python3
# Copyright (c) Meta Platforms, Inc. and affiliates.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

import unittest

from cryptography import x509
from cryptography.x509.oid import NameOID
from fbpcp.entity.certificate_request import CertificateRequest, KeyAlgorithm
from onedocker.mapper.cryptography import (
    map_certificaterequest_to_x509name,
    map_certificaterequest_to_x509subjectalternativename,
)

TEST_KEY_ALGORITHM = KeyAlgorithm.RSA
TEST_KEY_SIZE = 4096
TEST_PASSPHRASE = "test"
TEST_COUNTRY_NAME = "US"
TEST_STATE_OR_PROVINCE_NAME = "California"
TEST_LOCALITY_NAME = "San Francisco"
TEST_ORGANIZATION_NAME = "OneDocker"
TEST_COMMON_NAME = "test_site.com"
TEST_DNS_NAME = "localhost"


class TestCryptographyMapper(unittest.TestCase):
    def setUp(self):
        self.test_cert_request = CertificateRequest(
            key_algorithm=TEST_KEY_ALGORITHM,
            key_size=TEST_KEY_SIZE,
            passphrase=TEST_PASSPHRASE,
            cert_folder=None,
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

    def test_map_certificaterequest_to_x509name(self):
        # Arrange

        expected_x509_name = x509.Name(
            [
                x509.NameAttribute(NameOID.COUNTRY_NAME, TEST_COUNTRY_NAME),
                x509.NameAttribute(
                    NameOID.STATE_OR_PROVINCE_NAME, TEST_STATE_OR_PROVINCE_NAME
                ),
                x509.NameAttribute(NameOID.LOCALITY_NAME, TEST_LOCALITY_NAME),
                x509.NameAttribute(NameOID.ORGANIZATION_NAME, TEST_ORGANIZATION_NAME),
                x509.NameAttribute(NameOID.COMMON_NAME, TEST_COMMON_NAME),
            ]
        )

        # Act
        test_x509_name = map_certificaterequest_to_x509name(self.test_cert_request)

        # Assert
        self.assertEqual(expected_x509_name, test_x509_name)

    def test_map_certificaterequest_to_x509subjectalternativename(self):
        # Arrange
        expected_x509_san = x509.SubjectAlternativeName([x509.DNSName(TEST_DNS_NAME)])

        # Act
        test_x509_san = map_certificaterequest_to_x509subjectalternativename(
            self.test_cert_request
        )

        # Assert
        self.assertEqual(expected_x509_san, test_x509_san)
