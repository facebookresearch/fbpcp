#!/usr/bin/env python3
# Copyright (c) Facebook, Inc. and its affiliates.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

import unittest
from unittest import IsolatedAsyncioTestCase
from unittest.mock import patch

from fbpcs.decorator.metrics import request_counter


METRICS_NAME = "test_metrics"


class TestMetrics:
    def __init__(self, metrics):
        self.metrics = metrics

    @request_counter(METRICS_NAME)
    def test_sync(self):
        pass

    @request_counter(METRICS_NAME)
    async def test_async(self):
        pass


class TestMetricsDecoratorSync(unittest.TestCase):
    @patch("fbpcs.metrics.emitter.MetricsEmitter")
    def test_request_count_sync(self, MockMetricsEmitter):
        metrics = MockMetricsEmitter()
        test_metrics = TestMetrics(metrics)
        test_metrics.test_sync()
        metrics.count.assert_called_with(METRICS_NAME, 1)


class TestMetricsDecoratorAsync(IsolatedAsyncioTestCase):
    @patch("fbpcs.metrics.emitter.MetricsEmitter")
    async def test_request_count_async(self, MockMetricsEmitter):
        metrics = MockMetricsEmitter()
        test_metrics = TestMetrics(metrics)
        await test_metrics.test_async()
        metrics.count.assert_called_with(METRICS_NAME, 1)
