#!/usr/bin/env python3
# Copyright (c) Facebook, Inc. and its affiliates.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

# pyre-strict

import asyncio
import logging
from typing import Any, Dict, List, Optional

from fbpcs.entity.container_instance import ContainerInstance, ContainerInstanceStatus
from fbpcs.entity.mpc_instance import MPCInstance, MPCInstanceStatus, MPCRole
from fbpcs.repository.mpc_instance import MPCInstanceRepository
from fbpcs.service.container import ContainerService
from fbpcs.service.mpc_game import MPCGameService
from fbpcs.service.onedocker import OneDockerService
from fbpcs.service.storage import StorageService
from fbpcs.util.typing import checked_cast


class MPCService:
    """MPCService is responsible for distributing a larger MPC game to multiple
    MPC workers
    """

    def __init__(
        self,
        container_svc: ContainerService,
        storage_svc: StorageService,
        instance_repository: MPCInstanceRepository,
        task_definition: str,
        mpc_game_svc: MPCGameService,
    ) -> None:
        """Constructor of MPCService
        Keyword arguments:
        container_svc -- service to spawn container instances
        storage_svc -- service to read/write input/output files
        instance_repository -- repository to CRUD MPCInstance
        task_definition -- containers task definition
        mpc_game_svc -- service to generate package name and game arguments.
        """
        if (
            container_svc is None
            or storage_svc is None
            or instance_repository is None
            or mpc_game_svc is None
        ):
            raise ValueError(
                f"Dependency is missing. container_svc={container_svc}, mpc_game_svc={mpc_game_svc}, "
                f"storage_svc={storage_svc}, instance_repository={instance_repository}"
            )

        self.container_svc = container_svc
        self.storage_svc = storage_svc
        self.instance_repository = instance_repository
        self.task_definition = task_definition
        self.mpc_game_svc: MPCGameService = mpc_game_svc
        self.logger: logging.Logger = logging.getLogger(__name__)

        self.onedocker_svc = OneDockerService(self.container_svc)

    """
    The game_args should be consistent with the game_config, which should be
    defined in caller's game repository.

    For example,
    If the game config looks like this:

    game_config = {
    "game": {
        "one_docker_package_name": "package_name",
        "arguments": [
            {"name": "input_filenames", "required": True},
            {"name": "input_directory", "required": True},
            {"name": "output_filenames", "required": True},
            {"name": "output_directory", "required": True},
            {"name": "concurrency", "required": True},
        ],
    },

    The game args should look like this:
    [
        # 1st container
        {
            "input_filenames": input_path_1,
            "input_directory": input_directory,
            "output_filenames": output_path_1,
            "output_directory": output_directory,
            "concurrency": cocurrency,
        },
        # 2nd container
        {
            "input_filenames": input_path_2,
            "input_directory": input_directory,
            "output_filenames": output_path_2,
            "output_directory": output_directory,
            "concurrency": cocurrency,
        },
    ]
    """

    def create_instance(
        self,
        instance_id: str,
        game_name: str,
        mpc_role: MPCRole,
        num_workers: int,
        server_ips: Optional[List[str]] = None,
        game_args: Optional[List[Dict[str, Any]]] = None,
    ) -> MPCInstance:
        self.logger.info(f"Creating MPC instance: {instance_id}")

        instance = MPCInstance(
            instance_id=instance_id,
            game_name=game_name,
            mpc_role=mpc_role,
            num_workers=num_workers,
            server_ips=server_ips,
            status=MPCInstanceStatus.CREATED,
            game_args=game_args,
        )

        self.instance_repository.create(instance)
        return instance

    def start_instance(
        self,
        instance_id: str,
        output_files: Optional[List[str]] = None,
        server_ips: Optional[List[str]] = None,
        timeout: Optional[int] = None,
    ) -> MPCInstance:
        return asyncio.run(
            self.start_instance_async(instance_id, output_files, server_ips, timeout)
        )

    async def start_instance_async(
        self,
        instance_id: str,
        output_files: Optional[List[str]] = None,
        server_ips: Optional[List[str]] = None,
        timeout: Optional[int] = None,
    ) -> MPCInstance:
        """To run a distributed MPC game
        Keyword arguments:
        instance_id -- unique id to identify the MPC instance
        """
        instance = self.instance_repository.read(instance_id)
        self.logger.info(f"Starting MPC instance: {instance_id}")

        if instance.mpc_role is MPCRole.CLIENT and not server_ips:
            raise ValueError("Missing server_ips")

        # spin up containers
        self.logger.info("Spinning up container instances")
        game_args = instance.game_args
        instance.containers = await self._spin_up_containers_onedocker(
            instance.game_name,
            instance.mpc_role,
            instance.num_workers,
            game_args,
            server_ips,
            timeout,
        )

        if instance.mpc_role is MPCRole.SERVER:
            ip_addresses = [
                checked_cast(str, instance.ip_address)
                for instance in instance.containers
            ]
            instance.server_ips = ip_addresses

        instance.status = MPCInstanceStatus.STARTED
        self.instance_repository.update(instance)

        return instance

    def get_instance(self, instance_id: str) -> MPCInstance:
        self.logger.info(f"Getting MPC instance: {instance_id}")
        return self.instance_repository.read(instance_id)

    def update_instance(self, instance_id: str) -> MPCInstance:
        instance = self.instance_repository.read(instance_id)

        self.logger.info(f"Updating MPC instance: {instance_id}")

        if instance.status in [MPCInstanceStatus.COMPLETED, MPCInstanceStatus.FAILED]:
            return instance

        if instance.containers is not None:
            instance.containers = self._update_container_instances(instance.containers)
            instance.status = self._get_instance_status(instance)
            self.instance_repository.update(instance)

        return instance

    async def _spin_up_containers_onedocker(
        self,
        game_name: str,
        mpc_role: MPCRole,
        num_containers: int,
        game_args: Optional[List[Dict[str, Any]]] = None,
        ip_addresses: Optional[List[str]] = None,
        timeout: Optional[int] = None,
    ) -> List[ContainerInstance]:
        if game_args is not None and len(game_args) != num_containers:
            raise ValueError(
                "The number of containers is not consistent with the number of game argument dictionary."
            )
        if ip_addresses is not None and len(ip_addresses) != num_containers:
            raise ValueError(
                "The number of containers is not consistent with number of ip addresses."
            )
        cmd_tuple_list = []
        for i in range(num_containers):
            game_arg = game_args[i] if game_args is not None else {}
            server_ip = ip_addresses[i] if ip_addresses is not None else None
            cmd_tuple_list.append(
                self.mpc_game_svc.build_one_docker_args(
                    game_name=game_name,
                    mpc_role=mpc_role,
                    server_ip=server_ip,
                    **game_arg,
                )
            )
        cmd_args_list = [cmd_args for (package_name, cmd_args) in cmd_tuple_list]

        return await self.onedocker_svc.start_containers_async(
            self.task_definition, cmd_tuple_list[0][0], cmd_args_list, timeout
        )

    def _update_container_instances(
        self, containers: List[ContainerInstance]
    ) -> List[ContainerInstance]:
        ids = [container.instance_id for container in containers]
        return self.container_svc.get_instances(ids)

    def _get_instance_status(self, instance: MPCInstance) -> MPCInstanceStatus:
        status = MPCInstanceStatus.COMPLETED

        for container in instance.containers:
            if container.status == ContainerInstanceStatus.FAILED:
                return MPCInstanceStatus.FAILED
            if container.status == ContainerInstanceStatus.UNKNOWN:
                return MPCInstanceStatus.UNKNOWN
            if container.status == ContainerInstanceStatus.STARTED:
                status = MPCInstanceStatus.STARTED

        return status
