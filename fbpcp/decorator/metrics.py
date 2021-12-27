#!/usr/bin/env python3
# Copyright (c) Meta Platforms, Inc. and affiliates.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

"""Metrics Decorators

The decorators in this file are designed to deocrate classes that implement MetricsGetter.
"""

import asyncio
import functools
import time
from typing import Callable

from fbpcp.metrics.getter import MetricsGetter


def request_counter(metrics_name: str) -> Callable:
    def wrap(f: Callable):
        @functools.wraps(f)
        def wrapper_sync(self: MetricsGetter, *args, **kwargs):
            if self.has_metrics():
                self.get_metrics().count(metrics_name, 1)
            return f(self, *args, **kwargs)

        @functools.wraps(f)
        async def wrapper_async(self: MetricsGetter, *args, **kwargs):
            if self.has_metrics():
                self.get_metrics().count(metrics_name, 1)
            return await f(self, *args, **kwargs)

        return wrapper_async if asyncio.iscoroutinefunction(f) else wrapper_sync

    return wrap


def error_counter(metrics_name: str) -> Callable:
    def wrap(f: Callable):
        @functools.wraps(f)
        def wrapper_sync(self: MetricsGetter, *args, **kwargs):
            try:
                return f(self, *args, **kwargs)
            except Exception as err:
                if self.has_metrics():
                    self.get_metrics().count(metrics_name, 1)
                raise err

        @functools.wraps(f)
        async def wrapper_async(self: MetricsGetter, *args, **kwargs):
            try:
                return await f(self, *args, **kwargs)
            except Exception as err:
                if self.has_metrics():
                    self.get_metrics().count(metrics_name, 1)
                raise err

        return wrapper_async if asyncio.iscoroutinefunction(f) else wrapper_sync

    return wrap


def duration_time(metrics_name: str) -> Callable:
    def wrap(f: Callable):
        @functools.wraps(f)
        def wrapper_sync(self: MetricsGetter, *args, **kwargs):
            start = time.perf_counter_ns()
            res = f(self, *args, **kwargs)
            end = time.perf_counter_ns()

            if self.has_metrics():
                self.get_metrics().gauge(metrics_name, int((end - start) / 1e6))

            return res

        @functools.wraps(f)
        async def wrapper_async(self: MetricsGetter, *args, **kwargs):
            start = time.perf_counter_ns()
            res = await f(self, *args, **kwargs)
            end = time.perf_counter_ns()

            if self.has_metrics():
                self.get_metrics().gauge(metrics_name, int((end - start) / 1e6))

            return res

        return wrapper_async if asyncio.iscoroutinefunction(f) else wrapper_sync

    return wrap
