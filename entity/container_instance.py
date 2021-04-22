#!/usr/bin/env python3
# Copyright (c) Facebook, Inc. and its affiliates.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

# pyre-strict

from dataclasses import dataclass
from enum import Enum
from typing import Optional

from dataclasses_json import dataclass_json


class ContainerInstanceStatus(Enum):
    UNKNOWN = "UNKNOWN"
    STARTED = "STARTED"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


@dataclass_json
@dataclass
class ContainerInstance:
    instance_id: str
    ip_address: Optional[str] = None
    status: ContainerInstanceStatus = ContainerInstanceStatus.UNKNOWN
