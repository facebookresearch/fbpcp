#!/usr/bin/env python3
# Copyright (c) Meta Platforms, Inc. and affiliates.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

# pyre-strict


from dataclasses import dataclass
from enum import Enum

from dataclasses_json import DataClassJsonMixin
from onedocker.entity.opawdl_state import OPAWDLState


class Status(Enum):
    CREATED = "CREATED"
    STARTED = "STARTED"
    FAILED = "FAILED"
    COMPLETED = "COMPLETED"


@dataclass
class OPAWDLStateInstance(DataClassJsonMixin):
    opawdl_state: OPAWDLState
    status: Status = Status.CREATED

    def __str__(self) -> str:
        return self.to_json()
