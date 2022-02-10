#!/usr/bin/env python3
# Copyright (c) Meta Platforms, Inc. and affiliates.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

# pyre-strict

# patternlint-disable f-string-may-be-missing-leading-f

from typing import TypeVar


FIREWALL_RULE_INITIAL_PORT = 5000
FIREWALL_RULE_FINAL_PORT = 15500


AvailabilityZone = TypeVar("AvailabilityZone", str, bytes)


CONTAINER_CPU = 4096
CONTAINER_MEMORY = 30720
CONTAINER_IMAGE = "539290649537.dkr.ecr.us-west-2.amazonaws.com/one-docker-prod:latest"
TASK_POLICY = {
    "Version": "2012-10-17",
    "Statement": [
        {"Effect": "Allow", "Action": ["s3:*", "s3-object-lambda:*"], "Resource": "*"}
    ],
}

IGW_ROUTE_TARGET_PREFIX: str = "igw-"
IGW_ROUTE_DESTINATION_CIDR_BLOCK: str = "0.0.0.0/0"

DEFAULT_VPC_CIDR = "10.0.0.0/16"
DEFAULT_PARTNER_VPC_CIDR = "10.1.0.0/16"
