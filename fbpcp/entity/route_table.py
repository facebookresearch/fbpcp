#!/usr/bin/env python3
# Copyright (c) Meta Platforms, Inc. and affiliates.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

# pyre-strict
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List


class RouteTargetType(Enum):
    OTHER = "OTHER"
    INTERNET = "INTERNET"
    VPC_PEERING = "VPC_PEERING"


class RouteState(Enum):
    UNKNOWN = "UNKNOWN"
    ACTIVE = "ACTIVE"


@dataclass
class RouteTarget:
    route_target_id: str
    route_target_type: RouteTargetType


@dataclass
class Route:
    destination_cidr_block: str
    route_target: RouteTarget
    state: RouteState


@dataclass
class RouteTable:
    id: str
    routes: List[Route]
    vpc_id: str
    tags: Dict[str, str] = field(default_factory=dict)
