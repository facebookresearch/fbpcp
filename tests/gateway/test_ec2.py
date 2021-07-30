#!/usr/bin/env python3
# Copyright (c) Facebook, Inc. and its affiliates.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

import unittest
from unittest.mock import MagicMock, patch

from fbpcs.entity.subnet import Subnet
from fbpcs.entity.vpc_instance import Vpc, VpcState
from fbpcs.gateway.ec2 import EC2Gateway

TEST_VPC_ID = "test-vpc-id"
TEST_ACCESS_KEY_ID = "test-access-key-id"
TEST_ACCESS_KEY_DATA = "test-access-key-data"
TEST_VPC_TAG_KEY = "test-vpc-tag-key"
TEST_VPC_TAG_VALUE = "test-vpc-tag-value"
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
                VpcState.UNKNOWN,
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
