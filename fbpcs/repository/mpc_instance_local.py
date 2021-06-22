#!/usr/bin/env python3
# Copyright (c) Facebook, Inc. and its affiliates.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

# pyre-strict

from fbpcs.entity.mpc_instance import MPCInstance
from fbpcs.repository.instance_local import LocalInstanceRepository
from fbpcs.repository.mpc_instance import MPCInstanceRepository


class LocalMPCInstanceRepository(MPCInstanceRepository):
    def __init__(self, base_dir: str) -> None:
        self.repo = LocalInstanceRepository(base_dir)

    def create(self, instance: MPCInstance) -> None:
        self.repo.create(instance)

    def read(self, instance_id: str) -> MPCInstance:
        return MPCInstance.loads_schema(self.repo.read(instance_id))

    def update(self, instance: MPCInstance) -> None:
        self.repo.update(instance)

    def delete(self, instance_id: str) -> None:
        self.repo.delete(instance_id)
