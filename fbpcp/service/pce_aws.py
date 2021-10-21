#!/usr/bin/env python3
# Copyright (c) Facebook, Inc. and its affiliates.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

# pyre-strict

import logging
from typing import Optional, Any, Dict

from fbpcp.entity.pce import PCE
from fbpcp.entity.pce_compute import PCECompute
from fbpcp.entity.pce_network import PCENetwork
from fbpcp.gateway.ec2 import EC2Gateway
from fbpcp.gateway.ecs import ECSGateway
from fbpcp.service.pce import PCEService


PCE_ID_KEY = "pce:pce-id"
SHARED_TASK_DEFINITION_PREFIX = "onedocker-task-shared-"


class AWSPCEService(PCEService):
    def __init__(
        self,
        region: str,
        access_key_id: Optional[str] = None,
        access_key_data: Optional[str] = None,
        config: Optional[Dict[str, Any]] = None,
    ) -> None:
        self.logger: logging.Logger = logging.getLogger(__name__)
        self.region = region
        self.access_key_id = access_key_id
        self.access_key_data = access_key_data
        self.config = config

    def get_pce(
        self,
        pce_id: str,
    ) -> PCE:
        pce_network = self._get_network(pce_id)
        pce_compute = self._get_compute(pce_id)
        return PCE(pce_id, self.region, pce_network, pce_compute)

    def _get_network(self, pce_id: str) -> PCENetwork:
        ec2_gateway = EC2Gateway(
            self.region, self.access_key_id, self.access_key_data, self.config
        )
        tags = {PCE_ID_KEY: pce_id}
        vpcs = ec2_gateway.describe_vpcs(tags=tags)
        vpc = vpcs[0] if vpcs else None
        subnets = ec2_gateway.describe_subnets(tags=tags)
        firewall_rulesets = ec2_gateway.describe_security_groups(tags=tags)
        route_tables = ec2_gateway.describe_route_tables(tags=tags)
        route_table = route_tables[0] if route_tables else None
        vpc_peering = None
        if vpc:
            vpc_peerings = ec2_gateway.describe_vpc_peerings(
                vpc_id=vpc.vpc_id, tags=tags
            )
            vpc_peering = vpc_peerings[0] if vpc_peerings else None
        return PCENetwork(
            region=self.region,
            vpc=vpc,
            subnets=subnets,
            route_table=route_table,
            vpc_peering=vpc_peering,
            firewall_rulesets=firewall_rulesets,
        )

    def _get_compute(self, pce_id: str) -> PCECompute:
        ecs_gateway = ECSGateway(
            self.region, self.access_key_id, self.access_key_data, self.config
        )
        tags = {PCE_ID_KEY: pce_id}
        clusters = ecs_gateway.describe_clusters(tags=tags)
        cluster = clusters[0] if clusters else None
        container_definitions = ecs_gateway.describe_task_definitions(tags=tags)
        if container_definitions:
            container_definition = container_definitions[0]
        else:
            container_definition = ecs_gateway.describe_task_definition(
                SHARED_TASK_DEFINITION_PREFIX + self.region
            )
        return PCECompute(self.region, cluster, container_definition)
