#!/usr/bin/env python3
# pyre-strict

import abc
from typing import List

from fbpcs.entity.container_instance import ContainerInstance


class ContainerService(abc.ABC):
    @abc.abstractmethod
    def create_instance(self, container_definition: str, cmd: str) -> ContainerInstance:
        pass

    @abc.abstractmethod
    def create_instances(
        self, container_definition: str, cmds: List[str]
    ) -> List[ContainerInstance]:
        pass

    @abc.abstractmethod
    async def create_instances_async(
        self, container_definition: str, cmds: List[str]
    ) -> List[ContainerInstance]:
        pass

    @abc.abstractmethod
    def get_instance(self, instance_id: str) -> ContainerInstance:
        pass

    @abc.abstractmethod
    def get_instances(self, instance_ids: List[str]) -> List[ContainerInstance]:
        pass
