#!/usr/bin/env python3
# Copyright (c) Meta Platforms, Inc. and affiliates.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

import unittest

from fbpcp.entity.policy_settings_config import Effect, PolicySettingsConfig
from fbpcp.entity.policy_statement import PolicyStatement
from fbpcp.service.policy_validation_aws import AWSPolicyValidationService

TEST_ACTION_1 = "s3:GetObject"
TEST_ACTION_2 = "s3:ListBucket"
TEST_BUCKET = "onedocker-repo-test"
TEST_RESOURCE_1 = f"arn:aws:s3:::{TEST_BUCKET}/*"
TEST_RESOURCE_2 = f"arn:aws:s3:::{TEST_BUCKET}"
TEST_STATEMENT = [
    PolicyStatement(
        effect="Allow",
        principals=["*"],
        actions=[TEST_ACTION_1],
        resources=[TEST_RESOURCE_1],
    ),
    PolicyStatement(
        effect="Allow",
        principals=["arn:aws:iam::account-id:root"],
        actions=[TEST_ACTION_2],
        resources=[TEST_RESOURCE_2],
    ),
]


class TestAWSPolicyValidationService(unittest.TestCase):
    def setUp(self):
        self.checker = AWSPolicyValidationService()

    def test_is_bucket_policy_statements_valid(self):
        # Arrange
        policy_settings = [
            # Test normal principal
            PolicySettingsConfig(
                exist=True,
                effect=Effect.ALLOW.value,
                principal="*",
                actions=[TEST_ACTION_1],
                resources=[TEST_RESOURCE_1],
            ),
            # Test regex principal
            PolicySettingsConfig(
                exist=True,
                effect=Effect.ALLOW.value,
                principal="re(arn:aws:iam::account-id:.*)",
                actions=[TEST_ACTION_2],
                resources=[TEST_RESOURCE_2],
            ),
            # Test not exist policy
            PolicySettingsConfig(
                exist=False,
                effect=Effect.ALLOW.value,
                principal="re(.*)",
                actions=["not-exist-action"],
                resources=["non-existing-resource"],
            ),
        ]
        # Act
        result = self.checker.is_bucket_policy_statements_valid(
            TEST_BUCKET, TEST_STATEMENT, policy_settings
        )
        # Assert
        self.assertTrue(result)

    def test_is_bucket_policy_statements_invalid(self):
        # Arrange
        policy_settings = [
            PolicySettingsConfig(
                exist=True,
                effect=Effect.DENY.value,
                principal="*",
                actions=[TEST_ACTION_1],
                resources=[TEST_RESOURCE_1],
            ),
            PolicySettingsConfig(
                exist=True,
                effect=Effect.ALLOW.value,
                principal="re(arn:aws:iam::account-id:.*)",
                actions=[TEST_ACTION_2],
                resources=[TEST_RESOURCE_1],
            ),
        ]
        # Act
        result = self.checker.is_bucket_policy_statements_valid(
            TEST_BUCKET, TEST_STATEMENT, policy_settings
        )
        # Assert
        self.assertFalse(result)
