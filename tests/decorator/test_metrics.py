#!/usr/bin/env python3
# Copyright (c) Facebook, Inc. and its affiliates.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

import unittest
from unittest import IsolatedAsyncioTestCase
from unittest.mock import patch, ANY

from fbpcs.decorator.metrics import request_counter, duration_time, error_counter


METRICS_NAME = "test_metrics"


class TestMetrics:
    def __init__(self, metrics):
        self.metrics = metrics

    @duration_time(METRICS_NAME)
    @request_counter(METRICS_NAME)
    def test_sync(self):
        pass

    @duration_time(METRICS_NAME)
    @request_counter(METRICS_NAME)
    async def test_async(self):
        pass

    @error_counter(METRICS_NAME)
    def test_error_sync(self):
        raise ValueError("test")

    @error_counter(METRICS_NAME)
    async def test_error_async(self):
        raise ValueError("test")


class TestMetricsDecoratorSync(unittest.TestCase):
    @patch("fbpcs.metrics.emitter.MetricsEmitter")
    def test_sync(self, MockMetricsEmitter):
        metrics = MockMetricsEmitter()
        test_metrics = TestMetrics(metrics)
        test_metrics.test_sync()
        metrics.count.assert_called_with(METRICS_NAME, 1)
        metrics.gauge.assert_called_with(METRICS_NAME, ANY)
        with self.assertRaises(ValueError):
            test_metrics.test_error_sync()
        metrics.count.assert_called_with(METRICS_NAME, 1)


class TestMetricsDecoratorAsync(IsolatedAsyncioTestCase):
    @patch("fbpcs.metrics.emitter.MetricsEmitter")
    async def test_async(self, MockMetricsEmitter):
        metrics = MockMetricsEmitter()
        test_metrics = TestMetrics(metrics)
        await test_metrics.test_async()
        metrics.count.assert_called_with(METRICS_NAME, 1)
        metrics.gauge.assert_called_with(METRICS_NAME, ANY)
        with self.assertRaises(ValueError):
            await test_metrics.test_error_async()
        metrics.count.assert_called_with(METRICS_NAME, 1)
