#!/usr/bin/env python3
# Copyright (c) Facebook, Inc. and its affiliates.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

# pyre-strict

import abc


class MetricsEmitter(abc.ABC):
    @abc.abstractmethod
    def count(
        self,
        name: str,
        value: int,
    ) -> None:
        pass

    @abc.abstractmethod
    def gauge(
        self,
        name: str,
        value: int,
    ) -> None:
        pass
