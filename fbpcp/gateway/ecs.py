#!/usr/bin/env python3
# Copyright (c) Meta Platforms, Inc. and affiliates.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

# pyre-strict

from concurrent.futures import ThreadPoolExecutor
from typing import Any, Dict, Final, Iterator, List, Optional, Tuple

import boto3
from botocore.client import BaseClient
from fbpcp.decorator.error_handler import error_handler
from fbpcp.decorator.metrics import duration_time, error_counter, request_counter
from fbpcp.entity.cluster_instance import Cluster
from fbpcp.entity.container_definition import ContainerDefinition
from fbpcp.entity.container_instance import ContainerInstance
from fbpcp.error.pcp import PcpError
from fbpcp.gateway.aws import AWSGateway
from fbpcp.mapper.aws import (
    map_ecstask_to_containerinstance,
    map_ecstaskdefinition_to_containerdefinition,
    map_esccluster_to_clusterinstance,
)
from fbpcp.metrics.emitter import MetricsEmitter
from fbpcp.metrics.getter import MetricsGetter

METRICS_RUN_TASK_COUNT = "aws.ecs.run_task.count"
METRICS_RUN_TASK_ERROR_COUNT = "aws.ecs.run_task.error.count"
METRICS_RUN_TASK_DURATION = "aws.ecs.run_task.duration"


