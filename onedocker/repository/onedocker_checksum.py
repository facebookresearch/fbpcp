#!/usr/bin/env python3
# Copyright (c) Meta Platforms, Inc. and affiliates.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

# pyre-strict

from fbpcp.service.storage import StorageService


class OneDockerChecksumRepository:
    def __init__(
        self, storage_svc: StorageService, checksum_repository_path: str
    ) -> None:
        self.storage_svc = storage_svc
        self.checksum_repository_path = checksum_repository_path

    def _build_checksum_path(self, package_name: str, version: str) -> str:
        if not self.checksum_repository_path:
            raise ValueError(
                "Checksum Repository Path not set. Unable to attest Package"
            )
        return f"{self.checksum_repository_path}{package_name}/{version}/{package_name.split('/')[-1]}.json"

    def _file_exists(self, package_name: str, version: str) -> bool:
        package_path = self._build_checksum_path(
            package_name=package_name, version=version
        )
        return self.storage_svc.file_exists(package_path)

    def write(self, package_name: str, version: str, checksum_data: str) -> None:
        package_path = self._build_checksum_path(
            package_name=package_name, version=version
        )
        self.storage_svc.write(filename=package_path, data=checksum_data)

    def read(self, package_name: str, version: str) -> str:
        package_path = self._build_checksum_path(
            package_name=package_name, version=version
        )

        if not self._file_exists(package_name, version):
            raise FileNotFoundError(
                f"Cant find checksum file for package {package_name}, version {version}"
            )

        return self.storage_svc.read(filename=package_path)

    def archive_file(self, package_name: str, version: str) -> None:
        raise NotImplementedError
