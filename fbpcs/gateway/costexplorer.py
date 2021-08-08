#!/usr/bin/env python3
# Copyright (c) Facebook, Inc. and its affiliates.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

# pyre-strict

from enum import Enum
from typing import Optional, Dict, Any

import boto3
from fbpcs.decorator.error_handler import error_handler
from fbpcs.entity.cloud_cost import CloudCost


class ServiceName(Enum):
    MACIE = "Amazon Macie"
    # TODO will add more service name


class CostExplorerGateway:
    def __init__(
        self,
        region: str,
        access_key_id: Optional[str] = None,
        access_key_data: Optional[str] = None,
        config: Optional[Dict[str, Any]] = None,
    ) -> None:
        self.region = region
        config = config or {}
        if access_key_id:
            config["aws_access_key_id"] = access_key_id

        if access_key_data:
            config["aws_secret_access_key"] = access_key_data

        # pyre-ignore
        self.client = boto3.client("ce", region_name=self.region, **config)

    @error_handler
    def get_cost(self, start: str, end: str) -> CloudCost:
        """
        Get cost between start and end from CostExplorer API using get_cost_and_usage()
        get_cost_and_usage() referece: https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/ce.html#CostExplorer.Client.get_cost_and_usage
        :param start: start date for cost, required format "yyyy-mm-dd" (e.g "2020-12-01")
        :param end: end date for cycle, required format "yyyy-mm-dd" (e.g "2020-12-01")
        :return: CloudCost object that has the total cost and a list of CloudCostItem objects with granular cost information
        """
        raise NotImplementedError
