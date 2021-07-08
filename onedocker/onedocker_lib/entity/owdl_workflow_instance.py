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
from fbpcs.entity.instance_base import InstanceBase
from onedocker.onedocker_lib.entity.owdl_state_instance import OWDLStateInstance
from onedocker.onedocker_lib.entity.owdl_workflow import OWDLWorkflow


class Status(Enum):
    CREATED = "CREATED"
    STARTED = "STARTED"
    FAILED = "FAILED"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"


@dataclass
class OWDLWorkflowInstance(InstanceBase):
    instance_id: str
    owdl_workflow: OWDLWorkflow
    state_instances: List[OWDLStateInstance]
    status: Status = Status.CREATED

    def get_instance_id(self) -> str:
        return self.instance_id
