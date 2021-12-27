#!/usr/bin/env python3
# Copyright (c) Meta Platforms, Inc. and affiliates.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

# pyre-strict

from dataclasses import dataclass, field
from typing import Dict, List


@dataclass
class ContainerDefinition:
    id: str
    image: str
    cpu: int
    memory: int
    entry_point: List[str]
    environment: Dict[str, str]
    task_role_id: str
    tags: Dict[str, str] = field(default_factory=lambda: {})
