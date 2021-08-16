#!/usr/bin/env python3
# Copyright (c) Facebook, Inc. and its affiliates.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

# pyre-strict

from typing import Optional, Dict, Any

import boto3
from fbpcp.decorator.error_handler import error_handler
from fbpcp.entity.cloud_cost import CloudCost
from fbpcp.gateway.aws import AWSGateway
from fbpcp.mapper.aws import map_cecost_to_cloud_cost

COST_GRANULARITY = "DAILY"


class CostExplorerGateway(AWSGateway):
    def __init__(
        self,
        region: str,
        access_key_id: Optional[str] = None,
        access_key_data: Optional[str] = None,
        config: Optional[Dict[str, Any]] = None,
    ) -> None:
        super().__init__(region, access_key_id, access_key_data, config)
        # pyre-ignore
        self.client = boto3.client("ce", region_name=self.region, **self.config)

    @error_handler
    def get_cost(self, start_date: str, end_date: str) -> CloudCost:
        """
        Get cost between start_date and end_date from CostExplorer API using get_cost_and_usage()
        get_cost_and_usage() referece: https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/ce.html#CostExplorer.Client.get_cost_and_usage
        :param start_date: start date for cost, required format "yyyy-mm-dd" (e.g "2020-12-01")
        :param end_date: end date for cycle, required format "yyyy-mm-dd" (e.g "2020-12-01")
        :return: CloudCost object that has the total cost and a list of CloudCostItem objects group by region and service. Unit of cost_amount is USD
        """

        page_token = None
        results_by_time = []

        while True:
            paginate_kwargs = {"NextPageToken": page_token} if page_token else {}
            client_response = self.client.get_cost_and_usage(
                TimePeriod={"Start": start_date, "End": end_date},
                Granularity=COST_GRANULARITY,
                Metrics=["UnblendedCost"],
                GroupBy=[
                    {"Type": "DIMENSION", "Key": "REGION"},
                    {"Type": "DIMENSION", "Key": "SERVICE"},
                ],
                **paginate_kwargs,
            )
            results_by_time.extend(client_response.get("ResultsByTime"))
            page_token = client_response.get("NextPageToken")
            if not page_token:
                break

        return map_cecost_to_cloud_cost(results_by_time)
