#!/usr/bin/env python3
# Copyright (c) Meta Platforms, Inc. and affiliates.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from typing import Dict, List, Optional

from fbpcp.error.pcp import PcpError
from fbpcp.service.storage import StorageService
from onedocker.entity.measurement import MeasurementType
from onedocker.entity.metadata import PackageMetadata

from onedocker.repository.onedocker_package import OneDockerPackageRepository
from onedocker.service.metadata import MetadataService

DEFAULT_PROD_VERSION: str = "latest"
MEASUREMENT_TYPES: List[MeasurementType] = [MeasurementType.sha256]


class OneDockerRepositoryService:
    def __init__(
        self,
        storage_svc: StorageService,
        package_repository_path: str,
        metadata_svc: Optional[MetadataService] = None,
    ) -> None:
        self.package_repo = OneDockerPackageRepository(
            storage_svc, package_repository_path
        )
        self.metadata_svc = metadata_svc

    def upload(
        self,
        package_name: str,
        version: str,
        source: str,
    ) -> None:
        if not self._skip_version_validation_check(version):
            all_versions = self.package_repo.get_package_versions(package_name)
            if version in all_versions:
                raise ValueError(
                    f"Version {version} already exists. Please specify another version."
                )
        self.package_repo.upload(package_name, version, source)

        if self.metadata_svc:
            self.metadata_svc.put_metadata(
                metadata=self._generate_metadata(
                    package_name=package_name, version=version, source=source
                )
            )

    def download(self, package_name: str, version: str, destination: str) -> None:
        self.package_repo.download(package_name, version, destination)

    def _generate_measurements(self, source: str) -> Dict[MeasurementType, str]:
        # TODO: replace this logic with acutal call to measurement service T138464450
        mock_measurements = {t: t.value + "hash" for t in MEASUREMENT_TYPES}
        return mock_measurements

    def _generate_metadata(
        self,
        package_name: str,
        version: str,
        source: str,
    ) -> PackageMetadata:
        measurements = self._generate_measurements(source)
        return PackageMetadata(
            package_name=package_name, version=version, measurements=measurements
        )

    def archive_package(self, package_name: str, version: str) -> None:
        # TODO: Archive or delete checksum file associated with the archived package if exists.
        self.package_repo.archive_package(package_name, version)

    def _skip_version_validation_check(self, version: str) -> bool:
        # TODO: T129388192 remove this check when latest is no longer in use.
        if version == DEFAULT_PROD_VERSION:
            return True
        return False

    def get_package_measurements(
        self, package_name: str, version: str
    ) -> Dict[str, str]:
        if not self.metadata_svc:
            raise PcpError(
                "No MetadataService has been provided for OneDockerRepositoryService, which is required for get_package_measurements function"
            )

        md = self.metadata_svc.get_medadata(package_name=package_name, version=version)

        return {k.value: v for k, v in md.measurements.items()}
