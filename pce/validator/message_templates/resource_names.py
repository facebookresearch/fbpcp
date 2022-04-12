#!/usr/bin/env python3
# Copyright (c) Meta Platforms, Inc. and affiliates.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

# pyre-strict

# patternlint-disable f-string-may-be-missing-leading-f
from enum import Enum


class ResourceNamePlural(Enum):
    VPC = "VPCs"
    ROUTE_TABLE = "Route Tables"
    VPC_PEERING = "VPC Peerings"
    CLUSTER = "ECS Clusters"
    CONTAINER_DEFINITION = "Container Definitions"
