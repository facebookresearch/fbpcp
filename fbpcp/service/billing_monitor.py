#!/usr/bin/env python3
# Copyright (c) Facebook, Inc. and its affiliates.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

# pyre-strict


import abc

from fbpcp.entity.cloud_cost import CloudCost


class BillingMonitorService(abc.ABC):
    @abc.abstractmethod
    def emit_costs_metrics(self, cloud_cost: CloudCost) -> None:
        pass
