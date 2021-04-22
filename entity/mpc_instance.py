#!/usr/bin/env python3
# Copyright (c) Facebook, Inc. and its affiliates.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

# pyre-strict

from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Mapping, Optional

from dataclasses_json import dataclass_json
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


@dataclass_json
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
    arguments: Mapping[str, Any]

    def __init__(
        self,
        instance_id: str,
        game_name: str,
        mpc_role: MPCRole,
        num_workers: int,
        ip_config_file: Optional[str] = None,
        server_ips: Optional[List[str]] = None,
        containers: Optional[List[ContainerInstance]] = None,
        status: MPCInstanceStatus = MPCInstanceStatus.UNKNOWN,
        game_args: Optional[List[Dict[str, Any]]] = None,
        **arguments  # pyre-ignore
    ) -> None:
        self.instance_id = instance_id
        self.game_name = game_name
        self.mpc_role = mpc_role
        self.num_workers = num_workers
        self.ip_config_file = ip_config_file
        self.server_ips = server_ips
        self.containers = containers or []
        self.status = status
        self.game_args = game_args
        self.arguments = arguments

    def get_instance_id(self) -> str:
        return self.instance_id

    def __str__(self) -> str:
        # pyre-ignore
        return self.to_json()
