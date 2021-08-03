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

DEFAULT_BINARY_VERSION = "latest"


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

        self.onedocker_svc = OneDockerService(self.container_svc, self.task_definition)

    """
    The game_args should be consistent with the game_config, which should be
    defined in caller's game repository.

    For example,
    If the game config looks like this:

    game_config = {
    "game": {
        "onedocker_package_name": "package_name",
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

        instance = MPCInstance.create_instance(
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
        version: str = DEFAULT_BINARY_VERSION,
    ) -> MPCInstance:
        return asyncio.run(
            self.start_instance_async(
                instance_id, output_files, server_ips, timeout, version
            )
        )

    async def start_instance_async(
        self,
        instance_id: str,
        output_files: Optional[List[str]] = None,
        server_ips: Optional[List[str]] = None,
        timeout: Optional[int] = None,
        version: str = DEFAULT_BINARY_VERSION,
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
            version,
        )

        if len(instance.containers) != instance.num_workers:
            self.logger.warning(
                f"Instance {instance_id} has {len(instance.containers)} containers spun up, but expecting {instance.num_workers} containers!"
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

    def stop_instance(self, instance_id: str) -> MPCInstance:
        instance = self.instance_repository.read(instance_id)
        container_ids = [instance.instance_id for instance in instance.containers]
        if container_ids:
            errors = self.onedocker_svc.stop_containers(container_ids)
            error_msg = list(filter(lambda _: _[1], zip(container_ids, errors)))

            if error_msg:
                self.logger.error(
                    f"We encountered errors when stopping containers: {error_msg}"
                )

        instance.status = MPCInstanceStatus.CANCELED
        self.instance_repository.update(instance)
        self.logger.info(f"MPC instance {instance_id} has been successfully canceled.")

        return instance

    def get_instance(self, instance_id: str) -> MPCInstance:
        self.logger.info(f"Getting MPC instance: {instance_id}")
        return self.instance_repository.read(instance_id)

    def update_instance(self, instance_id: str) -> MPCInstance:
        instance = self.instance_repository.read(instance_id)

        self.logger.info(f"Updating MPC instance: {instance_id}")

        if instance.status in [
            MPCInstanceStatus.COMPLETED,
            MPCInstanceStatus.FAILED,
            MPCInstanceStatus.CANCELED,
        ]:
            return instance

        # skip if no containers registered under instance yet
        if instance.containers:
            instance.containers = self._update_container_instances(instance.containers)

            if len(instance.containers) != instance.num_workers:
                self.logger.warning(
                    f"Instance {instance_id} has {len(instance.containers)} containers after update, but expecting {instance.num_workers} containers!"
                )

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
        version: str = DEFAULT_BINARY_VERSION,
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
                self.mpc_game_svc.build_onedocker_args(
                    game_name=game_name,
                    mpc_role=mpc_role,
                    server_ip=server_ip,
                    **game_arg,
                )
            )
        cmd_args_list = [cmd_args for (package_name, cmd_args) in cmd_tuple_list]

        return await self.onedocker_svc.start_containers_async(
            task_definition=self.task_definition,
            package_name=cmd_tuple_list[0][0],
            version=version,
            cmd_args_list=cmd_args_list,
            timeout=timeout,
        )

    def _update_container_instances(
        self, containers: List[ContainerInstance]
    ) -> List[ContainerInstance]:
        ids = [container.instance_id for container in containers]
        return self.container_svc.get_instances(ids)

    def _get_instance_status(self, instance: MPCInstance) -> MPCInstanceStatus:
        if instance.status is MPCInstanceStatus.CANCELED:
            return instance.status
        status = MPCInstanceStatus.COMPLETED

        for container in instance.containers:
            if container.status == ContainerInstanceStatus.FAILED:
                return MPCInstanceStatus.FAILED
            if container.status == ContainerInstanceStatus.UNKNOWN:
                return MPCInstanceStatus.UNKNOWN
            if container.status == ContainerInstanceStatus.STARTED:
                status = MPCInstanceStatus.STARTED

        return status
