#!/usr/bin/env python3
# Copyright (c) Meta Platforms, Inc. and affiliates.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

# pyre-strict
import abc

from fbpcp.entity.certificate_request import CertificateRequest


class CertificateService(abc.ABC):
    @abc.abstractmethod
    def __init__(self, cert_request: CertificateRequest, exe_path: str) -> None:
        pass

    @abc.abstractmethod
    def generate_certificate(
        self,
    ) -> str:
        pass
