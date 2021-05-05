#!/usr/bin/env python3
# Copyright (c) Facebook, Inc. and its affiliates.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

# pyre-strict

import pickle

from fbpcs.entity.instance_base import InstanceBase
from fbpcs.service.storage_s3 import S3StorageService


class S3InstanceRepository:
    def __init__(self, s3_storage_svc: S3StorageService, base_dir: str) -> None:
        self.s3_storage_svc = s3_storage_svc
        self.base_dir = base_dir

    def create(self, instance: InstanceBase) -> None:
        if self._exist(instance.get_instance_id()):
            raise RuntimeError(f"{instance.get_instance_id()} already exists")

        filename = f"{self.base_dir}{instance.get_instance_id()}"
        # Use pickle protocol 0 to make ASCII only bytes that can be safely decoded into a string
        self.s3_storage_svc.write(filename, pickle.dumps(instance, 0).decode())

    def read(self, instance_id: str) -> InstanceBase:
        if not self._exist(instance_id):
            raise RuntimeError(f"{instance_id} does not exist")

        filename = f"{self.base_dir}{instance_id}"
        instance = pickle.loads(self.s3_storage_svc.read(filename).encode())
        return instance

    def update(self, instance: InstanceBase) -> None:
        if not self._exist(instance.get_instance_id()):
            raise RuntimeError(f"{instance.get_instance_id()} does not exist")

        filename = f"{self.base_dir}{instance.get_instance_id()}"
        # Use pickle protocol 0 to make ASCII only bytes that can be safely decoded into a string
        self.s3_storage_svc.write(filename, pickle.dumps(instance, 0).decode())

    def delete(self, instance_id: str) -> None:
        if not self._exist(instance_id):
            raise RuntimeError(f"{instance_id} does not exist")

        filename = f"{self.base_dir}{instance_id}"
        self.s3_storage_svc.delete(filename)

    def _exist(self, instance_id: str) -> bool:
        return self.s3_storage_svc.file_exists(f"{self.base_dir}{instance_id}")
