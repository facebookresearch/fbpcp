#!/usr/bin/env python3
# Copyright (c) Meta Platforms, Inc. and affiliates.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

# pyre-strict

from onedocker.entity.attestation_document import (
    AttestationDocument,
    AttestationPolicy,
    PolicyName,
)
from onedocker.service.attestation import AttestationService
from onedocker.service.attestation_pc import PCAttestationService


class AttestationFactoryService:
    def validate(self, attestation_document: str) -> bool:
        try:
            document = AttestationDocument.from_json(attestation_document)
        except Exception as e:
            raise ValueError(
                f"Failed to parse attestation document json, reason: {e}"
            ) from e
        attestation_svc = self._get_attestation_service(document.policy)
        return attestation_svc.validate(document.policy, document.measurements)

    def _get_attestation_service(self, policy: AttestationPolicy) -> AttestationService:
        if policy.policy_name == PolicyName.BINARY_MATCH:
            return PCAttestationService()
        else:
            raise NotImplementedError(
                f"Policy name {policy.policy_name} is NOT supported for now."
            )
