#!/usr/bin/env python3
# Copyright (c) Facebook, Inc. and its affiliates.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

import unittest
from unittest.mock import MagicMock, patch

from fbpcp.entity.route_table import (
    RouteTable,
    Route,
    RouteTarget,
    RouteTargetType,
    RouteState,
)
from fbpcp.entity.subnet import Subnet
from fbpcp.entity.vpc_instance import Vpc, VpcState
from fbpcp.gateway.ec2 import EC2Gateway

TEST_VPC_ID = "test-vpc-id"
TEST_ACCESS_KEY_ID = "test-access-key-id"
TEST_ACCESS_KEY_DATA = "test-access-key-data"
TEST_VPC_TAG_KEY = "test-vpc-tag-key"
TEST_VPC_TAG_VALUE = "test-vpc-tag-value"
TEST_CIDR_BLOCK = "10.1.0.0/16"
REGION = "us-west-2"


class TestEC2Gateway(unittest.TestCase):
    @patch("boto3.client")
    def setUp(self, BotoClient):
        self.gw = EC2Gateway(REGION, TEST_ACCESS_KEY_ID, TEST_ACCESS_KEY_DATA)
        self.gw.client = BotoClient()

    def test_describe_vpcs(self):
        client_return_response = {
            "Vpcs": [
                {
                    "State": "UNKNOWN",
                    "CidrBlock": TEST_CIDR_BLOCK,
                    "VpcId": TEST_VPC_ID,
                    "Tags": [
                        {
                            "Key": TEST_VPC_TAG_KEY,
                            "Value": TEST_VPC_TAG_VALUE,
                        },
                    ],
                }
            ]
        }
        tags = {TEST_VPC_TAG_KEY: TEST_VPC_TAG_VALUE}
        self.gw.client.describe_vpcs = MagicMock(return_value=client_return_response)
        vpcs = self.gw.describe_vpcs([TEST_VPC_ID])
        expected_vpcs = [
            Vpc(
                TEST_VPC_ID,
                TEST_CIDR_BLOCK,
                VpcState.UNKNOWN,
                [],
                tags,
            ),
        ]
        self.assertEqual(vpcs, expected_vpcs)
        self.gw.client.describe_vpcs.assert_called()

    def test_list_vpcs(self):
        client_return_response = {
            "Vpcs": [
                {"VpcId": TEST_VPC_ID},
            ]
        }
        self.gw.client.describe_vpcs = MagicMock(return_value=client_return_response)
        vpcs = self.gw.list_vpcs()
        expected_vpcs = [TEST_VPC_ID]
        self.assertEqual(vpcs, expected_vpcs)
        self.gw.client.describe_vpcs.assert_called()

    def test_describe_subnets(self):
        test_subnet_id = "subnet-a0b1c3d4e5"
        test_az = "us-west-2a"
        test_tag_key = "Name"
        test_tag_value = "test_value"
        client_return_response = {
            "Subnets": [
                {
                    "AvailabilityZone": test_az,
                    "SubnetId": test_subnet_id,
                    "Tags": [{"Key": test_tag_key, "Value": test_tag_value}],
                }
            ]
        }
        self.gw.client.describe_subnets = MagicMock(return_value=client_return_response)
        subnets = self.gw.describe_subnets()
        expected_subnets = [
            Subnet(test_subnet_id, test_az, {test_tag_key: test_tag_value}),
        ]
        self.assertEqual(subnets, expected_subnets)
        self.gw.client.describe_subnets.assert_called()

    def test_describe_route_tables(self):
        test_route_table_id = "rtb-a0b1c3d4e5"
        vpc_peering_id = "pcx-a0b1c3d4e5"
        gateway_id = "igw-a0b1c3d4e5"

        client_return_response = {
            "RouteTables": [
                {
                    "RouteTableId": test_route_table_id,
                    "VpcId": TEST_VPC_ID,
                    "Routes": [
                        {
                            "DestinationCidrBlock": TEST_CIDR_BLOCK,
                            "State": "blackhole",
                            "VpcPeeringConnectionId": vpc_peering_id,
                        },
                        {
                            "DestinationCidrBlock": TEST_CIDR_BLOCK,
                            "GatewayId": gateway_id,
                            "State": "active",
                        },
                    ],
                }
            ]
        }
        self.gw.client.describe_route_tables = MagicMock(
            return_value=client_return_response
        )
        route_tables = self.gw.describe_route_tables()
        vpc_peering_route = Route(
            TEST_CIDR_BLOCK,
            RouteTarget(vpc_peering_id, RouteTargetType.VPC_PEERING),
            RouteState.UNKNOWN,
        )
        internet_route = Route(
            TEST_CIDR_BLOCK,
            RouteTarget(gateway_id, RouteTargetType.INTERNET),
            RouteState.ACTIVE,
        )
        expected_route_tables = [
            RouteTable(
                test_route_table_id, [vpc_peering_route, internet_route], TEST_VPC_ID
            ),
        ]
        self.assertEqual(route_tables, expected_route_tables)
        self.gw.client.describe_route_tables.assert_called()
