#!/usr/bin/env python3
# Copyright (c) Meta Platforms, Inc. and affiliates.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

# pyre-strict

import logging
import re
from typing import Any, Dict, List, Optional

from fbpcp.entity.container_instance import ContainerInstance
from fbpcp.error.pcp import InvalidParameterError, PcpError
from fbpcp.gateway.ecs import ECSGateway
from fbpcp.metrics.emitter import MetricsEmitter
from fbpcp.service.container import ContainerService
from fbpcp.util.aws import split_container_definition

AWS_API_INPUT_SIZE_LIMIT = 100  # AWS API Call Capacity Limit


class AWSContainerService(ContainerService):
    def __init__(
        self,
        region: str,
        cluster: str,
        subnets: Optional[List[str]] = None,
        access_key_id: Optional[str] = None,
        access_key_data: Optional[str] = None,
        config: Optional[Dict[str, Any]] = None,
        metrics: Optional[MetricsEmitter] = None,
        session_token: Optional[str] = None,
    ) -> None:
        self.logger: logging.Logger = logging.getLogger(__name__)
        self.region = region
        self.cluster = cluster
        self.subnets = subnets
        self.ecs_gateway = ECSGateway(
            region, access_key_id, access_key_data, config, metrics, session_token
        )

    def get_region(
        self,
    ) -> str:
        return self.region

    def get_cluster(
        self,
    ) -> str:
        return self.cluster

    def create_instance(
        self,
        container_definition: str,
        cmd: str,
        env_vars: Optional[Dict[str, str]] = None,
    ) -> ContainerInstance:
        task_definition, container = split_container_definition(container_definition)

        if not self.subnets:
            raise PcpError(
                "No subnets specified. It's required to create container instances."
            )

        return self.ecs_gateway.run_task(
            task_definition, container, cmd, self.cluster, self.subnets, env_vars
        )

    def create_instances(
        self,
        container_definition: str,
        cmds: List[str],
        env_vars: Optional[Dict[str, str]] = None,
    ) -> List[ContainerInstance]:
        instances = [
            self.create_instance(container_definition, cmd, env_vars) for cmd in cmds
        ]
        self.logger.info(
            f"AWSContainerService created {len(instances)} containers successfully"
        )
        return instances

    def get_instance(self, instance_id: str) -> Optional[ContainerInstance]:
        return self.ecs_gateway.describe_task(self.cluster, instance_id)

    def get_instances(
        self, instance_ids: List[str]
    ) -> List[Optional[ContainerInstance]]:
        """Get one or more container instances

        Args:
            instance_ids: a list of the container instances.

        Returns:
            A list of Optional, in the same order as the input ids. For example, if
            users pass 3 instance_ids and the second instance could not be found,
            then returned list should also have 3 elements, with the 2nd elements being None.
        """
        id_batches = [
            instance_ids[i : i + AWS_API_INPUT_SIZE_LIMIT]
            for i in range(0, len(instance_ids), AWS_API_INPUT_SIZE_LIMIT)
        ]
        container_batches = [
            self.ecs_gateway.describe_tasks(self.cluster, ids) for ids in id_batches
        ]
        return sum(container_batches, [])

    def cancel_instance(self, instance_id: str) -> None:
        return self.ecs_gateway.stop_task(cluster=self.cluster, task_id=instance_id)

    def cancel_instances(self, instance_ids: List[str]) -> List[Optional[PcpError]]:
        res = []
        for instance_id in instance_ids:
            try:
                res.append(self.cancel_instance(instance_id))
            except PcpError as err:
                res.append(err)

        return res

    def get_current_instances_count(self) -> int:
        cluster = self.ecs_gateway.describe_cluster(self.cluster)
        return cluster.running_tasks + cluster.pending_tasks

    def validate_container_definition(self, container_definition: str) -> None:
        if not re.fullmatch(r"[\w\-/:]+?:\d+#[\w\-/]+?", container_definition):
            raise InvalidParameterError(
                "Parameter container_definition must be in format <task definition name>:<revision>#<container name>"
            )
