#!/usr/bin/env python3
# Copyright (c) Meta Platforms, Inc. and affiliates.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

# pyre-strict

import abc

from fbpcp.metrics.emitter import MetricsEmitter


class MetricsGetter(abc.ABC):
    @abc.abstractmethod
    def has_metrics(self) -> bool:
        pass

    @abc.abstractmethod
    def get_metrics(self) -> MetricsEmitter:
        pass
