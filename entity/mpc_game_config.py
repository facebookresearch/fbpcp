#!/usr/bin/env python3
# pyre-strict

from dataclasses import dataclass
from typing import List


@dataclass
class MPCGameArgument:
    name: str
    required: bool


@dataclass
class MPCGameConfig:
    game_name: str
    one_docker_package_name: str
    arguments: List[MPCGameArgument]
