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
from onedocker.onedocker_lib.entity.owdl_state_instance import OWDLStateInstance
from onedocker.onedocker_lib.entity.owdl_workflow import OWDLWorkflow


class Status(Enum):
    CREATED = "CREATED"
    STARTED = "STARTED"
    FAILED = "FAILED"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"


@dataclass
class OWDLWorkflowInstance(DataClassJsonMixin):
    owdl_workflow: OWDLWorkflow
    state_instances: List[OWDLStateInstance]
    status: Status = Status.CREATED

    def get_current_state_instance(self) -> OWDLStateInstance:
        return self.state_instances[-1]

    def add_next_state_instance(self, state_inst: OWDLStateInstance) -> None:
        self.state_instances.append(state_inst)

    def __str__(self) -> str:
        return self.to_json()
