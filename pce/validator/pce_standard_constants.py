#!/usr/bin/env python3
# Copyright (c) Facebook, Inc. and its affiliates.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

# pyre-strict

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
        {
            "Action": "sts:AssumeRole",
            "Principal": {"Service": "ecs-tasks.amazonaws.com"},
            "Effect": "Allow",
            "Sid": "",
        }
    ],
}
TASK_EXECUTION_POLICY = {
    "Version": "2012-10-17",
    "Statement": [
        {
            "Action": "sts:AssumeRole",
            "Principal": {"Service": "ecs-tasks.amazonaws.com"},
            "Effect": "Allow",
            "Sid": "",
        }
    ],
}
