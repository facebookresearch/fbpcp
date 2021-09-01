#!/usr/bin/env python3
# Copyright (c) Facebook, Inc. and its affiliates.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

# pyre-strict

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List

from dataclasses_json import dataclass_json
from fbpcp.entity.firewall_ruleset import FirewallRuleset


class VpcState(Enum):
    UNKNOWN = "UNKNOWN"
    PENDING = "PENDING"
    AVAILABLE = "AVAILABLE"


@dataclass_json
@dataclass
class Vpc:
    vpc_id: str
    state: VpcState = VpcState.UNKNOWN
    firewall_rulesets: List[FirewallRuleset] = field(default_factory=list)
    tags: Dict[str, str] = field(default_factory=dict)
