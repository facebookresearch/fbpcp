#!/usr/bin/env python3
# Copyright (c) Meta Platforms, Inc. and affiliates.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

# pyre-strict

import asyncio
import logging
import time
from typing import Dict, Final, List, Optional, Union

from fbpcp.decorator.metrics import duration_time, error_counter, request_counter
from fbpcp.entity.certificate_request import CertificateRequest
from fbpcp.entity.container_insight import ContainerInsight
from fbpcp.entity.container_instance import ContainerInstance, ContainerInstanceStatus
from fbpcp.entity.container_permission import ContainerPermissionConfig
from fbpcp.entity.container_type import ContainerType
from fbpcp.error.pcp import PcpError
from fbpcp.metrics.emitter import MetricsEmitter
from fbpcp.metrics.getter import MetricsGetter
from fbpcp.service.container import ContainerService
from fbpcp.service.insights import InsightsService
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

METRICS_FAILED_CONTAINERS_COUNT = "onedocker.failed.containers.count"
METRICS_REQUESTED_CONTAINERS_COUNT = "onedocker.requested.containers.count"


class OneDockerService(MetricsGetter):
    """OneDockerService is responsible for executing a package(binary) in a container on Cloud"""

    def __init__(
        self,
        container_svc: ContainerService,
        task_definition: Optional[str] = None,
        metrics: Optional[MetricsEmitter] = None,
        container_cmd_prefix: Optional[str] = None,
        insights: Optional[InsightsService] = None,
    ) -> None:
        """Constructor of OneDockerService
        container_svc -- service to spawn container instances
        task_definition -- container definition to spawn container instances
        metrics -- metrics emitter to emit metrics
        insights -- insights service to emit insights
        """
        if container_svc is None:
            raise ValueError(f"Dependency is missing. container_svc={container_svc}, ")
        self.container_svc = container_svc
        self.task_definition = task_definition
        self.metrics: Final[Optional[MetricsEmitter]] = metrics
        self.container_cmd_prefix: str = (
            container_cmd_prefix if container_cmd_prefix else ONEDOCKER_CMD_PREFIX
        )
        self.insights: Final[Optional[InsightsService]] = insights
        self.logger: logging.Logger = logging.getLogger(__name__)

    def get_cluster(self) -> str:
        """Get the cluster of the container service

        Returns:
            The container service's cluster name
        """
        return self.container_svc.get_cluster()

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
        env_vars: Optional[Union[Dict[str, str], List[Dict[str, str]]]] = None,
        timeout: Optional[int] = None,
        tag: Optional[str] = None,
        certificate_request: Optional[CertificateRequest] = None,
        opa_workflow_path: Optional[str] = None,
        container_type: Optional[ContainerType] = None,
        permission: Optional[ContainerPermissionConfig] = None,
    ) -> ContainerInstance:
        """
        This function statrts one container for running MPC games.

        Args:
            package_name:       Name of running package within docker image
            task_definition:    Task definition required by docker containers. If specified, overrides OneDockerService's task definition
                                when starting this container
            version:            The version of the MPC binary to run. This parameter defaults to the 'latest' binary version.
            cmd_args:           A string that is used to override the command in docker containers
            env_vars:           Environment variable overrides in docker containers. When given a single dictionary,
                                it will be applied to all container. When given a list of dictionraies, each will be assigned
                                to one container.
            timeout:            container timeout. If specified, docker container would be forced to stop
            tag:                Tag for docker containers
            certificate_request: An optional instance of CertificateRequest that contains the parameters required to create a TLS certificate
            opa_workflow_path:  A string that denotes the path to a specified opa workflow. Supported Path type: local.
            permission:         A configuration which describes the container permissions

        """
        return self.start_containers(
            package_name=package_name,
            task_definition=task_definition,
            version=version,
            cmd_args_list=[cmd_args] if cmd_args else None,
            env_vars=env_vars,
            timeout=timeout,
            tag=tag,
            certificate_request=certificate_request,
            opa_workflow_path=opa_workflow_path,
            container_type=container_type,
            permission=permission,
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
        env_vars: Optional[Union[Dict[str, str], List[Dict[str, str]]]] = None,
        timeout: Optional[int] = None,
        tag: Optional[str] = None,
        certificate_request: Optional[CertificateRequest] = None,
        opa_workflow_path: Optional[str] = None,
        container_type: Optional[ContainerType] = None,
        permission: Optional[ContainerPermissionConfig] = None,
    ) -> List[ContainerInstance]:
        """Spin up cloud containers according to command arg list.

        Args:
            package_name:       Name of running package within docker image
            task_definition:    Task definition required by docker containers. If specified, overrides OneDockerService's task definition
                                when starting this container
            version:            The version of the MPC binary to run. This parameter defaults to the 'latest' binary version.
            cmd_args_list:      A list of command overrides in docker containers
            env_vars:           Environment variable overrides in docker containers. When given a single dictionary,
                                it will be applied to all container. When given a list of dictionraies, each will be assigned
                                to one container.
            timeout:            container timeout. If specified, docker container would be forced to stop
            tag:                Tag for docker containers
            certificate_request: An optional instance of CertificateRequest that contains the parameters required to create a TLS certificate
            opa_workflow_path:  A string that denotes the path to a specified opa workflow. Supported Path type: local.
            permission:         A configuration which describes the container permissions

        Returns:
            A list of the containers that were successfuly started
        """
        if not cmd_args_list:
            raise ValueError("Command Argument List shouldn't be None or Empty")

        if type(env_vars) is list and len(env_vars) != len(cmd_args_list):
            raise ValueError(
                f"Length of env_vars {len(env_vars)} not equal to the length of cmd_args_list {len(cmd_args_list)}."
            )

        cmds = [
            self._get_cmd(
                package_name,
                version,
                cmd_args,
                timeout,
                certificate_request,
                opa_workflow_path,
            )
            for cmd_args in cmd_args_list
        ]
        container_type_log = f" of {container_type} type" if container_type else ""
        self.logger.info(
            f"Spinning up {len(cmds)} container instance[s]" + container_type_log
        )

        task_definition = task_definition or self.task_definition
        if not task_definition:
            raise ValueError(
                "task definition should be specified when spinning up containers"
            )
        containers = self.container_svc.create_instances(
            container_definition=task_definition,
            cmds=cmds,
            env_vars=env_vars,
            container_type=container_type,
            permission=permission,
        )
        if containers:
            self.logger.info(
                f"Spun up {len(containers)} ({containers[0].cpu}vCPU, {containers[0].memory}GB) containers"
            )

        if self.metrics:
            name = f"{METRICS_CONTAINER_COUNT}.{self.container_svc.get_region()}.{self.container_svc.get_cluster()}"
            name = f"{METRICS_CONTAINER_COUNT}.{tag}" if tag else name
            self.metrics.count(name, len(containers))

        if self.insights:
            for container in containers:
                self.insights.emit(self._get_insight(container))

        return containers

    async def wait_for_pending_containers(
        self, container_ids: List[str]
    ) -> List[ContainerInstance]:
        tasks = [
            asyncio.create_task(self.wait_for_pending_container(container_id))
            for container_id in container_ids
        ]
        res = await asyncio.gather(*tasks)

        if self.metrics:
            failed_metrics = f"{METRICS_FAILED_CONTAINERS_COUNT}.{self.container_svc.get_region()}.{self.container_svc.get_cluster()}"
            requested_metrics = f"{METRICS_REQUESTED_CONTAINERS_COUNT}.{self.container_svc.get_region()}.{self.container_svc.get_cluster()}"
            self.metrics.count(requested_metrics, len(res))

            """ The following sum(condition(c) for c in list) will count the number of elements c that match a certain condition(c).
            This creates a generator expression returns True for each element that matches the condition and False otherwise.
            Since the True and False values are represented as integer values 1 and 0, by summing over the iterable, we will get the total number of matching elements.
            """
            failed_count = sum(
                not (container and container.status == ContainerInstanceStatus.STARTED)
                for container in res
            )
            self.metrics.count(
                failed_metrics,
                failed_count,
            )
        containers = [checked_cast(ContainerInstance, container) for container in res]

        if self.insights:
            for container in containers:
                await self.insights.emit_async(self._get_insight(container))

        return containers

    async def wait_for_pending_container(
        self, container_id: str
    ) -> Optional[ContainerInstance]:
        updated_container = self.get_containers([container_id])[0]
        while (
            not updated_container
            or not updated_container.ip_address
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
        # TODO We will need long term discussion on the container capacity of onedocker
        """Get one or more container instances

        Args:
            instance_ids: a list of the container instances.

        Returns:
            A list of Optional, in the same order as the input ids. For example, if
            users pass 3 instance_ids and the second instance could not be found,
            then returned list should also have 3 elements, with the 2nd elements being None.
        """
        return self.container_svc.get_instances(instance_ids)

    def get_container(self, instance_id: str) -> Optional[ContainerInstance]:
        return self.container_svc.get_instance(instance_id)

    def _get_exe_name(self, package_name: str) -> str:
        return package_name.split("/")[1]

    def _get_cmd(
        self,
        package_name: str,
        version: str = DEFAULT_BINARY_VERSION,
        cmd_args: Optional[str] = None,
        timeout: Optional[int] = None,
        certificate_request: Optional[CertificateRequest] = None,
        opa_workflow_path: Optional[str] = None,
    ) -> str:
        args_dict = {"exe_args": cmd_args, "version": version, "timeout": timeout}
        if certificate_request:
            args_dict["cert_params"] = certificate_request.convert_to_cert_params()
        if opa_workflow_path:
            args_dict["opa_workflow_path"] = opa_workflow_path
        runner_args = build_cmd_args(**args_dict)
        return self.container_cmd_prefix.format(
            package_name=package_name,
            runner_args=runner_args,
        ).strip()

    def _get_insight(self, container: ContainerInstance) -> str:
        return ContainerInsight(
            time=time.time(),
            cluster_name=self.get_cluster(),
            instance_id=container.instance_id,
            status=container.status.value,
            exit_code=container.exit_code,
        ).convert_to_str_with_class_name()
