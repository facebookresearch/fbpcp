#!/usr/bin/env python3
# Copyright (c) Facebook, Inc. and its affiliates.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

# pyre-strict
from enum import Enum


class ServiceName(Enum):
    AWS_MACIE = "Amazon Macie"
    AWS_S3 = "Amazon Simple Storage Service"
    # TODO will add more service name
