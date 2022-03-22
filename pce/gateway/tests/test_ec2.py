#!/usr/bin/env python3
# Copyright (c) Meta Platforms, Inc. and affiliates.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

# pyre-strict

from unittest import TestCase
from unittest.mock import MagicMock
from unittest.mock import patch

from fbpcp.entity.vpc_peering import VpcPeering, VpcPeeringRole, VpcPeeringState
from pce.gateway.ec2 import PCEEC2Gateway


class TestPCEEC2Gateway(TestCase):
    REGION = "us-west-2"
    TEST_AWS_ACCOUNT_ID = "123456789012"
    TEST_ACCEPTER_VPC_ID = "vpc-12345"
    TEST_REQUESTER_VPC_ID = "vpc-56789"
    TEST_VPC_PEERING_ID = "pcx-77889900"

    def setUp(self) -> None:
        self.aws_ec2 = MagicMock()
        with patch("boto3.client") as mock_client:
            mock_client.return_value = self.aws_ec2
            self.ec2 = PCEEC2Gateway(self.REGION)

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
            "VpcPeeringConnections": [
                {
                    "AccepterVpcInfo": {
                        "CidrBlock": "10.0.0.0/16",
                        "CidrBlockSet": [{"CidrBlock": "10.0.0.0/16"}],
                        "OwnerId": self.TEST_AWS_ACCOUNT_ID,
                        "VpcId": self.TEST_ACCEPTER_VPC_ID,
                        "Region": self.REGION,
                    },
                    "RequesterVpcInfo": {
                        "CidrBlock": "10.1.0.0/16",
                        "CidrBlockSet": [{"CidrBlock": "10.1.0.0/16"}],
                        "OwnerId": self.TEST_AWS_ACCOUNT_ID,
                        "VpcId": self.TEST_REQUESTER_VPC_ID,
                        "Region": self.REGION,
                    },
                    "Status": {"Code": "active", "Message": "Active"},
                    "VpcPeeringConnectionId": self.TEST_VPC_PEERING_ID,
                }
            ],
        }
        self.aws_ec2.describe_vpc_peering_connections = MagicMock(
            return_value=client_return_response
        )

        expected_vpc_peering = VpcPeering(
            id=self.TEST_VPC_PEERING_ID,
            status=VpcPeeringState.ACTIVE,
            role=VpcPeeringRole.ACCEPTER,
            requester_vpc_id=self.TEST_REQUESTER_VPC_ID,
            accepter_vpc_id=self.TEST_ACCEPTER_VPC_ID,
        )

        # Act
        vpc_peering_connection = (
            self.ec2.describe_vpc_peering_connections_with_accepter_vpc_id(
                vpc_id=self.TEST_ACCEPTER_VPC_ID
            )
        )

        # Assert
        self.assertEqual(vpc_peering_connection, expected_vpc_peering)
        self.aws_ec2.describe_vpc_peering_connections.assert_called

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
        self.aws_ec2.describe_vpc_peering_connections.assert_called
