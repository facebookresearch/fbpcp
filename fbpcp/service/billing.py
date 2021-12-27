#!/usr/bin/env python3
# Copyright (c) Meta Platforms, Inc. and affiliates.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

# pyre-strict

import abc
from datetime import date
from typing import Optional

from fbpcp.entity.cloud_cost import CloudCost


class BillingService(abc.ABC):
    @abc.abstractmethod
    def get_cost(
        self, start_date: date, end_date: date, region: Optional[str] = None
    ) -> CloudCost:
        pass
