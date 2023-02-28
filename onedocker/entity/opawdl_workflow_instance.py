#!/usr/bin/env python3
# Copyright (c) Meta Platforms, Inc. and affiliates.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

# pyre-strict

from dataclasses import dataclass
from enum import Enum
from typing import List

from dataclasses_json import DataClassJsonMixin
from onedocker.entity.opawdl_state_instance import OPAWDLStateInstance
from onedocker.entity.opawdl_workflow import OPAWDLWorkflow


class Status(Enum):
    CREATED = "CREATED"
    STARTED = "STARTED"
    FAILED = "FAILED"
    COMPLETED = "COMPLETED"


@dataclass
class OPAWDLWorkflowInstance(DataClassJsonMixin):
    instance_id: str
    opawdl_workflow: OPAWDLWorkflow
    state_instances: List[OPAWDLStateInstance]
    status: Status = Status.CREATED

    def get_instance_id(self) -> str:
        return self.instance_id

    def __str__(self) -> str:
        return self.to_json()
