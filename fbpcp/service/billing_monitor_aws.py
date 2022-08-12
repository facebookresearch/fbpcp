#!/usr/bin/env python3
# Copyright (c) Facebook, Inc. and its affiliates.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

# pyre-strict
from datetime import date

from fbpcp.entity.cloud_cost import CloudCost, CloudCostItem
from fbpcp.metrics.emitter import MetricsEmitter
from fbpcp.service.billing_monitor import BillingMonitorService

METRICS_BILLING_GAUGE = "onedocker.container.count"


class AWSBillingMonitorService(BillingMonitorService):
    def __init__(self, metrics: MetricsEmitter) -> None:
        self.metrics = metrics

    def emit_costs_metrics(
        self,
        cost_date: date,
        cloud_cost: CloudCost,
    ) -> None:
        pass

    def _emit_metric(self, clould_cost_item: CloudCostItem) -> None:
        pass
