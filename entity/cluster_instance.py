#!/usr/bin/env python3
# Copyright (c) Facebook, Inc. and its affiliates.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

# pyre-strict

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict

from dataclasses_json import dataclass_json


class ClusterStatus(Enum):
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"
    UNKNOWN = "UNKNOWN"


@dataclass_json
@dataclass
class Cluster:
    cluster_arn: str
    cluster_name: str
    status: ClusterStatus = ClusterStatus.UNKNOWN
    tags: Dict[str, str] = field(default_factory=lambda: {})
