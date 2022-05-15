# Copyright (c) Meta Platforms, Inc. and affiliates.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

# pyre-strict

from dataclasses import dataclass
from typing import Any, Dict


RoleId = str
RoleName = str
PolicyName = str
PolicyContents = Dict[str, Any]


@dataclass
class IAMRole:
    role_id: RoleId
    attached_policy_contents: Dict[PolicyName, PolicyContents]
