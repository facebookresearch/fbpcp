#!/usr/bin/env python3
# Copyright (c) Facebook, Inc. and its affiliates.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

import asyncio
import functools
from typing import Callable


def request_counter(metrics_name: str) -> Callable:
    def wrap(f: Callable):
        @functools.wraps(f)
        def wrapper_sync(self, *args, **kwargs):
            if self.metrics:
                self.metrics.count(metrics_name, 1)
            return f(self, *args, **kwargs)

        @functools.wraps(f)
        async def wrapper_async(self, *args, **kwargs):
            if self.metrics:
                self.metrics.count(metrics_name, 1)
            return await f(self, *args, **kwargs)

        if asyncio.iscoroutinefunction(f):
            return wrapper_async
        else:
            return wrapper_sync

    return wrap


# def error_counter(metrics_name: str) -> Callable:
#     pass


# def duration_timer(metrics_name: str) -> Callable:
#     pass
