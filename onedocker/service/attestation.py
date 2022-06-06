#!/usr/bin/env python3
# Copyright (c) Meta Platforms, Inc. and affiliates.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

# pyre-strict

import json
import logging
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

# Package Info Dict Tags
PACKAGE_NAME = "Package Name"
PACKAGE_VERSION = "Package Version"
PACKAGE_CHECKSUMS = "Checksums"


class AttestationService:
    def __init__(self, storage_svc: StorageService, repository_path: str) -> None:
        self.logger: logging.Logger = logging.getLogger(__name__)
        self.checksum_generator = LocalChecksumGenerator()
        self.storage_svc = storage_svc
        self.repository_path = repository_path

    def _build_attestation_repository_path(
        self,
        package_name: str,
        version: str,
    ) -> str:
        return f"{self.repository_path}{package_name}/{version}.json"

    def _format_package_info(
        self,
        package_name: str,
        version: str,
        checksums: Dict[str, str],
    ) -> Dict[str, Union[str, Dict[str, str]]]:
        package_info = {}
        package_info[PACKAGE_NAME] = package_name
        package_info[PACKAGE_VERSION] = version
        package_info[PACKAGE_CHECKSUMS] = checksums
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
        file_path = self._build_attestation_repository_path(package_name, version)
        file_contents = json.dumps(package_info, indent=4)

        # upload contents to set repo path
        self.storage_svc.write(file_path, file_contents)

    def track_binary(
        self,
        binary_path: str,
        package_name: str,
        version: str,
    ) -> None:
        """
        This Function generates then uploads checksums for passed in local binary

        Args:
            binary_path:    Local file path pointing to the package
            package_name:   Package Name to use when uploading file to checksum repository
            version:        Package Version to relay while uploading file to checksum repository
        """
        # Generates checksums
        self.logger.info(f"Generating checksums for binary at {binary_path}")
        checksums: Dict[str, str] = self.checksum_generator.generate_checksums(
            binary_path=binary_path,
            checksum_algorithms=DEFAULT_CHECKSUM_TYPES,
        )

        # Upload checksums and package info to set repo path
        self.logger.info(f"Uploading checksums for package {package_name}: {version}")
        self._upload_checksum(
            package_name=package_name,
            version=version,
            checksums=checksums,
        )

    def verify_binary(
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
            version:                Package Version to relay while downloading the checksum file from checksum repository
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

        # Verify that file contents are for desired package
        self.logger.info("Attesting correct package information was retrived")
        if package_info[PACKAGE_NAME] != package_name:
            raise ValueError(
                f"Package Name {package_info[PACKAGE_NAME]} in file is different than passed in Name {package_name}"
            )
        if package_info[PACKAGE_VERSION] != version:
            raise ValueError(
                f"Package Version {package_info[PACKAGE_VERSION]} in file is different than passed in Version {version}"
            )

        # Process downloaded file and generate a local checksum
        checksums: Dict[str, str] = self.checksum_generator.generate_checksums(
            binary_path=binary_path,
            checksum_algorithms=[checksum_algorithm],
        )
        package_checksums = package_info[PACKAGE_CHECKSUMS]

        # Verify Checksum Details
        self.logger.info("Attesting binary integrity")
        if checksum_algorithm.name not in package_checksums:
            raise ValueError(
                f"Package Checksum Algorithms {package_checksums.keys()} does not contain passed in Checksum Algorithm {checksum_algorithm.name}"
            )
        if (
            checksums[checksum_algorithm.name]
            != package_checksums[checksum_algorithm.name]
        ):
            raise ValueError(
                f"Package Checksum {package_checksums[checksum_algorithm.name]} for Checksum Algorithm {checksum_algorithm.name} does not match actual binary Checksum {checksums[checksum_algorithm.name]}"
            )
        self.logger.info("Binary successfully attested")
