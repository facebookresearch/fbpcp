#!/usr/bin/env python3
# Copyright (c) Facebook, Inc. and its affiliates.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

# pyre-strict
from dataclasses import dataclass

from fbpcp.entity.pce_compute import PCECompute
from fbpcp.entity.pce_network import PCENetwork


@dataclass
class PCE:
    pce_id: str
    region: str
    pce_network: PCENetwork
    pce_compute: PCECompute
