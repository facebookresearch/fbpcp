#!/usr/bin/env python3
# Copyright (c) Facebook, Inc. and its affiliates.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

# pyre-strict

import abc
from typing import Dict, List, Optional

from fbpcp.entity.container_instance import ContainerInstance
from fbpcp.error.pcp import PcpError


class ContainerService(abc.ABC):
    @abc.abstractmethod
    def get_region(
        self,
    ) -> str:
        pass

    @abc.abstractmethod
    def get_cluster(
        self,
    ) -> str:
        pass

    @abc.abstractmethod
    def create_instance(
        self,
        container_definition: str,
        cmd: str,
        env_vars: Optional[Dict[str, str]] = None,
    ) -> ContainerInstance:
        pass

    @abc.abstractmethod
    def create_instances(
        self,
        container_definition: str,
        cmds: List[str],
        env_vars: Optional[Dict[str, str]] = None,
    ) -> List[ContainerInstance]:
        pass

    @abc.abstractmethod
    async def create_instances_async(
        self,
        container_definition: str,
        cmds: List[str],
        env_vars: Optional[Dict[str, str]] = None,
    ) -> List[ContainerInstance]:
        pass

    @abc.abstractmethod
    def get_instance(self, instance_id: str) -> ContainerInstance:
        pass

    @abc.abstractmethod
    def get_instances(self, instance_ids: List[str]) -> List[ContainerInstance]:
        pass

    @abc.abstractmethod
    def cancel_instances(self, instance_ids: List[str]) -> List[Optional[PcpError]]:
        pass

    @abc.abstractmethod
    def cancel_instance(self, instance_id: str) -> None:
        pass
