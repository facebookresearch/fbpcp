#!/usr/bin/env python3
# Copyright (c) Facebook, Inc. and its affiliates.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

# pyre-strict
from typing import List

from fbpcs.service.storage import StorageService


class OneDockerPackageRepository:
    def __init__(self, storage_svc: StorageService, repository_path: str) -> None:
        self.storage_svc = storage_svc
        self.repository_path = repository_path

    def upload(self, package_name: str, version: str, source: str) -> None:
        pass

    def download(self, package_name: str, version: str, destination: str) -> None:
        pass

    def get_versions(
        self,
        package_name: str,
    ) -> List[str]:
        return []

    def get_package_info(self, package_name: str, version: str) -> str:
        return ""
