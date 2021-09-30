#!/usr/bin/env python3
# Copyright (c) Facebook, Inc. and its affiliates.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

# pyre-strict
from enum import Enum

# This class will be deprecated because we want to get the cloud region list dynamically instead of maintaining it.
# Please contact Ji Liu if there is any reason that you need this
class RegionName(Enum):
    AWS_US_EAST_1 = "us-east-1"
    AWS_US_EAST_2 = "us-east-2"
    AWS_US_WEST_1 = "us-west-1"
    AWS_US_WEST_2 = "us-west-2"
