#!/usr/bin/env python3
# Copyright (c) Meta Platforms, Inc. and affiliates.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

# pyre-strict
import logging

from fbpcp.entity.certificate_request import CertificateRequest
from onedocker.service.certificate import CertificateService

DEFAULT_CERT_PATH = "certificate"


class SelfSignedCertificateService(CertificateService):
    def __init__(self, cert_request: CertificateRequest) -> None:
        self.logger: logging.Logger = logging.getLogger(__name__)
        self.cert_request = cert_request

    def generate_certificate(
        self,
    ) -> str:
        # TODO implement this function in later diff
        return ""
