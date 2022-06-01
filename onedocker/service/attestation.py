#!/usr/bin/env python3
# Copyright (c) Meta Platforms, Inc. and affiliates.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

# pyre-strict

import json
from typing import Dict, List, Union

from fbpcp.service.storage import StorageService
from onedocker.entity.checksum_type import ChecksumType
from onedocker.service.checksum import LocalChecksumGenerator

# Default checksum types
DEFAULT_CHECKSUM_TYPES: List[ChecksumType] = [
    ChecksumType.MD5,
    ChecksumType.SHA256,
    ChecksumType.BLAKE2B,
]


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

        # General Package Info
        package_info["Package Name"] = package_name
        package_info["Package Version"] = version

        # Checksum that were requested
        package_info["Checksums"] = checksums
        return package_info

    def _upload_checksum(
        self,
        package_name: str,
        version: str,
        checksums: Dict[str, str],
    ) -> None:
        # Put together package into a json format
        package_info = self._format_package_info(package_name, version, checksums)

        # Construct file information - (name and contents)
        file_path = f"{self.repository_path}{package_name}/{version}.json"
        file_contents = json.dumps(package_info, indent=4)

        # upload contents to set repo path
        self.storage_svc.write(file_path, file_contents)

    def track_binary(
        self,
        binary_path: str,
        package_name: str,
        version: str,
    ) -> None:
        # Generates checksums
        checksums: Dict[str, str] = self.checksum_generator.generate_checksums(
            path_to_binary=binary_path,
            checksum_algorithms=DEFAULT_CHECKSUM_TYPES,
        )

        # Upload checksums and package info to set repo path
        self._upload_checksum(
            package_name=package_name,
            version=version,
            checksums=checksums,
        )
