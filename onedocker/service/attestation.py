#!/usr/bin/env python3
# Copyright (c) Meta Platforms, Inc. and affiliates.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

import json
from typing import Dict, List, Union

from fbpcp.service.storage import StorageService
from onedocker.entity.checksum_type import ChecksumType
from onedocker.service.checksum import LocalChecksumGenerator

# Default checksum types
DEFAULT_CHECKSUM_TYPES = [ChecksumType.MD5, ChecksumType.SHA256, ChecksumType.BLAKE2B]


class AttestationService:
    def __init__(self, storage_svc: StorageService, repository_path: str) -> None:
        self.checksum_generator = LocalChecksumGenerator()
        self.storage_svc = storage_svc
        self.repository_path = repository_path

    def _format_package_info(
        self,
        package_name: str,
        version: str,
        checksums: Dict[str, str],
    ) -> Dict[str, Union[str, Dict[str, str]]]:
        package_info = {}
        package_info["Package Name"] = package_name
        package_info["Package Version"] = version
        package_info["Checksums"] = checksums
        return package_info

    def _upload_checksum(
        self,
        path_to_binary: str,
        package_name: str,
        version: str,
        checksums: Dict[str, str],
    ) -> None:

        file_path = f"{self.repository_path}{package_name}/{version}.json"
        package_info = self._format_package_info(package_name, version, checksums)
        file_contents = json.dumps(package_info, indent=4)

        self.storage_svc.write(file_path, file_contents)

    def track_package(
        self,
        path_to_binary: str,
        package_name: str,
        version: str,
        checksum_algorithms: Union[List[ChecksumType], None] = None,
    ) -> None:
        checksum_types = (
            checksum_algorithms
            if checksum_algorithms is not None
            else DEFAULT_CHECKSUM_TYPES
        )

        checksums: Dict[str, str] = self.checksum_generator.generate_checksums(
            path_to_binary=path_to_binary,
            checksum_algorithms=checksum_types,
        )
        self._upload_checksum(
            path_to_binary=path_to_binary,
            package_name=package_name,
            version=version,
            checksums=checksums,
        )
