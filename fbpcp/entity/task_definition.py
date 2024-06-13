#!/usr/bin/env python3
# Copyright (c) Facebook, Inc. and its affiliates.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

# pyre-strict

from dataclasses import dataclass, field
from typing import Dict, List

from fbpcp.entity.iam import Role


@dataclass
class TaskDefinition:
    name: str
    image: str
    cpu: int
    memory: int
    entry_point: List[str]
    environment: List[str]
    task_role: Role
    execution_role: Role
    tags: Dict[str, str] = field(default_factory=lambda: {})
