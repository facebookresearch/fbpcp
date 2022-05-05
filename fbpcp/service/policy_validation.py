#!/usr/bin/env python3
# Copyright (c) Meta Platforms, Inc. and affiliates.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

# pyre-strict
import abc
from typing import List

from fbpcp.entity.policy_settings_config import PolicySettingsConfig
from fbpcp.entity.policy_statement import PolicyStatement


class PolicyValidationService:
    @abc.abstractmethod
    def is_bucket_policy_statements_valid(
        self,
        bucket: str,
        bucket_statements: List[PolicyStatement],
        policy_settings: List[PolicySettingsConfig],
    ) -> bool:
        """Returns whether the bucket's policy is valid according to policy_settings"""
        pass
