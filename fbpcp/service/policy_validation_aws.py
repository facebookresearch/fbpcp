#!/usr/bin/env python3
# Copyright (c) Meta Platforms, Inc. and affiliates.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

# pyre-strict
import logging
import re
from typing import List

from fbpcp.entity.policy_settings_config import PolicySettingsConfig
from fbpcp.entity.policy_statement import PolicyStatement
from fbpcp.service.policy_validation import PolicyValidationService


class AWSPolicyValidationService(PolicyValidationService):
    def __init__(self) -> None:
        self.logger: logging.Logger = logging.getLogger(__name__)

    def _principal_match(self, principal_settings: str, principal: str) -> bool:
        """Returns whether the principal matches the principal_settings.
        Args:
            principal_settings: Principal settings in the PolicySettingsConfig.
                This can either be a normal string,
                or in format "re(<principal regex>)" to indicate regex matching.
            principal: The principal string.
        """
        match = re.fullmatch(r"re\((.*?)\)", principal_settings)
        if match:
            principal_regex = match.group(1)
            return bool(re.fullmatch(principal_regex, principal))
        return principal_settings == principal

    def _policy_exists_in_statements(
        self,
        statements: List[PolicyStatement],
        effect: str,
        principal: str,
        actions: List[str],
        resources: List[str],
    ) -> bool:
        for statement in statements:
            contain_principal = any(
                self._principal_match(principal, stmt_principal)
                for stmt_principal in statement.principals
            )
            if (
                contain_principal
                and effect == statement.effect
                and set(actions).issubset(statement.actions)
                and set(resources).issubset(statement.resources)
            ):
                return True
        return False

    def is_bucket_policy_statements_valid(
        self,
        bucket: str,
        bucket_statements: List[PolicyStatement],
        policy_settings: List[PolicySettingsConfig],
    ) -> bool:
        for rule in policy_settings:
            if rule.exist != self._policy_exists_in_statements(
                bucket_statements,
                rule.effect,
                rule.principal,
                rule.actions,
                [f"arn:aws:s3:::{bucket}/*"],
            ):
                self.logger.error(
                    "The policy of bucket %s does not satisfy the following policy settings: %s.",
                    bucket,
                    str(rule),
                )
                return False
        return True
