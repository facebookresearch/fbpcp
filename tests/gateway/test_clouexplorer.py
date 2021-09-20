#!/usr/bin/env python3
# Copyright (c) Facebook, Inc. and its affiliates.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

import unittest
from decimal import Decimal
from unittest.mock import MagicMock, patch

from fbpcp.cloud.region import RegionName
from fbpcp.cloud.service import ServiceName
from fbpcp.entity.cloud_cost import CloudCost, CloudCostItem
from fbpcp.gateway.costexplorer import CostExplorerGateway


class TestCostExplorerGateway(unittest.TestCase):
    TEST_ACCESS_KEY_ID = "test-access-key-id"
    TEST_ACCESS_KEY_DATA = "test-access-key-data"

    @patch("boto3.client")
    def setUp(self, BotoClient):
        self.gw = CostExplorerGateway(
            self.TEST_ACCESS_KEY_ID, self.TEST_ACCESS_KEY_DATA
        )
        self.gw.client = BotoClient()

    def test_get_cost(self):
        test_region = RegionName.AWS_US_EAST_1
        test_service_macie = ServiceName.AWS_MACIE
        test_service_s3 = ServiceName.AWS_S3
        test_amount_macie_1 = "0.0049312"
        test_amount_macie_2 = "0.051"
        test_amount_s3_1 = "0.0018546732"
        test_amount_s3_2 = "0.001235123"
        test_start_date = "2021-08-01"
        test_between_date = "2021-08-02"
        test_end_date = "2021-08-03"

        expected_test_amount_macie = Decimal(test_amount_macie_1) + Decimal(
            test_amount_macie_2
        )
        expected_test_amount_s3 = Decimal(test_amount_s3_1) + Decimal(test_amount_s3_2)
        expected_total_test_amount = (
            expected_test_amount_macie + expected_test_amount_s3
        )
        client_return_response = {
            "GroupDefinitions": [
                {"Type": "DIMENSION", "Key": "SERVICE"},
                {"Type": "DIMENSION", "Key": "REGION"},
            ],
            "ResultsByTime": [
                {
                    "TimePeriod": {"Start": test_start_date, "End": test_between_date},
                    "Total": {},
                    "Groups": [
                        {
                            "Keys": [test_region, test_service_macie],
                            "Metrics": {
                                "UnblendedCost": {
                                    "Amount": test_amount_macie_1,
                                    "Unit": "USD",
                                }
                            },
                        },
                        {
                            "Keys": [test_region, test_service_s3],
                            "Metrics": {
                                "UnblendedCost": {
                                    "Amount": test_amount_s3_1,
                                    "Unit": "USD",
                                }
                            },
                        },
                    ],
                    "Estimated": True,
                },
                {
                    "TimePeriod": {"Start": test_between_date, "End": test_end_date},
                    "Total": {},
                    "Groups": [
                        {
                            "Keys": [test_region, test_service_macie],
                            "Metrics": {
                                "UnblendedCost": {
                                    "Amount": test_amount_macie_2,
                                    "Unit": "USD",
                                }
                            },
                        },
                        {
                            "Keys": [test_region, test_service_s3],
                            "Metrics": {
                                "UnblendedCost": {
                                    "Amount": test_amount_s3_2,
                                    "Unit": "USD",
                                }
                            },
                        },
                    ],
                    "Estimated": True,
                },
            ],
            "DimensionValueAttributes": [],
        }
        self.gw.client.get_cost_and_usage = MagicMock(
            return_value=client_return_response
        )

        expected_cost = CloudCost(
            total_cost_amount=expected_total_test_amount,
            details=[
                CloudCostItem(
                    region=test_region,
                    service=test_service_macie,
                    cost_amount=expected_test_amount_macie,
                ),
                CloudCostItem(
                    region=test_region,
                    service=test_service_s3,
                    cost_amount=expected_test_amount_s3,
                ),
            ],
        )
        cloud_cost = self.gw.get_cost(test_start_date, test_end_date)
        self.assertEqual(expected_cost, cloud_cost)
        self.gw.client.get_cost_and_usage.assert_called()
