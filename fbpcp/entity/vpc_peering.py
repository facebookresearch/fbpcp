#!/usr/bin/env python3
# Copyright (c) Meta Platforms, Inc. and affiliates.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

# pyre-strict
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict


class VpcPeeringState(Enum):
    PENDING_ACCEPTANCE = "PENDING_ACCEPTANCE"
    ACTIVE = "ACTIVE"
    REJECTED = "REJECTED"
    NOT_READY = "NOT_READY"


class VpcPeeringRole(Enum):
    REQUESTER = "REQUESTER"
    ACCEPTER = "ACCEPTER"


@dataclass
class VpcPeering:
    id: str
    status: VpcPeeringState
    role: VpcPeeringRole
    requester_vpc_id: str
    accepter_vpc_id: str
    tags: Dict[str, str] = field(default_factory=dict)
