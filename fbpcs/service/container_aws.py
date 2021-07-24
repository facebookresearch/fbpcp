#!/usr/bin/env python3
# Copyright (c) Facebook, Inc. and its affiliates.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

# pyre-strict

import asyncio
import logging
from typing import Any, Dict, List, Optional, Tuple

from fbpcs.entity.container_instance import ContainerInstance, ContainerInstanceStatus
from fbpcs.error.pcs import PcsError
from fbpcs.gateway.ecs import ECSGateway
from fbpcs.service.container import ContainerService
from fbpcs.util.typing import checked_cast


class AWSContainerService(ContainerService):
    def __init__(
        self,
        region: str,
        cluster: str,
        subnets: Optional[List[str]] = None,
        access_key_id: Optional[str] = None,
        access_key_data: Optional[str] = None,
        config: Optional[Dict[str, Any]] = None,
    ) -> None:
        self.logger: logging.Logger = logging.getLogger(__name__)
        self.region = region
        self.cluster = cluster
        self.subnets = subnets
        self.ecs_gateway = ECSGateway(region, access_key_id, access_key_data, config)

    def create_instance(
        self,
        container_definition: str,
        cmd: str,
        env_vars: Optional[Dict[str, str]] = None,
    ) -> ContainerInstance:
        return asyncio.run(
            self._create_instance_async(container_definition, cmd, env_vars)
        )

    def create_instances(
        self,
        container_definition: str,
        cmds: List[str],
        env_vars: Optional[Dict[str, str]] = None,
    ) -> List[ContainerInstance]:
        return asyncio.run(
            self._create_instances_async(container_definition, cmds, env_vars)
        )

    async def create_instances_async(
        self,
        container_definition: str,
        cmds: List[str],
        env_vars: Optional[Dict[str, str]] = None,
    ) -> List[ContainerInstance]:
        return await self._create_instances_async(container_definition, cmds, env_vars)

    def get_instance(self, instance_id: str) -> ContainerInstance:
        return self.ecs_gateway.describe_task(self.cluster, instance_id)

    def get_instances(self, instance_ids: List[str]) -> List[ContainerInstance]:
        return self.ecs_gateway.describe_tasks(self.cluster, instance_ids)

    def list_tasks(self) -> List[str]:
        return self.ecs_gateway.list_tasks(cluster=self.cluster)

    def cancel_instance(self, instance_id: str) -> None:
        return self.ecs_gateway.stop_task(cluster=self.cluster, task_id=instance_id)

    def cancel_instances(self, instance_ids: List[str]) -> List[Optional[PcsError]]:
        res = []
        for instance_id in instance_ids:
            try:
                res.append(self.cancel_instance(instance_id))
            except PcsError as err:
                res.append(err)

        return res

    def _split_container_definition(self, container_definition: str) -> Tuple[str, str]:
        """
        container_definition = task_definition#container
        """
        s = container_definition.split("#")
        return (s[0], s[1])

    async def _create_instance_async(
        self,
        container_definition: str,
        cmd: str,
        env_vars: Optional[Dict[str, str]] = None,
    ) -> ContainerInstance:
        task_definition, container = self._split_container_definition(
            container_definition
        )

        if not self.subnets:
            raise PcsError(
                "No subnets specified. It's required to create container instances."
            )

        instance = self.ecs_gateway.run_task(
            task_definition, container, cmd, self.cluster, self.subnets, env_vars
        )

        # wait until the container is in running state
        while instance.status is ContainerInstanceStatus.UNKNOWN:
            await asyncio.sleep(1)
            instance = self.get_instance(instance.instance_id)

        return instance

    async def _create_instances_async(
        self,
        container_definition: str,
        cmds: List[str],
        env_vars: Optional[Dict[str, str]] = None,
    ) -> List[ContainerInstance]:
        tasks = [
            asyncio.create_task(
                self._create_instance_async(container_definition, cmd, env_vars)
            )
            for cmd in cmds
        ]
        res = await asyncio.gather(*tasks)
        self.logger.info(
            f"AWSContainerService created {len(res)} containers successfully"
        )
        return [checked_cast(ContainerInstance, instance) for instance in res]
