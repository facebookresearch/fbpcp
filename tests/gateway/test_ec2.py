#!/usr/bin/env python3

import unittest
from unittest.mock import MagicMock, patch

from entity.vpc_instance import Vpc, VpcState
from gateway.ec2 import EC2Gateway

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
