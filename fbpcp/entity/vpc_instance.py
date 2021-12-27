#!/usr/bin/env python3
# Copyright (c) Meta Platforms, Inc. and affiliates.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

# pyre-strict

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict

from dataclasses_json import dataclass_json


class VpcState(Enum):
    UNKNOWN = "UNKNOWN"
    PENDING = "PENDING"
    AVAILABLE = "AVAILABLE"


@dataclass_json
@dataclass
class Vpc:
    vpc_id: str
    cidr: str
    state: VpcState = VpcState.UNKNOWN
    tags: Dict[str, str] = field(default_factory=dict)
