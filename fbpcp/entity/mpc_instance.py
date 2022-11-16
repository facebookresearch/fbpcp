#!/usr/bin/env python3
# Copyright (c) Meta Platforms, Inc. and affiliates.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

# pyre-strict

from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Optional
from warnings import warn

from fbpcp.entity.container_instance import ContainerInstance


warn(
    f"{__file__} has been moved to fbpcs repo. Please consider https://github.com/facebookresearch/fbpcs/tree/main/fbpcs/private_computation/service/mpc instead.",
    DeprecationWarning,
    stacklevel=2,
)


class MPCParty(Enum):
    SERVER = "SERVER"
    CLIENT = "CLIENT"


class MPCInstanceStatus(Enum):
    UNKNOWN = "UNKNOWN"
    CREATED = "CREATED"
    STARTED = "STARTED"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    CANCELED = "CANCELED"


@dataclass
class MPCInstance:
    instance_id: str
    game_name: str
    mpc_party: MPCParty
    num_workers: int
    server_ips: Optional[List[str]]
    containers: List[ContainerInstance]
    status: MPCInstanceStatus
    game_args: Optional[List[Dict[str, Any]]]
    server_uris: Optional[List[str]] = None

    def get_instance_id(self) -> str:
        return self.instance_id
