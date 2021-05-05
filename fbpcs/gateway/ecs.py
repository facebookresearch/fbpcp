#!/usr/bin/env python3
# Copyright (c) Facebook, Inc. and its affiliates.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

# pyre-strict

from typing import Any, Dict, List, Optional

import boto3
from fbpcs.decorator.error_handler import error_handler
from fbpcs.entity.cluster_instance import Cluster
from fbpcs.entity.container_instance import ContainerInstance
from fbpcs.mapper.aws import (
    map_ecstask_to_containerinstance,
    map_esccluster_to_clusterinstance,
)


class ECSGateway:
    def __init__(
        self,
        region: str,
        access_key_id: Optional[str],
        access_key_data: Optional[str],
        config: Optional[Dict[str, Any]] = None,
    ) -> None:
        self.region = region
        config = config or {}

        if access_key_id is not None:
            config["aws_access_key_id"] = access_key_id

        if access_key_data is not None:
            config["aws_secret_access_key"] = access_key_data

        # pyre-ignore
        self.client = boto3.client("ecs", region_name=self.region, **config)

    @error_handler
    def run_task(
        self, task_definition: str, container: str, cmd: str, cluster: str, subnet: str
    ) -> ContainerInstance:
        response = self.client.run_task(
            taskDefinition=task_definition,
            cluster=cluster,
            networkConfiguration={
                "awsvpcConfiguration": {
                    "subnets": [subnet],
                    "assignPublicIp": "ENABLED",
                }
            },
            overrides={"containerOverrides": [{"name": container, "command": [cmd]}]},
        )

        return map_ecstask_to_containerinstance(response["tasks"][0])

    @error_handler
    def describe_tasks(self, cluster: str, tasks: List[str]) -> List[ContainerInstance]:
        response = self.client.describe_tasks(cluster=cluster, tasks=tasks)
        return [map_ecstask_to_containerinstance(task) for task in response["tasks"]]

    @error_handler
    def describe_task(self, cluster: str, task: str) -> ContainerInstance:
        return self.describe_tasks(cluster, [task])[0]

    @error_handler
    def list_tasks(self, cluster: str) -> List[str]:
        return self.client.list_tasks(cluster=cluster)["taskArns"]

    @error_handler
    def stop_task(self, cluster: str, task_id: str) -> Dict[str, Any]:
        return self.client.stop_task(
            cluster=cluster,
            task=task_id,
        )

    @error_handler
    def describe_clusters(self, clusters: List[str]) -> List[Cluster]:
        response = self.client.describe_clusters(clusters=clusters, include=["TAGS"])
        return [
            map_esccluster_to_clusterinstance(cluster)
            for cluster in response["clusters"]
        ]

    @error_handler
    def describe_cluster(self, cluster: str) -> Cluster:
        return self.describe_clusters([cluster])[0]

    @error_handler
    def list_clusters(self) -> List[str]:
        return self.client.list_clusters()["clusterArns"]
