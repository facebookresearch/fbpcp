#!/usr/bin/env python3
# Copyright (c) Meta Platforms, Inc. and affiliates.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

# pyre-strict

from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from fbpcp.gateway.ec2 import EC2Gateway
from fbpcp.gateway.ecs import ECSGateway
from pce.validator.message_templates.resource_names import ResourceNamePlural

PCE_ID_KEY = "pce:pce-id"


@dataclass
class DuplicatePCEResource:
    """
    Dataclass to represent information about a duplicated PCE resource, stored
    as formatted strings ready to be included in human readable error messages
    """

    resource_name_plural: str
    duplicate_resource_ids: str


class DuplicatePCEResourcesChecker:
    def __init__(
        self,
        region: str,
        access_key_id: Optional[str] = None,
        access_key_data: Optional[str] = None,
        config: Optional[Dict[str, Any]] = None,
    ) -> None:
        self.region = region
        self.ec2_gateway = EC2Gateway(region, access_key_id, access_key_data, config)
        self.ecs_gateway = ECSGateway(region, access_key_id, access_key_data, config)

    def check_pce(
        self,
        pce_id: str,
    ) -> List[DuplicatePCEResource]:
        tags = {PCE_ID_KEY: pce_id}
        duplicate_pce_resources = []

        # VPCs
        vpcs = self.ec2_gateway.describe_vpcs(tags=tags)
        if vpcs and len(vpcs) > 1:
            multiple_vpc_ids = ", ".join([vpc.vpc_id for vpc in vpcs])
            duplicate_pce_resources.append(
                DuplicatePCEResource(
                    resource_name_plural=ResourceNamePlural.VPC.value,
                    duplicate_resource_ids=multiple_vpc_ids,
                )
            )

        # route tables
        route_tables = self.ec2_gateway.describe_route_tables(tags=tags)
        if route_tables and len(route_tables) > 1:
            multiple_route_table_ids = ", ".join(
                [route_table.id for route_table in route_tables]
            )
            duplicate_pce_resources.append(
                DuplicatePCEResource(
                    resource_name_plural=ResourceNamePlural.ROUTE_TABLE.value,
                    duplicate_resource_ids=multiple_route_table_ids,
                )
            )

        # vpc peering
        vpc = vpcs[0] if vpcs else None
        if vpc:
            vpc_peerings = self.ec2_gateway.describe_vpc_peerings(
                vpc_id=vpc.vpc_id, tags=tags
            )
            if vpc_peerings and len(vpc_peerings) > 1:
                multiple_vpc_peering_ids = ", ".join(
                    [vpc_peering.id for vpc_peering in vpc_peerings]
                )
                duplicate_pce_resources.append(
                    DuplicatePCEResource(
                        resource_name_plural=ResourceNamePlural.VPC_PEERING.value,
                        duplicate_resource_ids=multiple_vpc_peering_ids,
                    )
                )

        # cluster
        clusters = self.ecs_gateway.describe_clusters(tags=tags)
        if clusters and len(clusters) > 1:
            mutiple_cluster_arns = ", ".join(
                [cluster.cluster_arn for cluster in clusters]
            )
            duplicate_pce_resources.append(
                DuplicatePCEResource(
                    resource_name_plural=ResourceNamePlural.CLUSTER.value,
                    duplicate_resource_ids=mutiple_cluster_arns,
                )
            )

        # cluster definitions
        container_definitions = self.ecs_gateway.describe_task_definitions(tags=tags)
        if container_definitions and len(container_definitions) > 1:
            multiple_container_definition_ids = ", ".join(
                [
                    container_definition.id
                    for container_definition in container_definitions
                ]
            )
            duplicate_pce_resources.append(
                DuplicatePCEResource(
                    resource_name_plural=ResourceNamePlural.CONTAINER_DEFINITION.value,
                    duplicate_resource_ids=multiple_container_definition_ids,
                )
            )
        return duplicate_pce_resources
