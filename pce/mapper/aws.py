#!/usr/bin/env python3
# Copyright (c) Facebook, Inc. and its affiliates.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

# pyre-strict

from typing import Dict, Optional

from pce.entity.iam_role import (
    IAMRole,
    RoleId,
    PolicyName,
    PolicyContents,
)


def map_attachedrolepolicies_to_rolepolicies(
    role_id: RoleId,
    attached_role_policies: Dict[PolicyName, PolicyContents],
) -> Optional[IAMRole]:
    return IAMRole(role_id, attached_role_policies) if attached_role_policies else None
