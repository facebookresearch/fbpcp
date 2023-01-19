#!/usr/bin/env python3
# Copyright (c) Meta Platforms, Inc. and affiliates.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

# pyre-strict

import abc
from typing import Dict

from onedocker.entity.attestation_document import AttestationPolicy


class AttestationService(abc.ABC):
    @abc.abstractmethod
    def validate(self, policy: AttestationPolicy, measurements: Dict[str, str]) -> bool:
        pass
