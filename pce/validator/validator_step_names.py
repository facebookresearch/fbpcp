#!/usr/bin/env python3
# Copyright (c) Meta Platforms, Inc. and affiliates.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

# pyre-strict

# patternlint-disable f-string-may-be-missing-leading-f
from enum import Enum


class ValidationStepNames(Enum):
    CIDR = "CIDR"
    VPC_PEERING = "VPC peering"
    FIREWALL = "Firewall"
    ROUTE_TABLE = "Route table"
    SUBNETS = "Subnets"
    CLUSTER_DEFINITION = "Cluster definition"
    ROLE = "IAM roles"
