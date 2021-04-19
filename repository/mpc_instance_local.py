#!/usr/bin/env python3
# pyre-strict

from typing import cast

from entity.mpc_instance import MPCInstance
from repository.instance_local import LocalInstanceRepository
from repository.mpc_instance import MPCInstanceRepository


class LocalMPCInstanceRepository(MPCInstanceRepository):
    def __init__(self, base_dir: str) -> None:
        self.repo = LocalInstanceRepository(base_dir)

    def create(self, instance: MPCInstance) -> None:
        self.repo.create(instance)

    def read(self, instance_id: str) -> MPCInstance:
        return cast(MPCInstance, self.repo.read(instance_id))

    def update(self, instance: MPCInstance) -> None:
        self.repo.update(instance)

    def delete(self, instance_id: str) -> None:
        self.repo.delete(instance_id)
