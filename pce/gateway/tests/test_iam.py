#!/usr/bin/env python3
# Copyright (c) Facebook, Inc. and its affiliates.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

# pyre-strict

from unittest import TestCase
from unittest.mock import call, MagicMock

from pce.entity.iam_role import (
    IAMRole,
)
from pce.gateway.iam import IAMGateway


class TestIAMGateway(TestCase):
    def setUp(self) -> None:
        self.aws_iam = MagicMock()
        self.iam = IAMGateway(lambda _: self.aws_iam)

    def test_get_policies_for_role(self) -> None:
        test_role_name_1 = "test_role_1"
        test_role_name_2 = "test_role_2"
        test_policy_name_1 = "test_policy_1"
        test_policy_name_2 = "test_policy_2"

        def role_name_to_arn(role_name: str) -> str:
            return f"arn:aws:iam::123456789:role/{role_name}"

        def policy_name_to_arn(policy_name: str) -> str:
            return f"arn:aws:iam::aws:policy/service-role/{policy_name}"

        test_policy_arn_1 = policy_name_to_arn(test_policy_name_1)
        test_policy_arn_2 = policy_name_to_arn(test_policy_name_2)
        test_role_arn_1 = role_name_to_arn(test_role_name_1)
        test_role_arn_2 = role_name_to_arn(test_role_name_2)
        test_policy_contents_1 = {"a1": "b1"}
        test_policy_contents_2 = {"a2": "b2"}

        mock_paginator = MagicMock()
        mock_paginator.paginate = MagicMock(
            side_effect=lambda RoleName: {
                test_role_name_1: [
                    {
                        "AttachedPolicies": [
                            {
                                "PolicyName": test_policy_name_1,
                                "PolicyArn": test_policy_arn_1,
                            }
                        ]
                    }
                ],
                test_role_name_2: [
                    {
                        "AttachedPolicies": [
                            {
                                "PolicyName": test_policy_name_2,
                                "PolicyArn": test_policy_arn_2,
                            }
                        ]
                    }
                ],
            }[RoleName]
        )

        self.aws_iam.get_paginator = MagicMock(return_value=mock_paginator)

        self.aws_iam.get_policy = MagicMock(
            return_value={"Policy": {"DefaultVersionId": 1}}
        )

        self.aws_iam.get_policy_version = MagicMock(
            side_effect=lambda PolicyArn, VersionId: {
                test_policy_arn_1: {
                    "PolicyVersion": {"Document": test_policy_contents_1}
                },
                test_policy_arn_2: {
                    "PolicyVersion": {"Document": test_policy_contents_2}
                },
            }[PolicyArn]
        )

        test_expected_role_attached_policies = {
            test_role_arn_1: IAMRole(
                test_role_arn_1, {test_policy_name_1: test_policy_contents_1}
            ),
            test_role_arn_2: IAMRole(
                test_role_arn_2, {test_policy_name_2: test_policy_contents_2}
            ),
        }

        for (
            role_id,
            test_expected_role_attached_policy,
        ) in test_expected_role_attached_policies.items():
            policies = self.iam.get_policies_for_role(role_id)
            self.assertEqual(
                test_expected_role_attached_policy,
                policies,
            )

        mock_paginator.paginate.assert_has_calls(
            [
                call(RoleName=IAMGateway._role_id_to_name(test_role_name))
                for test_role_name in test_expected_role_attached_policies.keys()
            ]
        )

    def test_role_id_to_name_slashes(self) -> None:
        role_name = "application_abc/component_xyz/RDSAccess"
        self.assertEqual(
            IAMGateway._role_id_to_name(f"arn:aws:iam::123456789012:role/{role_name}"),
            role_name,
        )

    def test_role_id_to_name_no_slashes(self) -> None:
        role_name = "RDSAccess"
        self.assertEqual(
            IAMGateway._role_id_to_name(f"arn:aws:iam::123456789012:role/{role_name}"),
            role_name,
        )
