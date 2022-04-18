#!/usr/bin/env python3
# Copyright (c) Meta Platforms, Inc. and affiliates.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

import unittest

from cryptography.hazmat.primitives.asymmetric.rsa import (
    RSAPrivateKeyWithSerialization,
)
from fbpcp.entity.certificate_request import KeyAlgorithm
from onedocker.entity.key_pair_details import KeyPairDetails
from onedocker.gateway.cryptography import CryptographyGateway


def write_bytes_to_file(filename: str, content: bytes) -> None:
    try:
        with open(filename, "wb") as f:
            f.write(content)
    except Exception as err:
        print(
            f"An error was raised in CertificateService while writing to file {filename}, error: {err}"
        )


class TestCryptographyGateway(unittest.TestCase):
    TEST_KEY_ALGORITHM = KeyAlgorithm.RSA
    TEST_KEY_SIZE = 4096
    TEST_PASSPHRASE = "test"

    def test_generate_key_pair(self):
        # Arrange
        gw = CryptographyGateway()

        # Act
        key_pair = gw.generate_key_pair(
            self.TEST_KEY_ALGORITHM, self.TEST_KEY_SIZE, self.TEST_PASSPHRASE
        )

        # Assert
        self.assertIsInstance(key_pair, KeyPairDetails)
        self.assertIsInstance(key_pair.public_key_pem, bytes)
        self.assertIsInstance(key_pair.private_key_pem, bytes)

    def test_get_private_key_pem(self):
        # Arrange
        gw = CryptographyGateway()
        test_key = gw._generate_private_key(self.TEST_KEY_ALGORITHM, self.TEST_KEY_SIZE)

        # Act
        private_key_pem = gw.get_private_key_pem(test_key, self.TEST_PASSPHRASE)
        unpacked_private_key = gw.load_private_key(
            private_key_pem, self.TEST_PASSPHRASE
        )
        test_key_pem = gw.get_private_key_pem(
            unpacked_private_key, self.TEST_PASSPHRASE
        )

        # Assert
        self.assertIsInstance(private_key_pem, bytes)
        self.assertIsInstance(test_key_pem, bytes)

    def test_get_public_key_pem(self):
        # Arrange
        gw = CryptographyGateway()

        # Act
        test_key_pair = gw.generate_key_pair(
            self.TEST_KEY_ALGORITHM, self.TEST_KEY_SIZE, self.TEST_PASSPHRASE
        )

        test_public_pem = test_key_pair.public_key_pem
        unpack_public_pem = gw.get_public_key_pem(gw.load_public_key(test_public_pem))

        # Assert
        self.assertIsInstance(test_public_pem, bytes)
        self.assertEqual(test_public_pem, unpack_public_pem)

    def test_generate_private_key(self):
        # Arrange
        gw = CryptographyGateway()
        test_rsa_algorithm = KeyAlgorithm.RSA
        test_unsupported_algorithm = "TEST"

        # Act
        test_rsa_key = gw._generate_private_key(test_rsa_algorithm, self.TEST_KEY_SIZE)

        # Assert
        self.assertIsInstance(test_rsa_key, RSAPrivateKeyWithSerialization)
        with self.assertRaises(NotImplementedError):
            gw._generate_private_key(test_unsupported_algorithm, self.TEST_KEY_SIZE)
