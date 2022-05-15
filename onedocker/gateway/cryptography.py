#!/usr/bin/env python3
# Copyright (c) Meta Platforms, Inc. and affiliates.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

# pyre-strict
from datetime import datetime, timedelta
from typing import Optional, Union

from cryptography import x509
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives.serialization import (
    load_pem_private_key,
    load_pem_public_key,
)
from fbpcp.entity.certificate_request import KeyAlgorithm
from onedocker.entity.key_pair_details import KeyPairDetails


class CryptographyGateway:
    SIGN_ALGORITHM = hashes.SHA256()

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
    ) -> Union[rsa.RSAPrivateKeyWithSerialization]:
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

    def _generate_certificate(
        self,
        subject_name: x509.Name,
        issuer_name: x509.Name,
        private_key: Union[rsa.RSAPrivateKey],
        public_key: Union[rsa.RSAPublicKey],
        not_valid_before: datetime,
        not_valid_after: datetime,
        subject_alternative_name: Optional[x509.SubjectAlternativeName] = None,
    ) -> x509.Certificate:
        builder = x509.CertificateBuilder(
            subject_name=subject_name,
            issuer_name=issuer_name,
            public_key=public_key,
            serial_number=x509.random_serial_number(),
            not_valid_before=not_valid_before,
            not_valid_after=not_valid_after,
        )
        if subject_alternative_name:
            builder.add_extension(
                subject_alternative_name,
                critical=False,
            )

        certificate = builder.sign(private_key, self.SIGN_ALGORITHM)
        return certificate

    def generate_certificate_pem(
        self,
        subject_name: x509.Name,
        issuer_name: x509.Name,
        key_pair_details: KeyPairDetails,
        passphrase: str,
        days_valid: int,
        subject_alternative_name: Optional[x509.SubjectAlternativeName] = None,
    ) -> bytes:
        not_valid_before = datetime.utcnow()
        not_valid_after = not_valid_before + timedelta(days=days_valid)

        public_key = self.load_public_key(key_pair_details.public_key_pem)
        private_key = self.load_private_key(
            key_pair_details.private_key_pem, passphrase
        )
        certificate = self._generate_certificate(
            subject_name=subject_name,
            issuer_name=issuer_name,
            private_key=private_key,
            public_key=public_key,
            not_valid_before=not_valid_before,
            not_valid_after=not_valid_after,
            subject_alternative_name=subject_alternative_name,
        )
        return self.get_certificate_pem(certificate)

    def get_certificate_pem(self, certificate: x509.Certificate) -> bytes:
        return certificate.public_bytes(serialization.Encoding.PEM)
