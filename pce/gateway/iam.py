# Copyright (c) Meta Platforms, Inc. and affiliates.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

# pyre-strict

from re import sub
from typing import Any, Dict, Optional

import boto3
from fbpcp.gateway.aws import AWSGateway
from pce.entity.iam_role import IAMRole, RoleId, RoleName
from pce.mapper.aws import map_attachedrolepolicies_to_rolepolicies


class IAMGateway(AWSGateway):
    def __init__(
        self,
        region: str,
        access_key_id: Optional[str] = None,
        access_key_data: Optional[str] = None,
        config: Optional[Dict[str, Any]] = None,
    ) -> None:
        super().__init__(region, access_key_id, access_key_data, config)

        # pyre-ignore
        self.client = boto3.client("iam", region_name=self.region, **self.config)

    @classmethod
    def _role_id_to_name(cls, role_id: RoleId) -> RoleName:
        return sub(r".*?:role/", "", role_id)

    def get_policies_for_role(
        self,
        role_id: RoleId,
    ) -> Optional[IAMRole]:
        return map_attachedrolepolicies_to_rolepolicies(
            role_id,
            {
                policy["PolicyName"]:
                # Retrieving the policy document requires retrieving the version id for each policy arn, hence `get_policy` has to be called for each `get_policy_version` invocation
                self.client.get_policy_version(
                    PolicyArn=policy["PolicyArn"],
                    VersionId=self.client.get_policy(PolicyArn=policy["PolicyArn"])[
                        "Policy"
                    ]["DefaultVersionId"],
                )["PolicyVersion"]["Document"]
                for policy_result in self.client.get_paginator(
                    "list_attached_role_policies"
                ).paginate(RoleName=self._role_id_to_name(role_id))
                for policy in policy_result["AttachedPolicies"]
            },
        )
