#!/usr/bin/env python3
# Copyright (c) Facebook, Inc. and its affiliates.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

# pyre-strict

from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Optional

from fbpcs.entity.container_instance import ContainerInstance
from fbpcs.entity.instance_base import InstanceBase


class MPCRole(Enum):
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
class MPCInstance(InstanceBase):
    instance_id: str
    game_name: str
    mpc_role: MPCRole
    num_workers: int
    server_ips: Optional[List[str]]
    containers: List[ContainerInstance]
    status: MPCInstanceStatus
    game_args: Optional[List[Dict[str, Any]]]

    @classmethod
    def create_instance(
        cls,
        instance_id: str,
        game_name: str,
        mpc_role: MPCRole,
        num_workers: int,
        server_ips: Optional[List[str]] = None,
        containers: Optional[List[ContainerInstance]] = None,
        status: MPCInstanceStatus = MPCInstanceStatus.UNKNOWN,
        game_args: Optional[List[Dict[str, Any]]] = None,
    ) -> "MPCInstance":
        return cls(
            instance_id,
            game_name,
            mpc_role,
            num_workers,
            server_ips,
            containers or [],
            status,
            game_args,
        )

    def get_instance_id(self) -> str:
        return self.instance_id
