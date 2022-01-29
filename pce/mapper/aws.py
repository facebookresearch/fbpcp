#!/usr/bin/env python3
# Copyright (c) Meta Platforms, Inc. and affiliates.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

# pyre-strict

from typing import Dict, Optional, Any

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


def map_ecstaskdefinition_to_awslogsgroupname(
    task_definition: Dict[str, Any],
) -> Optional[str]:
    try:
        container_definition = task_definition["containerDefinitions"][0]
        logConfiguration = container_definition["logConfiguration"]
        log_group_name = logConfiguration["options"]["awslogs-group"]
        return log_group_name
    except KeyError:
        return None
