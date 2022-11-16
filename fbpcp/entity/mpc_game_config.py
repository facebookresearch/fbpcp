#!/usr/bin/env python3
# Copyright (c) Meta Platforms, Inc. and affiliates.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

# pyre-strict

from dataclasses import dataclass
from typing import List
from warnings import warn


warn(
    f"{__file__} has been moved to fbpcs repo. Please consider https://github.com/facebookresearch/fbpcs/tree/main/fbpcs/private_computation/service/mpc instead.",
    DeprecationWarning,
    stacklevel=2,
)


@dataclass
class MPCGameArgument:
    name: str
    required: bool


@dataclass
class MPCGameConfig:
    game_name: str
    onedocker_package_name: str
    arguments: List[MPCGameArgument]
