#!/usr/bin/env python3
# Copyright (c) Meta Platforms, Inc. and affiliates.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

# pyre-strict
from dataclasses import dataclass
from enum import Enum
from typing import List, Optional

from dataclasses_json import dataclass_json
from fbpcp.entity.measurement import Measurement


class PolicyName(str, Enum):
    BINARY_MATCH = "BINARY_MATCH"


@dataclass_json
@dataclass
class PolicyParams:
    package_name: Optional[str]
    version: Optional[str]


@dataclass_json
@dataclass
class AttestationPolicy:
    policy_name: PolicyName
    params: PolicyParams


@dataclass_json
@dataclass
class AttestationDocument:
    policy: AttestationPolicy
    measurements: List[Measurement]
