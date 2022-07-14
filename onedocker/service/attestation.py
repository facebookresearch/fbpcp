#!/usr/bin/env python3
# Copyright (c) Meta Platforms, Inc. and affiliates.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

# pyre-strict

import json
import logging
from typing import Dict, List, Optional

from fbpcp.service.storage import StorageService
from onedocker.entity.attestation_error import AttestationError
from onedocker.entity.checksum_info import ChecksumInfo
from onedocker.entity.checksum_type import ChecksumType
from onedocker.service.checksum import LocalChecksumGenerator


class AttestationService:
    # Default checksum types
    DEFAULT_CHECKSUM_TYPES: List[ChecksumType] = [
        ChecksumType.MD5,
        ChecksumType.SHA256,
        ChecksumType.BLAKE2B,
    ]

    def __init__(
        self,
        storage_svc: Optional[StorageService] = None,
        repository_path: str = "",
    ) -> None:
        self.logger: logging.Logger = logging.getLogger(__name__)
        self.checksum_generator = LocalChecksumGenerator()
        if storage_svc is not None:
            self.storage_svc: StorageService = storage_svc
        self.repository_path: str = repository_path

    def _build_attestation_repository_path(
        self,
        package_name: str,
        version: str,
    ) -> str:
        return f"{self.repository_path}{package_name}/{version}.json"

    def _get_checksum_info(
        self,
        package_name: str,
        version: str,
        binary_path: str,
        checksum_types: List[ChecksumType] = DEFAULT_CHECKSUM_TYPES,
    ) -> ChecksumInfo:
        checksums: Dict[str, str] = self.checksum_generator.generate_checksums(
            binary_path=binary_path,
            checksum_algorithms=checksum_types,
        )

        return ChecksumInfo(
            package_name=package_name,
            version=version,
            checksums=checksums,
        )

    def track_binary(
        self,
        binary_path: str,
        package_name: str,
        version: str,
    ) -> str:
        """
        This Function generates then uploads checksums for passed in local binary

        Args:
            binary_path:        Local file path pointing to the package
            package_name:       Package Name to use when uploading file to checksum repository
            version:    Package Version to relay while uploading file to checksum repository

        Returns:
            formated_checksum_info:  A JSON formated file that contains all the checksum data for a file
        """
        # Generates checksums
        self.logger.info(f"Generating checksums for binary at {binary_path}")
        checksum_info = self._get_checksum_info(
            package_name=package_name,
            version=version,
            binary_path=binary_path,
        )

        return json.dumps(checksum_info.asdict(), indent=4)

    def attest_binary(
        self,
        binary_path: str,
        package_name: str,
        version: str,
        checksum_algorithm: ChecksumType,
    ) -> None:
        """
        This functions generates a checksum for a local file and then compares the generated value to what is stored in the checksum repository for the given package_name and version

        Args:
            binary_path:            Local file path pointing to the package
            package_name:           Package Name to use when downlading the checksum file from checksum repository
            version:        Package Version to relay while downloading the checksum file from checksum repository
            checksum_algorithm:     Checksum algorithm that should be used while attesting local binary
        """
        # Build file path
        file_path = self._build_attestation_repository_path(package_name, version)

        if not self.storage_svc.file_exists(file_path):
            self.logger.info(
                f"Untracked package {package_name}: {version}. Skipping Attestion."
            )
            return None
        # Retrieve file info and parse contents
        file_contents = self.storage_svc.read(file_path)
        package_info = json.loads(file_contents)
        package_checksum_info = ChecksumInfo(**package_info)

        # Generates checksums
        self.logger.info(f"Generating checksums for binary at {binary_path}")
        checksum_info = self._get_checksum_info(
            package_name=package_name,
            version=version,
            binary_path=binary_path,
            checksum_types=[checksum_algorithm],
        )

        if checksum_info != package_checksum_info:
            raise AttestationError(
                "Downloaded binaries checksum information differs from uploaded package's checksum information"
            )
        self.logger.info("Binary successfully attested")
