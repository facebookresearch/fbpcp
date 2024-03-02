#!/usr/bin/env python3
# Copyright (c) Meta Platforms, Inc. and affiliates.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

# pyre-unsafe

import unittest
from unittest.mock import MagicMock, patch

from fbpcp.entity.cluster_instance import Cluster
from fbpcp.entity.container_definition import ContainerDefinition
from fbpcp.entity.route_table import RouteTable
from fbpcp.entity.vpc_instance import Vpc
from fbpcp.entity.vpc_peering import VpcPeering
from pce.validator.duplicate_pce_resources_checker import (
    DuplicatePCEResource,
    DuplicatePCEResourcesChecker,
)
from pce.validator.message_templates.resource_names import ResourceNamePlural

TEST_REGION = "us-west-2"
TEST_PCE_ID = "foobar"


class TestDuplicatePCEResourcesChecker(unittest.TestCase):
    @patch("pce.validator.duplicate_pce_resources_checker.EC2Gateway")
    @patch("pce.validator.duplicate_pce_resources_checker.ECSGateway")
    def setUp(self, MockECSGateway, MockEC2Gateway):
        self.duplicate_resource_checker = DuplicatePCEResourcesChecker(
            region=TEST_REGION
        )
        self.duplicate_resource_checker.ec2_gateway = MockEC2Gateway()
        self.duplicate_resource_checker.ecs_gateway = MockECSGateway()

    def test_check_pce_no_resource_duplicated(self):
        # arrange: all describe resources call return single unique resource
        self.duplicate_resource_checker.ec2_gateway.describe_vpcs = MagicMock(
            return_value=[Vpc(vpc_id="vpc_id_1", cidr="")]
        )
        self.duplicate_resource_checker.ec2_gateway.describe_route_tables = MagicMock(
            return_value=[RouteTable(id="rtb_123", routes=MagicMock(), vpc_id="")]
        )
        self.duplicate_resource_checker.ec2_gateway.describe_vpc_peerings = MagicMock(
            return_value=[
                VpcPeering(
                    id="pcx_1234",
                    status=MagicMock(),
                    role=MagicMock(),
                    requester_vpc_id="",
                    accepter_vpc_id="",
                ),
            ]
        )
        self.duplicate_resource_checker.ecs_gateway.describe_clusters = MagicMock(
            return_value=[
                Cluster(
                    cluster_arn="arn:foo",
                    cluster_name="",
                    pending_tasks=1,
                    running_tasks=1,
                ),
            ]
        )
        self.duplicate_resource_checker.ecs_gateway.describe_task_definitions = (
            MagicMock(
                return_value=[
                    ContainerDefinition(
                        id="onedocker:task-foo:1",
                        image="",
                        cpu=1,
                        memory=1,
                        entry_point=[""],
                        environment={"": ""},
                        task_role_id="",
                    ),
                ]
            )
        )
        # act
        duplicate_resources = self.duplicate_resource_checker.check_pce(TEST_PCE_ID)
        # assert
        self.assertListEqual(
            duplicate_resources,
            [],  # no duplicates
        )

    def test_check_pce_multiple_resources_duplicated(self):
        # arrange: getting 2 VPCs in response to describe_vpcs call,
        describe_vpcs_response = [
            Vpc(vpc_id="vpc_id_1", cidr=""),
            Vpc(vpc_id="vpc_id_2", cidr=""),
        ]
        self.duplicate_resource_checker.ec2_gateway.describe_vpcs = MagicMock(
            return_value=describe_vpcs_response
        )
        # 2 RouteTable objects in response to describe_route_tables call, and
        describe_route_tables_response = [
            RouteTable(id="rtb_123", routes=MagicMock(), vpc_id=""),
            RouteTable(id="rtb_456", routes=MagicMock(), vpc_id=""),
        ]
        self.duplicate_resource_checker.ec2_gateway.describe_route_tables = MagicMock(
            return_value=describe_route_tables_response
        )
        # 2 Cluster objects in response to describe_clusters call
        describe_clusters_response = [
            Cluster(
                cluster_arn="arn:foo",
                cluster_name="",
                pending_tasks=1,
                running_tasks=1,
            ),
            Cluster(
                cluster_arn="arn:bar",
                cluster_name="",
                pending_tasks=1,
                running_tasks=1,
            ),
        ]
        self.duplicate_resource_checker.ecs_gateway.describe_clusters = MagicMock(
            return_value=describe_clusters_response
        )
        # act
        duplicate_resources = self.duplicate_resource_checker.check_pce(TEST_PCE_ID)
        # assert
        self.assertListEqual(
            duplicate_resources,
            [
                DuplicatePCEResource(
                    resource_name_plural=ResourceNamePlural.VPC.value,
                    duplicate_resource_ids="vpc_id_1, vpc_id_2",
                ),
                DuplicatePCEResource(
                    resource_name_plural=ResourceNamePlural.ROUTE_TABLE.value,
                    duplicate_resource_ids="rtb_123, rtb_456",
                ),
                DuplicatePCEResource(
                    resource_name_plural=ResourceNamePlural.CLUSTER.value,
                    duplicate_resource_ids="arn:foo, arn:bar",
                ),
            ],
        )

    def test_check_pce_single_resource_multiplicated(self):
        # arrange: getting 3 VPCs in response to describe_vpcs call
        describe_vpcs_response = [
            Vpc(vpc_id="vpc_id_1", cidr=""),
            Vpc(vpc_id="vpc_id_2", cidr=""),
            Vpc(vpc_id="vpc_id_3", cidr=""),
        ]
        self.duplicate_resource_checker.ec2_gateway.describe_vpcs = MagicMock(
            return_value=describe_vpcs_response
        )
        # act
        duplicate_resources = self.duplicate_resource_checker.check_pce(TEST_PCE_ID)
        # assert
        self.assertListEqual(
            duplicate_resources,
            [
                DuplicatePCEResource(
                    resource_name_plural=ResourceNamePlural.VPC.value,
                    duplicate_resource_ids="vpc_id_1, vpc_id_2, vpc_id_3",
                )
            ],
        )
