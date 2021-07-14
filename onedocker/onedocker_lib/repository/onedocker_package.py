#!/usr/bin/env python3
# Copyright (c) Facebook, Inc. and its affiliates.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

# pyre-strict
from typing import List

from fbpcs.service.storage import StorageService
from fbpcs.service.storage_s3 import S3StorageService
from fbpcs.util.typing import checked_cast
from onedocker.onedocker_lib.entity.package_info import PackageInfo


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
        pass

    def get_versions(
        self,
        package_name: str,
    ) -> List[str]:
        return []

    def get_package_info(self, package_name: str, version: str) -> PackageInfo:
        # TODO: refactor storage service so we don't have to cast it
        s3_storage_svc = checked_cast(S3StorageService, self.storage_svc)
        package_path = self._build_package_path(package_name, version)

        if not s3_storage_svc.file_exists(package_path):
            raise ValueError(
                f"Package {package_name}, version {version} not found in repository"
            )

        package_info_dict = s3_storage_svc.ls_file(package_path)
        return PackageInfo(
            package_name=package_name,
            version=version,
            last_modified=package_info_dict.get("LastModified").ctime(),
            package_type=package_info_dict.get("ContentType"),
            package_size=package_info_dict.get("ContentLength"),
        )
