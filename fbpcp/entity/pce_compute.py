#!/usr/bin/env python3
# Copyright (c) Meta Platforms, Inc. and affiliates.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

# pyre-strict
from dataclasses import dataclass
from typing import Optional

from fbpcp.entity.cluster_instance import Cluster
from fbpcp.entity.container_definition import ContainerDefinition


@dataclass
class PCECompute:
    region: str
    cluster: Optional[Cluster]
    container_definition: Optional[ContainerDefinition]
