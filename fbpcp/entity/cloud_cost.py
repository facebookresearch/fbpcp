#!/usr/bin/env python3
# Copyright (c) Facebook, Inc. and its affiliates.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

# pyre-strict
from dataclasses import dataclass
from decimal import Decimal
from typing import List

from fbpcp.cloud.region import RegionName
from fbpcp.cloud.service import ServiceName


@dataclass
class CloudCostItem:
    region: RegionName
    service: ServiceName
    cost_amount: Decimal


@dataclass
class CloudCost:
    total_cost_amount: Decimal
    details: List[CloudCostItem]
