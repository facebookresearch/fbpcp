#!/usr/bin/env python3
# Copyright (c) Meta Platforms, Inc. and affiliates.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

# pyre-strict
from dataclasses import dataclass
from typing import List, Optional

from fbpcp.entity.firewall_ruleset import FirewallRuleset
from fbpcp.entity.route_table import RouteTable
from fbpcp.entity.subnet import Subnet
from fbpcp.entity.vpc_instance import Vpc
from fbpcp.entity.vpc_peering import VpcPeering


@dataclass
class PCENetwork:
    region: str
    vpc: Optional[Vpc]
    subnets: List[Subnet]
    route_table: Optional[RouteTable]
    vpc_peering: Optional[VpcPeering]
    firewall_rulesets: List[FirewallRuleset]
