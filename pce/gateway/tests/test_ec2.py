#!/usr/bin/env python3
# Copyright (c) Meta Platforms, Inc. and affiliates.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

# pyre-strict

from unittest import TestCase
from unittest.mock import MagicMock
from unittest.mock import patch

from pce.gateway.ec2 import PCEEC2Gateway

REGION = "us-west-2"


class TestPCEEC2Gateway(TestCase):
    def setUp(self) -> None:
        self.aws_ec2 = MagicMock()
        with patch("boto3.client") as mock_client:
            mock_client.return_value = self.aws_ec2
            self.ec2 = PCEEC2Gateway(REGION)

    def test_describe_availability_zones(self) -> None:
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

        availability_zones = self.ec2.describe_availability_zones()
        self.assertEqual(expected_availability_zones, availability_zones)

        self.aws_ec2.describe_availability_zones.assert_called()
