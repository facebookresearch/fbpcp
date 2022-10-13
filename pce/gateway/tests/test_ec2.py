#!/usr/bin/env python3
# Copyright (c) Meta Platforms, Inc. and affiliates.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from unittest import TestCase
from unittest.mock import MagicMock, patch

from botocore.exceptions import ClientError

from fbpcp.entity.vpc_peering import VpcPeering, VpcPeeringRole, VpcPeeringState
from fbpcp.error.pcp import PcpError
from pce.gateway.ec2 import EC2Gateway

TEST_REGION = "us-west-2"
TEST_AWS_ACCOUNT_ID = "123456789012"
TEST_ACCEPTER_VPC_ID = "vpc-12345"
TEST_REQUESTER_VPC_ID = "vpc-56789"
TEST_VPC_PEERING_ID = "pcx-77889900"
TEST_ACCEPTER_CIDR_BLOCK = "10.0.0.0/16"
TEST_REQUESTER_CIDR_BLOCK = "10.1.0.0/16"
TEST_ROUTE_TABLE_ID = "rtb-123456"
TEST_VPC_PEERING_CONNECTION = {
    "AccepterVpcInfo": {
        "CidrBlock": TEST_ACCEPTER_CIDR_BLOCK,
        "CidrBlockSet": [{"CidrBlock": "10.0.0.0/16"}],
        "OwnerId": TEST_AWS_ACCOUNT_ID,
        "VpcId": TEST_ACCEPTER_VPC_ID,
        "TEST_REGION": TEST_REGION,
    },
    "RequesterVpcInfo": {
        "CidrBlock": TEST_REQUESTER_CIDR_BLOCK,
        "CidrBlockSet": [{"CidrBlock": "10.1.0.0/16"}],
        "OwnerId": TEST_AWS_ACCOUNT_ID,
        "VpcId": TEST_REQUESTER_VPC_ID,
        "TEST_REGION": TEST_REGION,
    },
    "Status": {"Code": "active", "Message": "Active"},
    "VpcPeeringConnectionId": TEST_VPC_PEERING_ID,
}


