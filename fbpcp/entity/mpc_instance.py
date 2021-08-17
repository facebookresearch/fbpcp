#!/usr/bin/env python3
# Copyright (c) Facebook, Inc. and its affiliates.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

# pyre-strict

from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Optional

from fbpcp.entity.container_instance import ContainerInstance
from fbpcp.entity.instance_base import InstanceBase


# TODO: T96692057 will delete MPCRole, keeping for now so that code doesn't break
# while fbpmp codebase expects it to exist
class MPCRole(Enum):
    SERVER = "SERVER"
    CLIENT = "CLIENT"


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
class MPCInstance(InstanceBase):
    instance_id: str
    game_name: str
    mpc_party: MPCParty
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
        num_workers: int,
        mpc_role: Optional[MPCRole] = None,
        mpc_party: Optional[MPCParty] = None,
        server_ips: Optional[List[str]] = None,
        containers: Optional[List[ContainerInstance]] = None,
        status: MPCInstanceStatus = MPCInstanceStatus.UNKNOWN,
        game_args: Optional[List[Dict[str, Any]]] = None,
    ) -> "MPCInstance":
        # TODO: T96692057 will delete mpc_role and make mpc_party required
        if mpc_party:
            party = mpc_party
        elif mpc_role:
            party = MPCParty.SERVER if mpc_role is MPCRole.SERVER else MPCParty.CLIENT
        else:
            raise ValueError("mpc_role or mpc_party should be specified")

        return cls(
            instance_id,
            game_name,
            party,
            num_workers,
            server_ips,
            containers or [],
            status,
            game_args,
        )

    def get_instance_id(self) -> str:
        return self.instance_id
