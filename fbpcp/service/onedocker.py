#!/usr/bin/env python3
# Copyright (c) Facebook, Inc. and its affiliates.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

# pyre-strict

import asyncio
import logging
from typing import Dict, List, Optional, Final

from fbpcp.decorator.metrics import request_counter, duration_time, error_counter
from fbpcp.entity.container_instance import ContainerInstance, ContainerInstanceStatus
from fbpcp.error.pcp import PcpError
from fbpcp.metrics.emitter import MetricsEmitter
from fbpcp.metrics.getter import MetricsGetter
from fbpcp.service.container import ContainerService
from fbpcp.util.arg_builder import build_cmd_args
from fbpcp.util.typing import checked_cast


ONEDOCKER_CMD_PREFIX = (
    # patternlint-disable-next-line f-string-may-be-missing-leading-f
    "python3.8 -m onedocker.script.runner {package_name} {runner_args}"
)

DEFAULT_BINARY_VERSION = "latest"

METRICS_CONTAINER_COUNT = "onedocker.container.count"
METRICS_START_CONTAINERS_COUNT = "onedocker.start_containers.count"
METRICS_START_CONTAINERS_ERROR_COUNT = "onedocker.start_containers.error.count"
METRICS_START_CONTAINERS_DURATION = "onedocker.start_containers.duration"


class OneDockerService(MetricsGetter):
    """OneDockerService is responsible for executing a package(binary) in a container on Cloud"""

    def __init__(
        self,
        container_svc: ContainerService,
        task_definition: Optional[str] = None,
        metrics: Optional[MetricsEmitter] = None,
    ) -> None:
        """Constructor of OneDockerService
        container_svc -- service to spawn container instances
        task_definition -- container definition to spawn container instances
        metrics -- metrics emitter to emit metrics
        """
        if container_svc is None:
            raise ValueError(f"Dependency is missing. container_svc={container_svc}, ")

        self.container_svc = container_svc
        self.task_definition = task_definition
        self.metrics: Final[Optional[MetricsEmitter]] = metrics
        self.logger: logging.Logger = logging.getLogger(__name__)

    def has_metrics(self) -> bool:
        return self.metrics is not None

    def get_metrics(self) -> MetricsEmitter:
        if not self.metrics:
            raise PcpError("OneDocker doesn't have metrics emitter")

        return self.metrics

    def start_container(
        self,
        package_name: str,
        task_definition: Optional[str] = None,
        version: str = DEFAULT_BINARY_VERSION,
        cmd_args: str = "",
        env_vars: Optional[Dict[str, str]] = None,
        timeout: Optional[int] = None,
        tag: Optional[str] = None,
    ) -> ContainerInstance:
        return self.start_containers(
            package_name,
            task_definition,
            version,
            [cmd_args] if cmd_args else None,
            env_vars,
            timeout,
            tag,
        )[0]

    @error_counter(METRICS_START_CONTAINERS_ERROR_COUNT)
    @request_counter(METRICS_START_CONTAINERS_COUNT)
    @duration_time(METRICS_START_CONTAINERS_DURATION)
    def start_containers(
        self,
        package_name: str,
        task_definition: Optional[str] = None,
        version: str = DEFAULT_BINARY_VERSION,
        cmd_args_list: Optional[List[str]] = None,
        env_vars: Optional[Dict[str, str]] = None,
        timeout: Optional[int] = None,
        tag: Optional[str] = None,
    ) -> List[ContainerInstance]:
        """Spin up one container per element in input command list.
        task_definition -- if specified, overrides OneDockerService's task definition
                           when starting this container
        """
        if not cmd_args_list:
            raise ValueError("Command Argument List shouldn't be None or Empty")

        cmds = [
            self._get_cmd(package_name, version, cmd_args, timeout)
            for cmd_args in cmd_args_list
        ]

        self.logger.info(f"Spinning up {len(cmds)} container instance[s]")

        task_definition = task_definition or self.task_definition
        if not task_definition:
            raise ValueError(
                "task definition should be specified when spinning up containers"
            )
        containers = self.container_svc.create_instances(
            task_definition,
            cmds,
            env_vars,
        )

        if self.metrics:
            name = f"{METRICS_CONTAINER_COUNT}.{self.container_svc.get_region()}.{self.container_svc.get_cluster()}"
            name = f"{METRICS_CONTAINER_COUNT}.{tag}" if tag else name
            self.metrics.count(name, len(containers))
        return containers

    async def wait_for_pending_containers(
        self, container_ids: List[str]
    ) -> List[ContainerInstance]:
        tasks = [
            asyncio.create_task(self.wait_for_pending_container(container_id))
            for container_id in container_ids
        ]
        res = await asyncio.gather(*tasks)
        return [checked_cast(ContainerInstance, container) for container in res]

    async def wait_for_pending_container(
        self, container_id: str
    ) -> Optional[ContainerInstance]:
        updated_container = self.get_containers([container_id])[0]
        while (
            updated_container is None
            or updated_container.status is ContainerInstanceStatus.UNKNOWN
        ):
            await asyncio.sleep(1)
            updated_container = self.get_containers([container_id])[0]
            if updated_container is None:
                break
        return updated_container

    def stop_containers(self, containers: List[str]) -> List[Optional[PcpError]]:
        return self.container_svc.cancel_instances(containers)

    def get_containers(
        self, instance_ids: List[str]
    ) -> List[Optional[ContainerInstance]]:
        return self.container_svc.get_instances(instance_ids)

    def _get_exe_name(self, package_name: str) -> str:
        return package_name.split("/")[1]

    def _get_cmd(
        self,
        package_name: str,
        version: str = DEFAULT_BINARY_VERSION,
        cmd_args: Optional[str] = None,
        timeout: Optional[int] = None,
    ) -> str:
        runner_args = build_cmd_args(
            exe_args=cmd_args,
            version=version,
            timeout=timeout,
        )
        return ONEDOCKER_CMD_PREFIX.format(
            package_name=package_name,
            runner_args=runner_args,
        ).strip()
