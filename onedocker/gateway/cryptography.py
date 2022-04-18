#!/usr/bin/env python3
# Copyright (c) Meta Platforms, Inc. and affiliates.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

# pyre-strict
from typing import Union

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives.asymmetric.rsa import RSAPrivateKeyWithSerialization
from cryptography.hazmat.primitives.serialization import (
    load_pem_private_key,
    load_pem_public_key,
)
from fbpcp.entity.certificate_request import KeyAlgorithm
from onedocker.entity.key_pair_details import KeyPairDetails


class CryptographyGateway:
    def _convert_str_to_bytes(self, s: str) -> bytes:
        return s.encode("utf-8")

    def generate_key_pair(
        self,
        key_algorithm: KeyAlgorithm,
        key_size: int,
        passphrase: str,
    ) -> KeyPairDetails:
        private_key = self._generate_private_key(key_algorithm, key_size)
        private_key_pem = self.get_private_key_pem(private_key, passphrase)
        public_key_pem = self.get_public_key_pem(private_key.public_key())
        return KeyPairDetails(
            private_key_pem=private_key_pem,
            public_key_pem=public_key_pem,
        )

    def _generate_private_key(
        self,
        key_algorithm: KeyAlgorithm,
        key_size: int,
    ) -> Union[RSAPrivateKeyWithSerialization]:
        if key_algorithm == KeyAlgorithm.RSA:
            # The public_exponent indicates what one mathematical property of the key generation will be. Official guide suggests always use 65537. (https://cryptography.io/en/latest/hazmat/primitives/asymmetric/rsa/)
            public_exponent = 65537
            private_key = rsa.generate_private_key(
                public_exponent=public_exponent,
                key_size=key_size,
            )
            return private_key
        else:
            # For now we only support RSA since it is one of the most common algorithms, will add more key algorithms in the future
            raise NotImplementedError

    def get_private_key_pem(
        self,
        private_key: Union[rsa.RSAPrivateKeyWithSerialization],
        passphrase: str,
    ) -> bytes:
        key_pem = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.TraditionalOpenSSL,
            encryption_algorithm=serialization.BestAvailableEncryption(
                self._convert_str_to_bytes(passphrase)
            ),
        )
        return key_pem

    def load_private_key(
        self,
        key_pem: bytes,
        passphrase: str,
    ) -> Union[rsa.RSAPrivateKey]:
        private_key = load_pem_private_key(
            key_pem, self._convert_str_to_bytes(passphrase), default_backend()
        )
        return private_key

    def get_public_key_pem(
        self,
        public_key: Union[rsa.RSAPublicKey],
    ) -> bytes:
        key_pem = public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo,
        )
        return key_pem

    def load_public_key(self, key_pem: bytes) -> Union[rsa.RSAPublicKey]:
        public_key = load_pem_public_key(key_pem, default_backend())
        return public_key
