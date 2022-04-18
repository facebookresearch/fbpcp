#!/usr/bin/env python3
# Copyright (c) Meta Platforms, Inc. and affiliates.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

# pyre-strict
import logging
import os

from fbpcp.entity.certificate_request import CertificateRequest
from onedocker.gateway.cryptography import CryptographyGateway
from onedocker.service.certificate import CertificateService

DEFAULT_CERT_PATH = "certificate"
DEFAULT_PRIVATE_KEY_NAME = "private_key.pem"


def str_to_bytes(s: str) -> bytes:
    return s.encode("utf-8")


class SelfSignedCertificateService(CertificateService):
    def __init__(self, cert_request: CertificateRequest) -> None:
        self.logger: logging.Logger = logging.getLogger(__name__)
        self.cert_request = cert_request
        self.cert_path: str = self.cert_request.cert_path or DEFAULT_CERT_PATH
        self.private_key_path: str = os.path.join(
            self.cert_path,
            (self.cert_request.private_key_name or DEFAULT_PRIVATE_KEY_NAME),
        )
        self.crypt_gateway = CryptographyGateway()

    def _write_bytes_to_file(self, filename: str, content: bytes) -> None:
        try:
            with open(filename, "wb") as f:
                f.write(content)
        except Exception as err:
            self.logger.exception(
                f"An error was raised in CertificateService while writing to file {filename}, error: {err}"
            )

    def generate_certificate(
        self,
    ) -> str:
        # create dir for private key and certificate
        os.makedirs(self.cert_path, exist_ok=True)

        # generate key pair
        key_pair = self.crypt_gateway.generate_key_pair(
            self.cert_request.key_algorithm,
            self.cert_request.key_size,
            self.cert_request.passphrase,
        )

        # write private key to file
        self._write_bytes_to_file(self.private_key_path, key_pair.private_key_pem)

        # TODO implement the certificate signing part

        return self.cert_path
