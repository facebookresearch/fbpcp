#!/usr/bin/env python3
# Copyright (c) Facebook, Inc. and its affiliates.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

# pyre-strict

import logging
from typing import List, Optional

from fbpcp.entity.cluster_instance import Cluster
from fbpcp.entity.container_instance import ContainerInstance
from fbpcp.intern.gateway.ecs_fb import FBECSGateway
from fbpcp.metrics.emitter import MetricsEmitter
from fbpcp.service.cluster import ClusterService


class AWSClusterService(ClusterService):
    def __init__(
        self,
        region: str,
        cluster: str,
        account: str,
        role: Optional[str] = None,
        metrics: Optional[MetricsEmitter] = None,
    ) -> None:
        self.logger: logging.Logger = logging.getLogger(__name__)
        self.region = region
        self.cluster = cluster
        self.account = account
        self.role = role
        self.metrics = metrics
        self.ecs_gateway = FBECSGateway(
            account=account, role=role, region=region, metrics=metrics
        )

    def get_region(
        self,
    ) -> str:
        return self.region

    def list_clusters(
        self,
    ) -> List[Cluster]:
        return self.ecs_gateway.describe_clusters()

    def list_instances(
        self,
        cluster_name: str,
    ) -> List[ContainerInstance]:
        task_arns = self.ecs_gateway.list_tasks(cluster_name)
        if not task_arns:
            return []
        return self.ecs_gateway.describe_tasks(cluster_name, task_arns)
