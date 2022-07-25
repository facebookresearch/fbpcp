# Copyright (c) Meta Platforms, Inc. and affiliates.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from typing import Optional

from fbpcp.service.storage import StorageService
from onedocker.repository.onedocker_checksum import OneDockerChecksumRepository
from onedocker.repository.onedocker_package import OneDockerPackageRepository


class OnedockerRepositoryService:
    def __init__(
        self,
        storage_svc: StorageService,
        package_repository_path: str,
        checksum_repository_path: str,
    ) -> None:
        self.storage_svc = storage_svc
        self.package_repo = OneDockerPackageRepository(
            storage_svc, package_repository_path
        )
        self.checksum_repo = OneDockerChecksumRepository(
            storage_svc, checksum_repository_path
        )

    def upload(
        self,
        package_name: str,
        version: str,
        source: str,
        metadata: Optional[dict] = None,
    ) -> None:
        raise NotImplementedError

    def download(self, package_name: str, version: str, destination: str) -> None:
        raise NotImplementedError

    def promote(self, package_name: str, old_version: str, new_version: str) -> None:
        raise NotImplementedError
