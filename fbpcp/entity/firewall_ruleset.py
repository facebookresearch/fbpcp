#!/usr/bin/env python3
# Copyright (c) Meta Platforms, Inc. and affiliates.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

# pyre-strict
from dataclasses import dataclass, field
from typing import Dict, List


@dataclass
class FirewallRule:
    from_port: int
    to_port: int
    ip_protocol: str
    cidr: str


@dataclass
class FirewallRuleset:
    id: str
    vpc_id: str
    ingress: List[FirewallRule]
    egress: List[FirewallRule]
    tags: Dict[str, str] = field(default_factory=dict)
