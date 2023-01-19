#!/usr/bin/env python3
# Copyright (c) Meta Platforms, Inc. and affiliates.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

# pyre-strict

from dataclasses import dataclass
from enum import Enum
from typing import Dict, Optional

from dataclasses_json import DataClassJsonMixin


class PolicyName(str, Enum):
    BINARY_MATCH = "BINARY_MATCH"


@dataclass
class PolicyParams(DataClassJsonMixin):
    package_name: Optional[str]
    version: Optional[str]


@dataclass
class AttestationPolicy(DataClassJsonMixin):
    policy_name: PolicyName
    params: PolicyParams


@dataclass
class AttestationDocument(DataClassJsonMixin):
    policy: AttestationPolicy
    measurements: Dict[str, str]
