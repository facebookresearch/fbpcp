#!/usr/bin/env python3
# Copyright (c) Meta Platforms, Inc. and affiliates.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from typing import Optional

from fbpcp.service.storage import StorageService
from onedocker.entity.object_metadata import PackageMetadata
from onedocker.repository.onedocker_package import OneDockerPackageRepository


class OneDockerRepositoryService:
    def __init__(
        self,
        storage_svc: StorageService,
        package_repository_path: str,
    ) -> None:
        self.storage_svc = storage_svc
        self.package_repo = OneDockerPackageRepository(
            storage_svc, package_repository_path
        )

    def upload(
        self,
        package_name: str,
        version: str,
        source: str,
        metadata: Optional[dict] = None,
    ) -> None:
        self.package_repo.upload(package_name, version, source)

    def download(self, package_name: str, version: str, destination: str) -> None:
        self.package_repo.download(package_name, version, destination)

    def _set_metadata(
        self,
        package_name: str,
        version: str,
        metadata: PackageMetadata,
    ) -> None:
        # TODO: T127441856 handle storing metadata
        raise NotImplementedError

    def _get_metadata(
        self,
        package_name: str,
        version: str,
    ) -> PackageMetadata:
        raise NotImplementedError

    def archive_package(self, package_name: str, version: str) -> None:
        # TODO: Archive or delete checksum file associated with the archived package if exists.
        self.package_repo.archive_package(package_name, version)
