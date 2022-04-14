#!/usr/bin/env python3
# Copyright (c) Meta Platforms, Inc. and affiliates.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

# pyre-strict

# patternlint-disable f-string-may-be-missing-leading-f
from enum import Enum


class ValidationStepNames(Enum):
    """
    Enumerates the names of validation steps, each step corresponding to a
    method of pce.validator.ValidationSuite called validate_{code_name}
    """

    VPC_CIDR = ("VPC CIDR", "vpc_cidr")
    VPC_PEERING = ("VPC peering", "vpc_peering")
    FIREWALL = ("Firewall", "firewall")
    ROUTE_TABLE = ("Route table", "route_table")
    SUBNETS = ("Subnets", "subnets")
    CLUSTER_DEFINITION = ("Cluster definition", "cluster_definition")
    IAM_ROLES = ("IAM roles", "iam_roles")
    LOG_GROUP = ("Log group", "log_group")

    def __init__(self, formatted_name: str, code_name: str) -> None:
        """
        set the Enum member values under better attribute names for
        easier access later eg ValidationStepNames.VPC_CIDR.code_name
        """
        self.formatted_name = formatted_name
        self.code_name = code_name
