#!/usr/bin/env python3
# Copyright (c) Meta Platforms, Inc. and affiliates.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

# pyre-strict
from typing import List, Optional

from fbpcp.service.storage import StorageService
from onedocker.entity.package_info import PackageInfo


class OneDockerPackageRepository:
    def __init__(self, storage_svc: StorageService, repository_path: str) -> None:
        self.storage_svc = storage_svc
        self.repository_path = repository_path

    def _build_package_path(self, package_name: str, version: str) -> str:
        return f"{self.repository_path}{package_name}/{version}/{package_name.split('/')[-1]}"

    def upload(self, package_name: str, version: str, source: str) -> None:
        package_path = self._build_package_path(package_name, version)
        self.storage_svc.copy(source, package_path)

    def download(self, package_name: str, version: str, destination: str) -> None:
        package_path = self._build_package_path(package_name, version)
        self.storage_svc.copy(package_path, destination)

    def get_package_versions(
        self,
        package_name: str,
    ) -> List[str]:
        package_parent_path = f"{self.repository_path}{package_name}/"
        return self.storage_svc.list_folders(package_parent_path)

    def _read_contents(
        self,
        package_name: str,
        version: str,
        file_name: Optional[str] = None,
    ) -> str:

        if file_name is None:
            file_path = self._build_package_path(package_name, version)
        else:
            file_path = f"{self.repository_path}{package_name}/{version}/{file_name}"

        return self.storage_svc.read(file_path)

    def get_package_info(self, package_name: str, version: str) -> PackageInfo:
        package_path = self._build_package_path(package_name, version)

        if not self.storage_svc.file_exists(package_path):
            raise ValueError(
                f"Package {package_name}, version {version} not found in repository"
            )

        file_info = self.storage_svc.get_file_info(package_path)
        return PackageInfo(
            package_name=package_name,
            version=version,
            last_modified=file_info.last_modified,
            package_size=file_info.file_size,
        )
