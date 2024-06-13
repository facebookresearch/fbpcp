#!/usr/bin/env python3
# Copyright (c) Meta Platforms, Inc. and affiliates.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

# pyre-strict
from dataclasses import dataclass


@dataclass
class InsightsMessage:
    time: float
    cluster_name: str
    instance_id: str
    status: str
