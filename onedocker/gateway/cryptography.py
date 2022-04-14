#!/usr/bin/env python3
# Copyright (c) Meta Platforms, Inc. and affiliates.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

# pyre-strict
from typing import Union

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from fbpcp.entity.certificate_request import KeyAlgorithm


class CryptographyGateway:
    def _convert_str_to_bytes(self, s: str) -> bytes:
        return s.encode("utf-8")

    def generate_private_key(
        self,
        key_algorithm: KeyAlgorithm,
        key_size: int,
    ) -> Union[rsa.RSAPrivateKeyWithSerialization]:
        if key_algorithm == KeyAlgorithm.RSA:
            # The public_exponent indicates what one mathematical property of the key generation will be. Official guide suggests always use 65537. (https://cryptography.io/en/latest/hazmat/primitives/asymmetric/rsa/)
            public_exponent = 65537
            key = rsa.generate_private_key(
                public_exponent=public_exponent,
                key_size=key_size,
            )
            return key
        else:
            # For now we only support RSA since it is one of the most common algorithms, will add more key algorithms in the future
            raise NotImplementedError

    def get_key_private_bytes(
        self,
        key: Union[rsa.RSAPrivateKeyWithSerialization],
        passphrase: str,
    ) -> bytes:
        key_bytes = key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.TraditionalOpenSSL,
            encryption_algorithm=serialization.BestAvailableEncryption(
                self._convert_str_to_bytes(passphrase)
            ),
        )
        return key_bytes
