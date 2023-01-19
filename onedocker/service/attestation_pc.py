#!/usr/bin/env python3
# Copyright (c) Meta Platforms, Inc. and affiliates.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

# pyre-strict


import logging
from typing import Dict

from fbpcp.error.pcp import InvalidParameterError

from onedocker.entity.attestation_document import AttestationPolicy, PolicyName
from onedocker.gateway.repository_service import RepositoryServiceGateway
from onedocker.service.attestation import AttestationService


class PCAttestationService(AttestationService):
    def __init__(self) -> None:
        self.repository_service_gateway = RepositoryServiceGateway()
        self.logger: logging.Logger = logging.getLogger(__name__)

    def validate(self, policy: AttestationPolicy, measurements: Dict[str, str]) -> bool:
        if policy.policy_name != PolicyName.BINARY_MATCH:
            raise NotImplementedError("Only BINARY_MATCH policy is supported for now.")
        if policy.params.package_name is None or policy.params.version is None:
            raise InvalidParameterError(
                "Package name and version must be specified in policy to perform binary match."
            )
        return self.binary_match(
            policy.params.package_name, policy.params.version, measurements
        )

    def binary_match(
        self, package_name: str, version: str, measurements: Dict[str, str]
    ) -> bool:
        allowlist = self.repository_service_gateway.get_measurements(
            package_name, version
        )
        for measurement_key, measurement_value in measurements.items():
            if measurement_key not in allowlist:
                self.logger.error(
                    f"Cannot find measurement with key '{measurement_key}' in allowlist."
                )
                return False
            if allowlist[measurement_key] != measurement_value:
                self.logger.error(
                    f"Measurement with key '{measurement_key}' does not match the allowed value."
                )
                return False
        return True
