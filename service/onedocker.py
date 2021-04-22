#!/usr/bin/env python3
# Copyright (c) Facebook, Inc. and its affiliates.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

# pyre-strict

import asyncio
import logging
from typing import List, Optional

from fbpcs.entity.container_instance import ContainerInstance
from fbpcs.service.container import ContainerService


# patternlint-disable-next-line f-string-may-be-missing-leading-f
ONE_DOCKER_CMD_PREFIX = "python3.8 -m one_docker_runner --package_name={0} --cmd='/root/one_docker/package/"


class OneDockerService:
    """OneDockerService is responsible for executing executable(s) in a Fargate container"""

    def __init__(self, container_svc: ContainerService) -> None:
        """Constructor of OneDockerService
        container_svc -- service to spawn container instances
        TODO: log_svc -- service to read cloudwatch logs
        """
        if container_svc is None:
            raise ValueError(f"Dependency is missing. container_svc={container_svc}, ")

        self.container_svc = container_svc
        self.logger: logging.Logger = logging.getLogger(__name__)

    def start_container(
        self,
        container_definition: str,
        package_name: str,
        cmd_args: str,
        timeout: Optional[int] = None,
    ) -> ContainerInstance:
        # TODO: ContainerInstance mapper
        return asyncio.run(
            self.start_containers_async(
                container_definition, package_name, [cmd_args], timeout
            )
        )[0]

    def start_containers(
        self,
        container_definition: str,
        package_name: str,
        cmd_args_list: List[str],
        timeout: Optional[int] = None,
    ) -> List[ContainerInstance]:
        return asyncio.run(
            self.start_containers_async(
                container_definition, package_name, cmd_args_list, timeout
            )
        )

    async def start_containers_async(
        self,
        container_definition: str,
        package_name: str,
        cmd_args_list: List[str],
        timeout: Optional[int] = None,
    ) -> List[ContainerInstance]:
        """Asynchronously spin up one container per element in input command list."""
        cmds = [
            self._get_cmd(package_name, cmd_args, timeout) for cmd_args in cmd_args_list
        ]
        self.logger.info("Spinning up container instances")
        container_ids = await self.container_svc.create_instances_async(
            container_definition, cmds
        )
        return container_ids

    def _get_exe_name(self, package_name: str) -> str:
        return package_name.split("/")[1]

    def _get_cmd(
        self, package_name: str, cmd_args: str, timeout: Optional[int] = None
    ) -> str:
        cmd_timeout = ""
        """
        If we passed --timeout=None, the schema module will raise error,
        since f-string converts None to "None" and schema treats None
        in --timeout=None as a string
        """
        if timeout is not None:
            cmd_timeout = f" --timeout={timeout}"
        return f"{ONE_DOCKER_CMD_PREFIX.format(package_name, timeout)}{self._get_exe_name(package_name)} {cmd_args}'{cmd_timeout}"
