#!/usr/bin/env python3
# Copyright (c) Meta Platforms, Inc. and affiliates.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

# pyre-strict
from dataclasses import dataclass, field
from typing import Dict


@dataclass
class Subnet:
    id: str
    availability_zone: str
    tags: Dict[str, str] = field(default_factory=dict)
