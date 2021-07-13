#!/usr/bin/env python3
# Copyright (c) Facebook, Inc. and its affiliates.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

# pyre-strict

from dataclasses import dataclass
from enum import Enum
from typing import List

from dataclasses_json import DataClassJsonMixin
from fbpcs.entity.container_instance import ContainerInstance
from onedocker.onedocker_lib.entity.owdl_state import OWDLState


class Status(Enum):
    CREATED = "CREATED"
    STARTED = "STARTED"
    FAILED = "FAILED"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"


@dataclass
class OWDLStateInstance(DataClassJsonMixin):
    owdl_state: OWDLState
    containers: List[ContainerInstance]
    status: Status = Status.CREATED
    retry_num: int = 0

    def __str__(self) -> str:
        return self.to_json()
