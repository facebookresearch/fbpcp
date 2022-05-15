#!/usr/bin/env python3
# Copyright (c) Meta Platforms, Inc. and affiliates.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

# pyre-strict

from datetime import date
from typing import Any, Dict, Optional

from fbpcp.entity.cloud_cost import CloudCost
from fbpcp.gateway.costexplorer import CostExplorerGateway
from fbpcp.service.billing import BillingService


class AWSBillingService(BillingService):
    def __init__(
        self,
        access_key_id: Optional[str] = None,
        access_key_data: Optional[str] = None,
        config: Optional[Dict[str, Any]] = None,
    ) -> None:
        self.ce_gateway = CostExplorerGateway(access_key_id, access_key_data, config)

    def get_cost(
        self, start_date: date, end_date: date, region: Optional[str] = None
    ) -> CloudCost:
        """Get cost between start_date and end_date
        Keyword arguments:
        start_date: start date for cost
        end_date: end date for cost
        region: region name as optional filter for cost.
        """
        date_format = "%Y-%m-%d"
        return self.ce_gateway.get_cost(
            start_date.strftime(date_format),
            end_date.strftime(date_format),
            region,
        )
