# Copyright (c) Meta Platforms, Inc. and affiliates.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

# pyre-strict
from dataclasses import dataclass
from enum import Enum
from typing import List


class Effect(str, Enum):
    ALLOW = "Allow"
    DENY = "Deny"


@dataclass
class PolicySettingsConfig:
    """This is a config struct used by Repository Monitor to set constraints for bucket policy.
    Args:
        exist: Wether the specified permission exists in the bucket's policy.
        effect: The specified effect.
        principal: The specified principal. Use normal string or "re(<principal regex>)" for regex matching.
        actions: List of specified actions.
    """

    exist: bool
    effect: Effect
    principal: str
    actions: List[str]
