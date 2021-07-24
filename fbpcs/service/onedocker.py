#!/usr/bin/env python3
# Copyright (c) Facebook, Inc. and its affiliates.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

# pyre-strict

import asyncio
import logging
from typing import Dict, List, Optional

from fbpcs.entity.container_instance import ContainerInstance
from fbpcs.error.pcs import PcsError
from fbpcs.service.container import ContainerService
from fbpcs.util.arg_builder import build_cmd_args


ONEDOCKER_CMD_PREFIX = (
    # patternlint-disable-next-line f-string-may-be-missing-leading-f
    "python3.8 -m onedocker.script.runner {package_name} {runner_args}"
)

DEFAULT_BINARY_VERSION = "latest"


class OneDockerService:
    """OneDockerService is responsible for executing a package(binary) in a container on Cloud"""

    def __init__(self, container_svc: ContainerService) -> None:
        """Constructor of OneDockerService
        container_svc -- service to spawn container instances
        """
        if container_svc is None:
            raise ValueError(f"Dependency is missing. container_svc={container_svc}, ")

        self.container_svc = container_svc
        self.logger: logging.Logger = logging.getLogger(__name__)

    def start_container(
        self,
        container_definition: str,
        package_name: str,
        version: str = DEFAULT_BINARY_VERSION,
        cmd_args: str = "",
        env_vars: Optional[Dict[str, str]] = None,
        timeout: Optional[int] = None,
    ) -> ContainerInstance:
        # TODO: ContainerInstance mapper
        return asyncio.run(
            self.start_containers_async(
                container_definition,
                package_name,
                version,
                [cmd_args] if cmd_args else None,
                env_vars,
                timeout,
            )
        )[0]

    def start_containers(
        self,
        container_definition: str,
        package_name: str,
        version: str = DEFAULT_BINARY_VERSION,
        cmd_args_list: Optional[List[str]] = None,
        env_vars: Optional[Dict[str, str]] = None,
        timeout: Optional[int] = None,
    ) -> List[ContainerInstance]:
        return asyncio.run(
            self.start_containers_async(
                container_definition,
                package_name,
                version,
                cmd_args_list,
                env_vars,
                timeout,
            )
        )

    async def start_containers_async(
        self,
        container_definition: str,
        package_name: str,
        version: str = DEFAULT_BINARY_VERSION,
        cmd_args_list: Optional[List[str]] = None,
        env_vars: Optional[Dict[str, str]] = None,
        timeout: Optional[int] = None,
    ) -> List[ContainerInstance]:
        """Asynchronously spin up one container per element in input command list."""
        if not cmd_args_list:
            raise ValueError("Command Argument List shouldn't be None or Empty")
        cmds = [
            self._get_cmd(package_name, version, cmd_args, timeout)
            for cmd_args in cmd_args_list
        ]
        self.logger.info("Spinning up container instances")
        container_ids = await self.container_svc.create_instances_async(
            container_definition, cmds, env_vars
        )
        return container_ids

    def stop_containers(self, containers: List[str]) -> List[Optional[PcsError]]:
        return self.container_svc.cancel_instances(containers)

    def get_containers(self, instance_ids: List[str]) -> List[ContainerInstance]:
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
