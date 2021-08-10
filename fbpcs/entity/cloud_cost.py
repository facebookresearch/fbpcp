#!/usr/bin/env python3
# Copyright (c) Facebook, Inc. and its affiliates.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

# pyre-strict
from dataclasses import dataclass
from typing import List

from fbpcs.cloud.region import RegionName
from fbpcs.cloud.service import ServiceName


@dataclass
class CloudCostItem:
    region: RegionName
    service: ServiceName
    cost_amount: int


@dataclass
class CloudCost:
    total_cost_amount: int
    details: List[CloudCostItem]
