#!/usr/bin/env python3
# Copyright (c) Facebook, Inc. and its affiliates.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

# pyre-strict
from dataclasses import dataclass, field
from typing import Dict, List


@dataclass
class PolicyDocument:
    json: str


@dataclass
class Policy:
    name: str
    resource_name: str
    policy_document: PolicyDocument
    permissions: List[str]


@dataclass
class Role:
    name: str
    resource_name: str
    assume_role_policy_document: PolicyDocument
    attached_policies: List[Policy]
    tags: Dict[str, str] = field(default_factory=lambda: {})
