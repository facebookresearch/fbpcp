#!/usr/bin/env python3
# Copyright (c) Meta Platforms, Inc. and affiliates.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from datetime import datetime
from typing import Optional

from fbpcp.service.storage import StorageService
from onedocker.repository.onedocker_checksum import OneDockerChecksumRepository
from onedocker.repository.onedocker_package import OneDockerPackageRepository


class OneDockerRepositoryService:
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
        # TODO: T127441856 handle storing metadata
        self.package_repo.upload(package_name, version, source)

    def download(self, package_name: str, version: str, destination: str) -> None:
        raise NotImplementedError

    def promote(self, package_name: str, old_version: str, new_version: str) -> None:
        # Build the target path to promote the package to.
        target_path = self.package_repo.build_package_path(package_name, new_version)
        if new_version == "latest":
            # Archive the existing files in the target path.
            last_modified_date = self.package_repo.get_package_info(
                package_name, new_version
            ).last_modified
            formatted_date = datetime.strftime(
                datetime.strptime(last_modified_date, "%a %b %d %H:%M:%S %Y"),
                "%Y-%m-%d",
            )

            archive_path = self.package_repo.build_package_path(
                package_name, formatted_date
            )
            self.storage_svc.copy(target_path, archive_path)
        current_path = self.package_repo.build_package_path(package_name, old_version)
        self.storage_svc.copy(current_path, target_path)
