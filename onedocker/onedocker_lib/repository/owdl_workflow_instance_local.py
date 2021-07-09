#!/usr/bin/env python3
# Copyright (c) Facebook, Inc. and its affiliates.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

# pyre-strict

from fbpcs.repository.instance_local import LocalInstanceRepository
from onedocker.onedocker_lib.entity.owdl_workflow_instance import OWDLWorkflowInstance
from onedocker.onedocker_lib.repository.owdl_workflow_instance import (
    OWDLWorkflowInstanceRepository,
)


class LocalOWDLWorkflowInstanceRepository(OWDLWorkflowInstanceRepository):
    def __init__(self, base_dir: str) -> None:
        self.repo = LocalInstanceRepository(base_dir)

    def create(self, instance: OWDLWorkflowInstance) -> None:
        self.repo.create(instance)

    def read(self, instance_id: str) -> OWDLWorkflowInstance:
        return OWDLWorkflowInstance.loads_schema(self.repo.read(instance_id))

    def update(self, instance: OWDLWorkflowInstance) -> None:
        self.repo.update(instance)

    def delete(self, instance_id: str) -> None:
        self.repo.delete(instance_id)
