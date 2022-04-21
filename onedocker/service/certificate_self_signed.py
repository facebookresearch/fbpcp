#!/usr/bin/env python3
# Copyright (c) Meta Platforms, Inc. and affiliates.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

# pyre-strict
import logging
import os

from cryptography import x509
from cryptography.x509.oid import NameOID
from fbpcp.entity.certificate_request import CertificateRequest
from onedocker.gateway.cryptography import CryptographyGateway
from onedocker.mapper.cryptography import (
    map_certificaterequest_to_x509name,
    map_certificaterequest_to_x509subjectalternativename,
)
from onedocker.service.certificate import CertificateService

DEFAULT_CERT_FOLDER = "certificate"
DEFAULT_PRIVATE_KEY_NAME = "private_key.pem"
DEFAULT_CERTIFICATE_NAME = "certificate.pem"
DEFAULT_DAYS_VALID = 5

ISSUER_COUNTRY_NAME = "US"
ISSUER_ORGANIZATION_NAME = "OneDocker"


def convert_str_to_bytes(s: str) -> bytes:
    return s.encode("utf-8")


class SelfSignedCertificateService(CertificateService):
    def __init__(self, cert_request: CertificateRequest, exe_path: str) -> None:
        self.logger: logging.Logger = logging.getLogger(__name__)
        self._cert_request = cert_request
        self._cert_path: str = os.path.join(
            exe_path, self._cert_request.cert_folder or DEFAULT_CERT_FOLDER
        )
        self._private_key_file: str = self._get_file_path(
            self._cert_request.private_key_name or DEFAULT_PRIVATE_KEY_NAME,
        )
        self._certificate_file: str = self._get_file_path(
            self._cert_request.certificate_name or DEFAULT_CERTIFICATE_NAME
        )
        self._crypt_gateway: CryptographyGateway = CryptographyGateway()

    def _get_file_path(self, filename: str) -> str:
        return os.path.join(self._cert_path, filename)

    def _write_bytes_to_file(self, filename: str, content: bytes) -> None:
        try:
            with open(filename, "wb") as f:
                f.write(content)
            os.chmod(filename, 0o755)
        except Exception as err:
            self.logger.exception(
                f"An error was raised in CertificateService while writing to file {filename}, error: {err}"
            )

    def _get_self_sign_issuer_name(self) -> x509.Name:
        return x509.Name(
            [
                x509.NameAttribute(NameOID.COUNTRY_NAME, ISSUER_COUNTRY_NAME),
                x509.NameAttribute(NameOID.ORGANIZATION_NAME, ISSUER_ORGANIZATION_NAME),
            ]
        )

    def generate_certificate(
        self,
    ) -> str:
        # create dir for private key and certificate
        os.makedirs(self._cert_path, mode=0o777, exist_ok=True)

        # generate key pair
        key_pair = self._crypt_gateway.generate_key_pair(
            self._cert_request.key_algorithm,
            self._cert_request.key_size,
            self._cert_request.passphrase,
        )

        # write private key to file

        self._write_bytes_to_file(self._private_key_file, key_pair.private_key_pem)

        # generate certificate
        subject_name = map_certificaterequest_to_x509name(self._cert_request)
        subject_alternative_name = map_certificaterequest_to_x509subjectalternativename(
            self._cert_request
        )
        certificate_pem = self._crypt_gateway.generate_certificate_pem(
            subject_name=subject_name,
            issuer_name=self._get_self_sign_issuer_name(),
            key_pair_details=key_pair,
            passphrase=self._cert_request.passphrase,
            days_valid=self._cert_request.days_valid or DEFAULT_DAYS_VALID,
            subject_alternative_name=subject_alternative_name,
        )

        # write certificate to file

        self._write_bytes_to_file(self._certificate_file, certificate_pem)
        self.logger.info(f"Write private key and certificate to {self._cert_path}")
        return self._cert_path