class TestEC2Gateway(TestCase):
    def setUp(self) -> None:
        self.aws_ec2 = MagicMock()
        with patch("boto3.client") as mock_client:
            mock_client.return_value = self.aws_ec2
            self.ec2 = EC2Gateway(TEST_REGION)

    def test_describe_availability_zones(self) -> None:
        # Arrange
        client_return_response = {
            "AvailabilityZones": [
                {
                    "State": "available",
                    "ZoneName": "foo_1_zone",
                },
                {
                    "State": "available",
                    "ZoneName": "foo_2_zone",
                },
                {
                    "State": "information",
                    "ZoneName": "foo_3_zone",
                },
                {
                    "State": "available",
                    "ZoneName": "foo_4_zone",
                },
            ]
        }

        self.aws_ec2.describe_availability_zones = MagicMock(
            return_value=client_return_response
        )

        expected_availability_zones = [
            "foo_1_zone",
            "foo_2_zone",
            "foo_3_zone",
            "foo_4_zone",
        ]
        # Act
        availability_zones = self.ec2.describe_availability_zones()

        # Assert
        self.assertEqual(expected_availability_zones, availability_zones)
        self.aws_ec2.describe_availability_zones.assert_called()

    def test_describe_vpc_peering_connections_with_accepter_vpc_id(self) -> None:
        # Arrange
        client_return_response = {
            "VpcPeeringConnections": [TEST_VPC_PEERING_CONNECTION],
        }
        self.aws_ec2.describe_vpc_peering_connections = MagicMock(
            return_value=client_return_response
        )

        expected_vpc_peering = VpcPeering(
            id=TEST_VPC_PEERING_ID,
            status=VpcPeeringState.ACTIVE,
            role=VpcPeeringRole.ACCEPTER,
            requester_vpc_id=TEST_REQUESTER_VPC_ID,
            accepter_vpc_id=TEST_ACCEPTER_VPC_ID,
            requester_vpc_cidr=TEST_REQUESTER_CIDR_BLOCK,
            accepter_vpc_cidr=TEST_ACCEPTER_CIDR_BLOCK,
        )

        # Act
        vpc_peering_connection = (
            self.ec2.describe_vpc_peering_connections_with_accepter_vpc_id(
                vpc_id=TEST_ACCEPTER_VPC_ID
            )[0]
        )

        # Assert
        self.assertEqual(vpc_peering_connection, expected_vpc_peering)
        self.aws_ec2.describe_vpc_peering_connections.assert_called()

    def test_describe_vpc_peering_connections_with_no_accepter_vpc_id(self) -> None:
        # Arrange
        client_return_response = {"VpcPeeringConnections": []}
        self.aws_ec2.describe_vpc_peering_connections = MagicMock(
            return_value=client_return_response
        )

        # Act
        vpc_peering_connection = (
            self.ec2.describe_vpc_peering_connections_with_accepter_vpc_id(vpc_id=None)
        )

        # Assert
        self.assertIsNone(vpc_peering_connection, "vpc peering connection is None")
        self.aws_ec2.describe_vpc_peering_connections.assert_called()

    def test_accept_vpc_peering_connection_success(self) -> None:
        # Arrange
        client_return_response = {"VpcPeeringConnection": TEST_VPC_PEERING_CONNECTION}
        self.aws_ec2.accept_vpc_peering_connection = MagicMock(
            return_value=client_return_response
        )

        expected_vpc_peering = VpcPeering(
            id=TEST_VPC_PEERING_ID,
            status=VpcPeeringState.ACTIVE,
            role=VpcPeeringRole.ACCEPTER,
            requester_vpc_id=TEST_REQUESTER_VPC_ID,
            accepter_vpc_id=TEST_ACCEPTER_VPC_ID,
            requester_vpc_cidr=TEST_REQUESTER_CIDR_BLOCK,
            accepter_vpc_cidr=TEST_ACCEPTER_CIDR_BLOCK,
        )

        # Act
        vpc_peering_connection = self.ec2.accept_vpc_peering_connection(
            vpc_peering_connection_id=TEST_VPC_PEERING_ID, vpc_id=TEST_ACCEPTER_VPC_ID
        )

        # Assert
        self.assertEqual(vpc_peering_connection, expected_vpc_peering)
        self.aws_ec2.accept_vpc_peering_connection.assert_called()

    def test_accept_vpc_peering_connection_fail(self) -> None:
        # Arrange
        self.aws_ec2.accept_vpc_peering_connection = MagicMock(
            side_effect=ClientError(
                {
                    "Error": {"Message": "test_msg", "Code": "test_code"},
                    "ResponseMetadata": {},
                },
                None,
            )
        )
        # patternlint-disable-next-line f-string-may-be-missing-leading-f
        expect_msg = "An error occurred (test_code) when calling the None operation: test_msg\n\n Details: {}\n"

        # Act
        with self.assertRaises(PcpError) as err:
            self.ec2.accept_vpc_peering_connection(
                vpc_peering_connection_id=TEST_VPC_PEERING_ID,
                vpc_id=TEST_ACCEPTER_VPC_ID,
            )

        # Assert
        self.assertEqual(str(err.exception), expect_msg)

    def test_create_route_success(self) -> None:
        # Arrange
        client_return_response = {"Return": True}
        self.aws_ec2.create_route = MagicMock(return_value=client_return_response)

        # Act
        creation_res = self.ec2.create_route(
            route_table_id=TEST_ROUTE_TABLE_ID,
            vpc_peering_connection_id=TEST_VPC_PEERING_ID,
            dest_cidr=TEST_REQUESTER_CIDR_BLOCK,
        )

        # Assert
        self.assertTrue(creation_res)
        self.aws_ec2.create_route.assert_called()

    def test_create_route_fail(self) -> None:
        # Arrange
        self.aws_ec2.create_route = MagicMock(
            side_effect=ClientError(
                {
                    "Error": {"Message": "client error", "Code": "RouteAlreadyExists"},
                    "ResponseMetadata": {},
                },
                None,
            )
        )
        # patternlint-disable-next-line f-string-may-be-missing-leading-f
        expect_msg = "An error occurred (RouteAlreadyExists) when calling the None operation: client error\n\n Details: {}\n"

        # Act
        with self.assertRaises(PcpError) as err:
            self.ec2.create_route(
                route_table_id=TEST_ROUTE_TABLE_ID,
                vpc_peering_connection_id=TEST_VPC_PEERING_ID,
                dest_cidr=TEST_REQUESTER_CIDR_BLOCK,
            )

        # Assert
        self.assertEqual(str(err.exception), expect_msg)