class ECSGateway(AWSGateway, MetricsGetter):
    def __init__(
        self,
        region: str,
        access_key_id: Optional[str] = None,
        access_key_data: Optional[str] = None,
        config: Optional[Dict[str, Any]] = None,
        metrics: Optional[MetricsEmitter] = None,
        session_token: Optional[str] = None,
    ) -> None:
        super().__init__(region, access_key_id, access_key_data, config, session_token)

        self.client: BaseClient = self.create_ecs_client()
        self.metrics: Final[Optional[MetricsEmitter]] = metrics

    def has_metrics(self) -> bool:
        return self.metrics is not None

    def get_metrics(self) -> MetricsEmitter:
        if not self.metrics:
            raise PcpError("ECSGateway doesn't have metrics emitter")

        return self.metrics

    # TODO: Create an interface to create a client per environment
    def create_ecs_client(
        self,
    ) -> BaseClient:
        return boto3.client("ecs", region_name=self.region, **self.config)

    @error_counter(METRICS_RUN_TASK_ERROR_COUNT)
    @request_counter(METRICS_RUN_TASK_COUNT)
    @duration_time(METRICS_RUN_TASK_DURATION)
    @error_handler
    def run_task(
        self,
        task_definition: str,
        container: str,
        cmd: str,
        cluster: str,
        subnets: List[str],
        env_vars: Optional[Dict[str, str]] = None,
    ) -> ContainerInstance:
        environment = []
        if env_vars:
            environment = [
                {"name": env_name, "value": env_value}
                for env_name, env_value in env_vars.items()
            ]
        response = self.client.run_task(
            taskDefinition=task_definition,
            cluster=cluster,
            networkConfiguration={
                "awsvpcConfiguration": {
                    "subnets": subnets,
                    "assignPublicIp": "ENABLED",
                }
            },
            overrides={
                "containerOverrides": [
                    {
                        "name": container,
                        "command": [cmd],
                        "environment": environment,
                    }
                ]
            },
        )

        if not response["tasks"]:
            # common failures: https://docs.aws.amazon.com/AmazonECS/latest/developerguide/api_failures_messages.html
            failure = response["failures"][0]
            self.logger.error(f"ECSGateway failed to create a task. Failure: {failure}")
            raise PcpError(f"ECS failure: reason: {failure['reason']}")

        return map_ecstask_to_containerinstance(response["tasks"][0])

    @error_handler
    def describe_tasks(
        self, cluster: str, tasks: List[str]
    ) -> List[Optional[ContainerInstance]]:
        response = self.client.describe_tasks(
            cluster=cluster, tasks=tasks
        )  # not necessarily in order of `tasks`

        arn_to_instance: Dict[str, Optional[ContainerInstance]] = {}
        for resp_task_dict in response["tasks"]:
            arn_to_instance[
                resp_task_dict["taskArn"]
            ] = map_ecstask_to_containerinstance(resp_task_dict)

        for failure in response["failures"]:
            self.logger.warning(
                f"ECSGateway failed to describe a task {failure['arn']}, reason: {failure['reason']}"
            )

        return [arn_to_instance.get(arn, None) for arn in tasks]

    @error_handler
    def describe_task(self, cluster: str, task: str) -> Optional[ContainerInstance]:
        return self.describe_tasks(cluster, [task])[0]

    @error_handler
    def list_tasks(
        self,
        cluster: str,
        nextToken: Optional[str] = None,
    ) -> Tuple[List[str], str]:
        kwargs = {"cluster": cluster}
        if nextToken:
            kwargs["nextToken"] = nextToken

        response = self.client.list_tasks(**kwargs)
        return response.get("taskArns", None), response.get("nextToken", None)

    @error_handler
    def iterate_list_tasks(
        self,
        cluster: str,
    ) -> Iterator[str]:
        list_tasks = self.list_tasks(cluster)
        if list_tasks[0]:
            yield from list_tasks[0]

        while list_tasks[1]:
            list_tasks = self.list_tasks(cluster, list_tasks[1])
            if list_tasks[0]:
                yield from list_tasks[0]

    @error_handler
    def stop_task(self, cluster: str, task_id: str) -> None:
        self.client.stop_task(
            cluster=cluster,
            task=task_id,
        )

    @error_handler
    def describe_clusters(
        self,
        clusters: Optional[List[str]] = None,
        tags: Optional[Dict[str, str]] = None,
    ) -> List[Cluster]:
        if not clusters:
            clusters = self.list_clusters()
        response = self.client.describe_clusters(clusters=clusters, include=["TAGS"])
        cluster_instances = [
            map_esccluster_to_clusterinstance(cluster)
            for cluster in response["clusters"]
        ]
        if tags:
            return list(
                filter(
                    lambda cluster_instance: tags.items()
                    <= cluster_instance.tags.items(),
                    cluster_instances,
                )
            )
        return cluster_instances

    @error_handler
    def describe_cluster(self, cluster: str) -> Cluster:
        return self.describe_clusters(clusters=[cluster])[0]

    @error_handler
    def list_clusters(self) -> List[str]:
        return self.client.list_clusters()["clusterArns"]

    @error_handler
    def describe_task_definition(self, task_defination: str) -> ContainerDefinition:
        return self._describe_task_definition_core(self.client, task_defination)

    def _describe_task_definition_core(
        self,
        client: BaseClient,
        task_defination: str,
    ) -> ContainerDefinition:
        response = client.describe_task_definition(
            taskDefinition=task_defination, include=["TAGS"]
        )
        return map_ecstaskdefinition_to_containerdefinition(
            response["taskDefinition"], response["tags"]
        )

    @error_handler
    def list_task_definitions(self, limit: int = 1000) -> List[str]:
        task_definitions = []
        next_token = ""

        while len(task_definitions) < limit:
            task_definition_response = self.client.list_task_definitions(
                nextToken=next_token,
            )
            task_definitions.extend(task_definition_response["taskDefinitionArns"])
            next_token = task_definition_response.get("nextToken")
            if not next_token:
                break

        if limit and len(task_definitions) > limit:
            task_definitions = task_definitions[:limit]
        return task_definitions

    @error_handler
    def describe_task_definitions(
        self,
        task_definitions: Optional[List[str]] = None,
        tags: Optional[Dict[str, str]] = None,
    ) -> List[ContainerDefinition]:
        if not task_definitions:
            task_definitions = self.list_task_definitions()
        container_definitions = []
        for arn in task_definitions:
            container_definition = self.describe_task_definition(arn)
            if tags is None or tags.items() <= container_definition.tags.items():
                container_definitions.append(container_definition)

        return container_definitions

    @error_handler
    def describe_task_definitions_in_parallel(
        self,
        task_definitions: Optional[List[str]] = None,
        tags: Optional[Dict[str, str]] = None,
        max_workers: int = 8,
    ) -> List[ContainerDefinition]:
        if not task_definitions:
            task_definitions = self.list_task_definitions()
        container_definitions = []
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            input_arguments = [
                (
                    self.create_ecs_client(),
                    definition,
                )
                for definition in task_definitions
            ]
            results = executor.map(
                lambda args: self._describe_task_definition_core(*args),
                input_arguments,
            )
            for container_definition in results:
                if tags is None or tags.items() <= container_definition.tags.items():
                    container_definitions.append(container_definition)

        return container_definitions
