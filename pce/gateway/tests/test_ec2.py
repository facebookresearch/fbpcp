#!/usr/bin/env python3
# Copyright (c) Facebook, Inc. and its affiliates.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

# pyre-strict

from unittest import TestCase
from unittest.mock import MagicMock

from pce.gateway.ec2 import EC2Gateway


class TestEC2Gateway(TestCase):
    def setUp(self) -> None:
        self.aws_ec2 = MagicMock()
        self.ec2 = EC2Gateway(lambda _: self.aws_ec2)

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
