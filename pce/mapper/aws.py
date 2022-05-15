#!/usr/bin/env python3
# Copyright (c) Meta Platforms, Inc. and affiliates.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

# pyre-strict

from typing import Any, Dict, Optional

from pce.entity.iam_role import IAMRole, PolicyContents, PolicyName, RoleId


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
        log_configuration = container_definition["logConfiguration"]
        log_group_name = log_configuration["options"]["awslogs-group"]
        return log_group_name
    # Key error indicates the log group does not exist, error will be returned in error message templates
    except KeyError:
        return None
