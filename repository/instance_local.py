#!/usr/bin/env python3
# pyre-strict

import pickle
from pathlib import Path

from entity.instance_base import InstanceBase


class LocalInstanceRepository:
    def __init__(self, base_dir: str) -> None:
        self.base_dir = Path(base_dir)

    def create(self, instance: InstanceBase) -> None:
        if self._exist(instance.get_instance_id()):
            raise RuntimeError(f"{instance.get_instance_id()} already exists")

        path = self.base_dir.joinpath(instance.get_instance_id())
        with open(path, "wb") as f:
            pickle.dump(instance, f)

    def read(self, instance_id: str) -> InstanceBase:
        if not self._exist(instance_id):
            raise RuntimeError(f"{instance_id} does not exist")

        path = self.base_dir.joinpath(instance_id)
        with open(path, "rb") as f:
            instance = pickle.load(f)
        return instance

    def update(self, instance: InstanceBase) -> None:
        if not self._exist(instance.get_instance_id()):
            raise RuntimeError(f"{instance.get_instance_id()} does not exist")

        path = self.base_dir.joinpath(instance.get_instance_id())
        with open(path, "wb") as f:
            pickle.dump(instance, f)

    def delete(self, instance_id: str) -> None:
        if not self._exist(instance_id):
            raise RuntimeError(f"{instance_id} does not exist")

        self.base_dir.joinpath(instance_id).unlink()

    def _exist(self, instance_id: str) -> bool:
        return self.base_dir.joinpath(instance_id).exists()
