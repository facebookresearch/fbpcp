#!/usr/bin/env python3
# Copyright (c) Facebook, Inc. and its affiliates.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

# pyre-strict
from enum import Enum


class RegionName(Enum):
    AWS_US_EAST_1 = "us-east-1"
    AWS_US_EAST_2 = "us-east-2"
    AWS_US_WEST_1 = "us-west-1"
    AWS_US_WEST_2 = "us-west-2"
    AWS_AP_NORTHEAST_1 = "ap-northeast-1"
    AWS_AP_NORTHEAST_2 = "ap-northeast-2"
    AWS_AP_NORTHEAST_3 = "ap-northeast-3"
    AWS_AP_SOUTH_1 = "ap-south-1"
    AWS_AP_SOUTHEAST_1 = "ap-southeast-1"
    AWS_AP_SOUTHEAST_2 = "ap-southeast-2"
    AWS_CA_CENTRAL_1 = "ca-central-1"
    AWS_EU_CENTRAL_1 = "eu-central-1"
    AWS_EU_NORTH_1 = "eu-north-1"
    AWS_EU_WEST_1 = "eu-west-1"
    AWS_EU_WEST_2 = "eu-west-2"
    AWS_EU_WEST_3 = "eu-west-3"
    AWS_SA_EAST_1 = "sa-east-1"
    NO_REGION = "NoRegion"
