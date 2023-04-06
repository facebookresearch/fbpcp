#!/usr/bin/env python3
# Copyright (c) Meta Platforms, Inc. and affiliates.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

# pyre-strict

from pathlib import Path

from onedocker.entity.opawdl_workflow_instance import OPAWDLWorkflowInstance
from onedocker.repository.opawdl_workflow_instance_repository import (
    OPAWDLWorkflowInstanceRepository,
)


class LocalOPAWDLWorkflowInstanceRepository(OPAWDLWorkflowInstanceRepository):
    def __init__(self, base_dir: str) -> None:
        self.base_dir = Path(base_dir)

    def exist(self, instance_id: str) -> bool:
        return self.base_dir.joinpath(instance_id).exists()

    def create(self, instance: OPAWDLWorkflowInstance) -> None:
        if self.exist(instance.get_instance_id()):
            raise Exception(
                f"Fail to create the workflow instance: {instance.get_instance_id()} already exists."
            )

        path = self.base_dir.joinpath(instance.get_instance_id())
        with open(path, "w") as f:
            f.write(str(instance))

    def get(self, instance_id: str) -> OPAWDLWorkflowInstance:
        if not self.exist(instance_id):
            raise Exception(f"{instance_id} does NOT exist")

        path = self.base_dir.joinpath(instance_id)
        with open(path, "r") as f:
            return OPAWDLWorkflowInstance.from_json((f.read().strip()))

    def update(self, instance: OPAWDLWorkflowInstance) -> None:
        if not self.exist(instance.get_instance_id()):
            raise Exception(f"{instance.get_instance_id()} does not exist")

        path = self.base_dir.joinpath(instance.get_instance_id())
        with open(path, "w") as f:
            f.write(str(instance))

    def delete(self, instance_id: str) -> None:
        if not self.exist(instance_id):
            raise Exception(f"{instance_id} does not exist")

        self.base_dir.joinpath(instance_id).unlink()
